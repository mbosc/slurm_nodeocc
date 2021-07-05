class Node:
    """
    A simple class modelling a node within
    the SLURM infrastructure
    """
    def __init__(self, name, n_gpus, gpu_model, reserved, status) -> None:
        self.name = name
        self.n_gpus = n_gpus
        self.gpu_model = gpu_model
        self.reserved = reserved
        self.status = status

    def __repr__(self):
        return f'NODE {self.name} - {self.n_gpus}x{self.gpu_model} - {self.status} ({"not " if not self.reserved else ""}reserved)'

class Maintenance:
    """
    A simple class modelling a pending
    SLURM maintenance
    """
    def __init__(self, nodes, start_time, end_time) -> None:
        self.nodes = nodes
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f'RESERVATION {self.start_time} - {self.end_time} on {",".join(self.nodes)}'

class Infrastructure:
    def __init__(self, maintenances, nodes, gpu_limit_pu, gpu_limit_grp, gpu_limit_stu, gpu_limit_stugrp) -> None:
        self.maintenances = maintenances
        self.nodes = nodes
        self.gpu_limit_pu = gpu_limit_pu
        self.gpu_limit_grp = gpu_limit_grp
        self.gpu_limit_stu = gpu_limit_stu
        self.gpu_limit_stugrp = gpu_limit_stugrp
        self.prior = ['RTX6000', '2080', 'V100', 'RTX5000', '1080', 'P100', 'K80']

    def __repr__(self):
        return "INFRASTRUCTURE\n" + "\n".join([str(x) for x in self.maintenances]) + "\n\n" + "\n".join([str(x) for x in self.nodes]) + f"\n\nlimits:({self.gpu_limit_pu}:{self.gpu_limit_grp}),({self.gpu_limit_stu}:{self.gpu_limit_stugrp})"

    def get_sorted_nodes(self):
        
        return sorted(self.nodes, key=lambda x: self.prior.index(x.gpu_model) if x.gpu_model in self.prior else -1)