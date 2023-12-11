import json
import os
import time
from io import StringIO

import pandas as pd

from model.infrastructure import Infrastructure, Maintenance, Node
from model.job import Job, Joblet
from view.curses_multiwindow import Singleton

joblet_node_cache = {}
joblet_array_cache = {}


def _ungroup_slurm_names(x):
    if '[' in x:
        tokens = x.split('[')[1].split(']')[0].split(',')
        return ','.join([x.split('[')[0].split(',')[-1] + tok + x.split(']')[1].split(',')[0] for tok in tokens] +
                        [a for a in x.split(',') if '[' not in a and ']' not in a])
    else:
        return x


def _split_column(df, column):
    # flatten representation
    node_flat = pd.DataFrame([[i, x]
                              for i, y in df[column].fillna('').apply(_ungroup_slurm_names).str.split(',').items()
                              for x in y], columns=['__I', column]).set_index('__I')
    node_flat[column] = node_flat[column].replace('', float('nan'))
    return node_flat.merge(df[[x for x in df.columns if x != column]], left_index=True, right_index=True).reset_index(drop=True)


def _node_from_sinfo(x):
    n = Node(_node_preproc(x['NODELIST']), x.n_gpu, x.m_gpu, x.reserved, None, x.CPUS, x.MEMORY)
    if x['STATE'] == 'drng' or 'drain' in x['STATE']:
        n.status = 'drain'
    elif x['STATE'].upper() in ('MAINT', 'DOWN', 'DOWN*', 'FAIL', 'FAILING', 'FAIL*'):
        n.status = 'down'
    else:
        n.status = 'ok'
    return n


def _read_nodes(reservations, pending_res):
    sinfo_df = pd.read_csv(StringIO(os.popen(r'sinfo -N -o "%N;%G;%t;%m;%c"').read()), sep=';')
    sinfo_df = _split_column(sinfo_df, 'NODELIST').drop_duplicates()
    sinfo_df['n_gpu'] = sinfo_df['GRES'].apply(lambda x: 0 if x.split('(')[0].split(':')[0] in ('(null)', '') else int(x.split('(')[0].split(':')[-1]))
    sinfo_df['m_gpu'] = sinfo_df['GRES'].str.split(':').apply(lambda x: 'n/a' if x[0] in ('(null)', '') else x[1])
    sinfo_df['reserved'] = 'no'
    if reservations is not None:
        sinfo_df.loc[sinfo_df['NODELIST'].isin(reservations.Nodes.unique()), 'reserved'] = 'yes'
    if pending_res is not None:
        sinfo_df.loc[sinfo_df['NODELIST'].isin(pending_res.Nodes.unique()), 'reserved'] = 'pending'

    return sinfo_df.apply(_node_from_sinfo, axis=1).tolist()


def _maint_from_reservations(x):
    mts = []
    for st in x.StartTime.unique():
        dt = x[x.StartTime == st]
        mts.append(Maintenance(dt.Nodes.unique().tolist(), st, dt.EndTime.iloc[0]))
    return mts


def _read_maintenances():
    # create dataframe
    reservations = os.popen(r'scontrol show reservation 2>/dev/null').read().split('\n\n')
    reservations = [{c.split('=')[0]: c.split('=')[1] for c in r.split()} for r in reservations if len(r) and '=' in r]
    if not len(reservations):
        return [], None, None
    reservations = pd.DataFrame.from_records(reservations)
    reservations['StartTime'] = str(pd.to_datetime(reservations['StartTime']))
    reservations['EndTime'] = str(pd.to_datetime(reservations['EndTime']))
    reservations = _split_column(reservations, 'Nodes')
    maint_flag = reservations['Flags'].str.contains('MAINT') & \
        reservations['Flags'].str.contains('SPEC_NODES') & \
        reservations['Flags'].str.contains('ALL_NODES')
    # | reservations['ReservationName'].str.contains('limit_temp')

    maintenances = _maint_from_reservations(reservations[maint_flag])
    return maintenances, reservations[(~maint_flag) & (reservations['State'] == 'ACTIVE')], reservations[(~maint_flag) & (reservations['State'] == 'INACTIVE')]


