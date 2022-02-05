class Job:
    """
    A simple class modelling a SLURM job
    """
    def __init__(self, jobid, name, user, partition, state, runtime, reason) -> None:
        self.jobid = jobid
        self.name = name
        self.user = user
        self.partition = partition
        self.state = state
        self.runtime = runtime
        self.joblets = []
        self.reason = reason

    def __repr__(self):
        return f"JOB: {self.jobid} - {self.name} ({self.user}) [{self.reason}]\n" + \
            '\n'.join(['\t' + str(x) for x in self.joblets])

class Joblet:
    """
    A simple class modelling the portion
    of a SLURM job running on a given node
    """
    
    def __init__(self, jobid, node, n_gpus, cpus, mem) -> None:
        self.jobid = jobid
        self.node = node
        self.n_gpus = int(n_gpus)
        self.mem = mem
        self.cpus = cpus

    def __repr__(self):
        return f"JOBLET: {self.jobid} on {self.node} ({self.n_gpus} gpus, {self.cpus} cpus, {self.mem/1024} Gmem)"
