import os
from io import StringIO
import pandas as pd
from model.infrastructure import Node, Maintenance, Infrastructure
from model.job import Job, Joblet

joblet_cache = {}

def _ungroup_slurm_names(x):
    if '[' in x:
        tokens = x.split('[')[1].split(']')[0].split(',')
        return ','.join([x.split('[')[0].split(',')[-1] + tok + x.split(']')[1].split(',')[0] for tok in tokens] + \
            [a for a in x.split(',') if '[' not in a and ']' not in a])
    else:
        return x

def _split_column(df, column):
    # flatten representation
    node_flat = pd.DataFrame([[i, x] 
               for i, y in df[column].fillna('').apply(_ungroup_slurm_names).str.split(',').iteritems() 
                    for x in y], columns=['__I', column]).set_index('__I')
    node_flat[column] = node_flat[column].replace('', float('nan'))
    return node_flat.merge(df[[x for x in df.columns if x != column]], left_index=True, right_index=True).reset_index(drop=True)

def _node_from_sinfo(x):
    n = Node(_node_preproc(x['NODELIST']), x.n_gpu, x.m_gpu, x.reserved, None, x.CPUS, x.MEMORY)
    if x['STATE'] == 'drng' or 'drain' in x['STATE']:
        n.status = 'drain'
    elif x['STATE'].upper() in ['MAINT', 'DOWN', 'DOWN*', 'FAIL', 'FAILING', 'FAIL*']:
        n.status = 'down'
    else:
        n.status = 'ok'
    return n


def _read_nodes(reservations):
    sinfo_df = pd.read_csv(StringIO(os.popen(r'sinfo -N -o "%N;%G;%t;%m;%c"').read()), sep=';')
    sinfo_df = _split_column(sinfo_df, 'NODELIST')
    sinfo_df['n_gpu'] = sinfo_df['GRES'].str.split(':').apply(lambda x: 0 if x[0] == '(null)' else int(x[-1]))
    sinfo_df['m_gpu'] = sinfo_df['GRES'].str.split(':').apply(lambda x: 'n/a' if x[0] == '(null)' else x[1])
    if reservations is not None:
        sinfo_df['reserved'] = sinfo_df['NODELIST'].isin(reservations.Nodes.unique())
    else:
        sinfo_df['reserved'] = False
    
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
    reservations = [{c.split('=')[0]:c.split('=')[1] for c in r.split()} for r in reservations if len(r) and '=' in r]
    if not len(reservations):
        return [], None
    reservations = pd.DataFrame.from_records(reservations)
    reservations['StartTime'] = pd.to_datetime(reservations['StartTime'])
    reservations['EndTime'] = pd.to_datetime(reservations['EndTime'])
    reservations = _split_column(reservations, 'Nodes')
    maint_flag = reservations['Flags'].str.contains('MAINT') #| reservations['ReservationName'].str.contains('limit_temp')
    
    maintenances = _maint_from_reservations(reservations[maint_flag])
    return maintenances, reservations[(~maint_flag) & (reservations['State'] == 'ACTIVE')]

def _read_limits():
    """
    Read the maximum amount of GPUs allowed
    :returns max_prod_per_user, max_prod_group, max_studentsprod_per_user, max_studentsprod_group
    """
    lims = pd.read_fwf(StringIO(os.popen(r'sacctmgr show qos format=\'name%15,maxtresperuser%25,grptres%25,maxjobsperuser\' 2>/dev/null').read())).loc[1:]
    lims['pu'] = lims['MaxTRESPU'].apply(lambda x: int(x.split('gres/gpu=')[1].split(',')[0]) if type(x)==str and 'gres/gpu' in x else float('nan'))
    lims['grp'] = lims['GrpTRES'].apply(lambda x: int(x.split('gres/gpu=')[1].split(',')[0]) if type(x)==str and 'gres/gpu' in x else float('nan'))
    return (lims.loc[lims['Name'] == 'prod', 'pu'].iloc[0], 
            lims.loc[lims['Name'] == 'prod', 'grp'].iloc[0],
            lims.loc[lims['Name'] == 'students-prod', 'pu'].iloc[0],
            lims.loc[lims['Name'] == 'students-prod', 'grp'].iloc[0])

def read_infrastructure():
    """
    Get infrastructure status (nodes, reservations,
    maintenances, resource limits, etc)
    """
    maints, reserv = _read_maintenances()
    nodes = _read_nodes(reserv)
    mpu, mpug, mspu, mspug = _read_limits()
    return Infrastructure(maints, nodes, mpu, mpug, mspu, mspug)


def _parse_scontrol_joblet(jobid):
    global joblet_cache
    if jobid not in joblet_cache:
        jobline = f'scontrol show jobid -d {jobid} | grep \' Nodes=\''
        joblet_id = os.popen(jobline).read().splitlines()
        joblet_cache[jobid] = joblet_id
    return joblet_cache[jobid]

def _purge_cache():
    global joblet_cache
    joblet_cache = {}