def _read_limits():
    """
    Read the maximum amount of GPUs allowed
    :returns max_prod_per_user, max_prod_group, max_studentsprod_per_user, max_studentsprod_group
    """
    lims = pd.read_fwf(StringIO(os.popen(r'sacctmgr show qos format=\'name%15,maxtresperuser%35,grptres%25,maxjobsperuser\' 2>/dev/null').read())).loc[1:]
    lims['puG'] = lims['MaxTRESPU'].apply(lambda x: int(x.split('gres/gpu=')[1].split(',')[0]) if isinstance(x, str) and 'gres/gpu' in x else float('nan'))
    lims['grpG'] = lims['GrpTRES'].apply(lambda x: int(x.split('gres/gpu=')[1].split(',')[0]) if isinstance(x, str) and 'gres/gpu' in x else float('nan'))
    lims['puM'] = lims['MaxTRESPU'].apply(lambda x: parse_mem(x.split('mem=')[1].split(',')[0]) if isinstance(x, str) and 'mem=' in x else float('nan'))
    lims['grpM'] = lims['GrpTRES'].apply(lambda x: parse_mem(x.split('mem=')[1].split(',')[0]) if isinstance(x, str) and 'mem=' in x else float('nan'))
    lims['puC'] = lims['MaxTRESPU'].apply(lambda x: int(x.split('cpu=')[1].split(',')[0]) if isinstance(x, str) and 'cpu=' in x else float('nan'))
    lims['grpC'] = lims['GrpTRES'].apply(lambda x: int(x.split('cpu=')[1].split(',')[0]) if isinstance(x, str) and 'cpu=' in x else float('nan'))
    return (lims.loc[lims['Name'] == 'all_usr_prod', 'puG'].iloc[0],
            lims.loc[lims['Name'] == 'all_usr_prod', 'grpG'].iloc[0],
            lims.loc[lims['Name'] == 'all_usr_prod', 'puG'].iloc[0],  # students
            lims.loc[lims['Name'] == 'all_usr_prod', 'grpG'].iloc[0],  # students
            lims.loc[lims['Name'] == 'all_usr_prod', 'puM'].iloc[0],
            lims.loc[lims['Name'] == 'all_usr_prod', 'grpM'].iloc[0],
            lims.loc[lims['Name'] == 'all_usr_prod', 'puM'].iloc[0],  # students
            lims.loc[lims['Name'] == 'all_usr_prod', 'grpM'].iloc[0],  # students
            lims.loc[lims['Name'] == 'all_usr_prod', 'puC'].iloc[0],
            lims.loc[lims['Name'] == 'all_usr_prod', 'grpC'].iloc[0],
            lims.loc[lims['Name'] == 'all_usr_prod', 'puC'].iloc[0],  # students
            lims.loc[lims['Name'] == 'all_usr_prod', 'grpC'].iloc[0])  # students


def read_infrastructure():
    """
    Get infrastructure status (nodes, reservations,
    maintenances, resource limits, etc)
    """
    maints, reserv, pending_res = _read_maintenances()
    nodes = _read_nodes(reserv, pending_res)
    mpuG, mpugG, mspuG, mspugG, mpuM, mpugM, mspuM, mspugM, mpuC, mpugC, mspuC, mspugC = _read_limits()
    return Infrastructure(maints, nodes, (mpuG, mpugG, mspuG, mspugG), (mpuM, mpugM, mspuM, mspugM), (mpuC, mpugC, mspuC, mspugC))


def _parse_scontrol_joblet_nodes(jobid):
    global joblet_node_cache
    if jobid not in joblet_node_cache:
        jobline = f'scontrol show jobid -d {jobid} | grep \' Nodes=\''
        joblet_id = os.popen(jobline).read().splitlines()
        joblet_node_cache[jobid] = joblet_id
    return joblet_node_cache[jobid]


def _parse_scontrol_joblet_arrays(jobid):
    global joblet_array_cache
    if jobid not in joblet_array_cache:
        jobline = f'scontrol show jobid -d {jobid} 2>/dev/null | grep Array '
        joblet_id = os.popen(jobline).read().splitlines()
        joblet_array_cache[jobid] = joblet_id
    return joblet_array_cache[jobid]


def _purge_cache():
    global joblet_node_cache, joblet_array_cache
    joblet_node_cache = {}
    joblet_array_cache = {}


def _load_joblet_meta(line):
    if line['ST'] != 'PD':
        return [x for x in _parse_scontrol_joblet_nodes(line["JOBID"]) if line["NODELIST"] in x]
    else:
        return '[]'


def _gpus_per_joblet(line):
    if pd.isna(line['gpus_per_job']) and pd.isna(line['gpus_per_node']) and pd.isna(line['gpus_per_task']):
        return 0
    elif not pd.isna(line['gpus_per_node']):
        return line['gpus_per_node'] * (line['NODES'] if pd.isna(line['NODELIST']) else 1)
    else:
        if line['ST'] == 'PD':
            return line['gpus_per_job'] if not pd.isna(line['gpus_per_job']) else line['gpus_per_task']
        gpus_id = line['joblet_meta_str']
        gpus_id = sum([x.split('IDX:')[-1].split(')')[0].split(',') for x in gpus_id if 'gpu' in x], [])
        gpus_n = len(gpus_id) + sum([len(range(int(x.split('-')[1].split()[0]) - int(x.split('-')[0]))) for x in gpus_id if '-' in x])
        return gpus_n


def _cpus_per_joblet(line):
    if line['ST'] == 'PD':
        return line['MIN_CPUS']
    else:
        cpus_id = line['joblet_meta_str']
        cpus = sum([x.split('CPU_IDs=')[-1].split()[0].split(',') for x in cpus_id], [])
        cpus_n = len(cpus) + sum([len(range(int(x.split('-')[1].split()[0]) - int(x.split('-')[0]))) for x in cpus if '-' in x])
        return cpus_n


