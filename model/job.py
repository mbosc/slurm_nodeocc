import grp
import os
from pwd import getpwnam

from view.curses_multiwindow import Singleton


class Job:
    """
    A simple class modelling a SLURM job
    """

    def __init__(self, jobid, true_jobid, name, user, partition, state, runtime, reason, account, priority, tres, start_time, nice) -> None:
        self.jobid = jobid
        self.true_jobid = str(true_jobid)
        self.name = name
        self.user = user
        self.partition = partition
        self.state = state
        self.runtime = runtime
        self.joblets = []
        self.reason = reason
        self.account = account
        self.priority = priority
        self.tres = tres
        self.starttime = start_time
        self.nice = nice
        self.user_group = grp.getgrgid(getpwnam(self.user)[3]).gr_name if self.user is not None else None

    def is_student(self):
        return self.user_group in ['studenti', 'tesisti']

    @staticmethod
    def from_dict(d):
        j = Job(None, None, None, None, None, None, None, None, None, None, None, None, None)
        j.joblets = []
        for k, v in d.items():
            if k == 'joblets':
                setattr(j, k, [Joblet(**jblet) for jblet in v])
            else:
                setattr(j, k, v)
        return j

    def to_nested_dict(self):
        return {
            k: (v if k != 'joblets' else [n.__dict__ for n in self.joblets]) for k, v in self.__dict__.items()
        }

    def __repr__(self):
        return f"JOB: {self.jobid} - {self.name} ({self.user}) [{self.reason}]\n" + \
            '\n'.join(['\t' + str(x) for x in self.joblets])


class Joblet:
    """
    A simple class modelling the portion
    of a SLURM job running on a given node
    """

    def __init__(self, jobid, true_jobid, node, n_gpus, cpus, mem) -> None:
        self.jobid = jobid
        self.true_jobid = true_jobid
        self.node = node.replace('ailb-login-02', '0💀') if node is not None else None
        self.n_gpus = int(n_gpus)
        self.mem = mem
        self.cpus = cpus

    def __repr__(self):
        try:
            if isinstance(self.mem, str):
                retstr = f"JOBLET: {self.jobid} on {self.node} ({self.n_gpus} gpus, {self.cpus} cpus, {self.mem} Mmem)"
            retstr = f"JOBLET: {self.jobid} on {self.node} ({self.n_gpus} gpus, {self.cpus} cpus, {self.mem/1024} Gmem)"
        except Exception as e:
            Singleton.getInstance().err(f"Exception in joblet repr: {e}")
        return retstr