def _gpus_per_joblet(line):
    if pd.isna(line['gpus_per_job']) and pd.isna(line['gpus_per_node']) and pd.isna(line['gpus_per_task']):
        return 0
    elif not pd.isna(line['gpus_per_node']):
        return line['gpus_per_node'] * (line['NODES'] if pd.isna(line['NODELIST']) else 1)
    else:
        if line['ST'] == 'PD':
            return line['gpus_per_job']
        gpus_id = [x for x in _parse_scontrol_joblet(line["JOBID"]) if line["NODELIST"] in x]
        gpus_id = sum([x.split('IDX:')[-1].split(')')[0].split(',') for x in gpus_id if 'gpu' in x], [])
        gpus_n = len(gpus_id) + sum([len(range(int(x.split('-')[1].split()[0]) - int(x.split('-')[0]))) for x in gpus_id if '-' in x])
        return gpus_n

def _cpus_per_joblet(line):
    if line['ST'] == 'PD':
        return line['MIN_CPUS']
    else:
        cpus_id = [x for x in _parse_scontrol_joblet(line["JOBID"]) if line["NODELIST"] in x]
        cpus = sum([x.split('CPU_IDs=')[-1].split()[0].split(',') for x in cpus_id], [])
        cpus_n = len(cpus) + sum([len(range(int(x.split('-')[1].split()[0]) - int(x.split('-')[0]))) for x in cpus if '-' in x])
        return cpus_n

memunits = {
    'K': 1/2e10,
    'M': 2e0,
    'G': 2e10,
    'T': 2e20
}

def _mem_per_joblet(line):
    if line['ST'] == 'PD':
        if any([l in line['MIN_MEMORY'] for l in memunits]):
            return float(line['MIN_MEMORY'][:-1]) * memunits[line['MIN_MEMORY'][-1]]
        else:
            return line['MIN_MEMORY']
    else:
        mem_id = [x for x in _parse_scontrol_joblet(line["JOBID"]) if line["NODELIST"] in x]
        mem = sum([int(x.split('Mem=')[-1].split()[0]) for x in mem_id])
        return mem

def _node_preproc(x):
    return x.replace('aimagelab-srv-', '')

def read_jobs():
    """
    Get jobs and joblets status
    """
    squeue_cmd = r'squeue -O jobarrayid:\;,Reason:\;,NodeList:\;,Username:\;,tres-per-job:\;,tres-per-task:\;,tres-per-node:\;,Name:\;,Partition:\;,StateCompact:\;,StartTime:\;,TimeUsed:\;,NumNodes:\;,NumTasks:\;,Reason:\;,MinMemory:\;,MinCpus 2> /dev/null'
    squeue_df = pd.read_csv(StringIO(os.popen(squeue_cmd).read()), sep=';')
    squeue_df['JOBID'] = squeue_df['JOBID'].apply(lambda x: str(x))
    squeue_df = _split_column(squeue_df, 'NODELIST')
    squeue_df['gpus_per_node'] = squeue_df['TRES_PER_NODE'].apply(lambda x: int(x.split(':')[-1].split()[0] if x != 'gpu' else 1) if type(x) == str else x)
    squeue_df['gpus_per_job'] = squeue_df['TRES_PER_JOB'].apply(lambda x: int(x.split(':')[-1].split()[0] if x != 'gpu' else 1) if type(x) == str else x)
    squeue_df['gpus_per_task'] = squeue_df['TRES_PER_TASK'].apply(lambda x: int(x.split(':')[-1].split()[0] if x != 'gpu' else 1) if type(x) == str else x)
    squeue_df['joblet_gpus'] = squeue_df[['gpus_per_node', 'gpus_per_job', 'gpus_per_task', 'TASKS', 'NODELIST', 'NODES', 'JOBID', 'ST']].apply(_gpus_per_joblet, axis=1)
    squeue_df['joblet_cpus'] = squeue_df[['gpus_per_node', 'gpus_per_job', 'gpus_per_task', 'TASKS', 'NODELIST', 'NODES', 'JOBID', 'ST', 'MIN_CPUS']].apply(_cpus_per_joblet, axis=1)
    squeue_df['joblet_mem'] = squeue_df[['gpus_per_node', 'gpus_per_job', 'gpus_per_task', 'TASKS', 'NODELIST', 'NODES', 'JOBID', 'ST', 'MIN_MEMORY']].apply(_mem_per_joblet, axis=1)
    _purge_cache()

    # import pdb; pdb.set_trace()
    joblets = squeue_df.apply(lambda line: Joblet(line['JOBID'], _node_preproc(line['NODELIST']) if not pd.isna(line['NODELIST']) else None, line['joblet_gpus'], line['joblet_cpus'], line['joblet_mem']), axis=1).tolist()
    jobs = squeue_df.drop_duplicates('JOBID').apply(lambda line: Job(
        line['JOBID'], line['NAME'], line['USER'],
        line['PARTITION'], line['ST'], line['TIME'], line['REASON']
        ), axis=1).tolist()

    for j in jobs:
        j.joblets = [x for x in joblets if x.jobid == j.jobid]
    return jobs, joblets

if __name__ == "__main__":
    print(read_infrastructure())
    print('\n'.join([str(x) for x in read_jobs()[0]]))