memunits = {
    'K': 2**-10,
    'M': 2**0,
    'G': 2**10,
    'T': 2**20
}


def parse_mem(thing):
    if thing == '0':
        return 0
    if any([l in thing for l in memunits]):
        return float(thing[:-1]) * memunits[thing[-1]]
    else:
        return thing


def _mem_per_joblet(line):
    if line['ST'] == 'PD':
        return parse_mem(line['MIN_MEMORY'])
    else:
        mem_id = line['joblet_meta_str']
        mem = sum([int(x.split('Mem=')[-1].split()[0]) for x in mem_id])
        return mem


def _true_jobid(line):

    try:
        base_jid = line.split('_')[0]
        tid = line.split('_')[1]
        tj = _parse_scontrol_joblet_arrays(line)
        assert len(tj) == 1
        return tj[0].split('JobId=')[1].split(' ')[0]
    except BaseException:
        return line


def _node_preproc(x):
    return x.replace('aimagelab-srv-', '').replace('ailb-login-', '')


def try_parse_gpu(s: str):
    if 'gpu' in s:
        try:
            return int(s.split(':')[-1].split()[0])
        except BaseException:
            return 1
    else:
        return 1


def get_mem_joblet(tres_str: str):
    try:
        mem = tres_str.split('mem=')[-1].split(',')[0]
        if 'G' in mem:
            return int(mem.split('G')[0]) * 1024
        elif 'M' in mem:
            return int(mem.split('M')[0])
        else:
            return int(mem)
    except BaseException:
        return 0


def read_jobs():
    """
    Get jobs and joblets status
    """
    instance = Singleton.getInstance()

    squeue_cmd = r'squeue -O jobarrayid:\;,Reason:\;,NodeList:\;,Username:\;,tres-per-job:\;,tres-per-task:\;,tres-per-node:\;,Name:\;,Partition:\;,StateCompact:\;,StartTime:\;,TimeUsed:\;,NumNodes:\;,NumTasks:\;,Reason:\;,MinMemory:\;,MinCpus:\;,Account:\;,PriorityLong:\;,jobid:\;,tres:\;,nice: 2> /dev/null'
    try:
        jobs_list = os.popen(squeue_cmd).read()
        squeue_df = pd.read_csv(StringIO(jobs_list), sep=';')
    except Exception as e:
        instance.err(f"Exception: {e}")
        return [], []

    instance.timeme(f"\t- squeue and dataframe creation")

    squeue_df['JOBID'] = squeue_df['JOBID'].apply(str)
    squeue_df = _split_column(squeue_df, 'NODELIST')
    squeue_df['gpus_per_node'] = squeue_df['TRES_PER_NODE'].apply(lambda x: try_parse_gpu(x) if isinstance(x, str) else x)
    squeue_df['gpus_per_job'] = squeue_df['TRES_PER_JOB'].apply(lambda x: try_parse_gpu(x) if isinstance(x, str) else x)
    squeue_df['gpus_per_task'] = squeue_df['TRES_PER_TASK'].apply(lambda x: try_parse_gpu(x) if isinstance(x, str) else x)

    try:
        squeue_df['joblet_mem'] = squeue_df['TRES_ALLOC'].apply(get_mem_joblet)
        squeue_df['joblet_gpus'] = squeue_df['TRES_ALLOC'].apply(lambda l: str(l).split('gpu=')[-1].split(',')[0] if 'gpu=' in str(l) else 0)
        squeue_df['joblet_cpus'] = squeue_df['TRES_ALLOC'].apply(lambda l: int(str(l).split('cpu=')[-1].split(',')[0]))
    except Exception as e:
        instance.err(f"Exception PD: {e}")

    instance.timeme(f"\t- re processing")
    squeue_df.rename(columns={'JOBID.1': 'TRUE_JOBID'}, inplace=True)

    instance.timeme(f"\t- processing")

    _purge_cache()
    instance.timeme(f"\t- purging cache")

    if len(squeue_df) == 0:
        return [], []

    joblets = squeue_df.apply(
        lambda line: Joblet(
            line['JOBID'],
            line['TRUE_JOBID'],
            _node_preproc(
                line['NODELIST']) if not pd.isna(
                line['NODELIST']) else None,
            line['joblet_gpus'],
            line['joblet_cpus'],
            line['joblet_mem']),
        axis=1).tolist()
    jobs = squeue_df.drop_duplicates('JOBID').apply(lambda line: Job(
        line['JOBID'], line['TRUE_JOBID'], line['NAME'], line['USER'],
        line['PARTITION'], line['ST'], line['TIME'], line['REASON'],
        line['ACCOUNT'], line['PRIORITY'], line['TRES_ALLOC'], line['START_TIME'],
        line['NICE']
    ), axis=1).tolist()

    for j in jobs:
        j.joblets = [x for x in joblets if x.jobid == j.jobid]
    return jobs, joblets


if __name__ == "__main__":
    print(read_infrastructure())
    print('\n'.join([str(x) for x in read_jobs()[0]]))
