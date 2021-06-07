import os
from io import StringIO
import pandas as pd
from model.infrastructure import Node, Maintenance, Infrastructure
from model.job import Job, Joblet

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
    n = Node(_node_preproc(x['NODELIST']), x.n_gpu, x.m_gpu, x.reserved, None)

    if x['STATE'] in ['drain', 'drng']:
        n.status = 'drain'
    elif x['STATE'] in ['MAINT', 'DOWN']:
        n.status = 'down'
    else:
        n.status = 'ok'
    return n


def _read_nodes(reservations):
    sinfo_df = pd.read_csv(StringIO(os.popen(r'sinfo -o "%N;%G;%t"').read()), sep=';')
    sinfo_df = _split_column(sinfo_df, 'NODELIST')
    
    sinfo_df['n_gpu'] = sinfo_df['GRES'].str.split(':').apply(lambda x: int(x[-1]))
    sinfo_df['m_gpu'] = sinfo_df['GRES'].str.split(':').apply(lambda x: x[1])
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
    maint_flag = reservations['Flags'].str.contains('MAINT')
    
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
    

def _gpus_per_joblet(line):
    
    if pd.isna(line['gpus_per_job']) and pd.isna(line['gpus_per_node']):
        return 0
    elif not pd.isna(line['gpus_per_node']):
        return line['gpus_per_node'] * (line['NODES'] if pd.isna(line['NODELIST']) else 1)
    else:
        jobline = f'scontrol show jobid -d {line["JOBID"]} | grep Nodes={line["NODELIST"]}'
        gpus_id = os.popen(jobline).read().split('IDX:')[-1].split(')')[0].split(',')
        gpus_n = len(gpus_id) + sum([len(range(int(x.split('-')[1]) - int(x.split('-')[0]))) for x in gpus_id if '-' in x])
        return gpus_n

def _node_preproc(x):
    return x.replace('aimagelab-srv-', '')

def read_jobs():
    """
    Get jobs and joblets status
    """
    squeue_cmd = r'squeue -O jobarrayid,Reason:130,NodeList:120,Username,tres-per-job,tres-per-node,Name:50,Partition,StateCompact,StartTime,TimeUsed,NumNodes,Reason:40 2> /dev/null'
    squeue_df = pd.read_fwf(StringIO(os.popen(squeue_cmd).read()))
    
    squeue_df = _split_column(squeue_df, 'NODELIST')
    squeue_df['gpus_per_node'] = squeue_df['TRES_PER_NODE'].apply(lambda x: int(x.split(':')[-1] if x != 'gpu' else 1) if type(x) == str else x)
    squeue_df['gpus_per_job'] = squeue_df['TRES_PER_JOB'].apply(lambda x: int(x.split(':')[-1] if x != 'gpu' else 1) if type(x) == str else x)
    squeue_df['joblet_gpus'] = squeue_df[['gpus_per_node', 'gpus_per_job', 'NODELIST', 'NODES', 'JOBID']].apply(_gpus_per_joblet, axis=1)

    joblets = squeue_df.apply(lambda line: Joblet(line['JOBID'], _node_preproc(line['NODELIST']) if not pd.isna(line['NODELIST']) else None, line['joblet_gpus']), axis=1).tolist()
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
