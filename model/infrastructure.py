from typing import List


class Node(object):
    """
    A simple class modelling a node within
    the SLURM infrastructure
    """

    def __init__(self, name, n_gpus, gpu_model, reserved, status, cpus, mem) -> None:
        self.name = name
        self.n_gpus = n_gpus
        self.gpu_model = gpu_model
        self.reserved = reserved
        assert reserved in ('no', 'yes', 'pending')
        self.status = status
        self.cpus = cpus
        self.mem = mem

    def __repr__(self):
        return f'NODE {self.name} - {self.n_gpus}x{self.gpu_model} [{self.cpus}/{self.mem/1000}] - {self.status} ({self.reserved} reserv)'


class Maintenance(object):
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

    @staticmethod
    def from_dict(d):
        m = Maintenance(None, None, None)
        for k, v in d.items():
            setattr(m, k, v)
        return m

    def to_nested_dict(self):
        return {
            k: v for k, v in self.__dict__.items()
        }


class Infrastructure(object):
    def __init__(self, maintenances: List[Maintenance], nodes, gpu_lims, ram_lims, cpu_lims) -> None:
        self.maintenances = maintenances
        self.nodes = nodes
        gpu_limit_pu, gpu_limit_grp, gpu_limit_stu, gpu_limit_stugrp = gpu_lims
        ram_limit_pu, ram_limit_grp, ram_limit_stu, ram_limit_stugrp = ram_lims
        cpu_limit_pu, cpu_limit_grp, cpu_limit_stu, cpu_limit_stugrp = cpu_lims
        self.gpu_limit_pu = gpu_limit_pu
        self.gpu_limit_grp = gpu_limit_grp
        self.gpu_limit_stu = gpu_limit_stu
        self.gpu_limit_stugrp = gpu_limit_stugrp
        self.ram_limit_pu = ram_limit_pu
        self.ram_limit_grp = ram_limit_grp
        self.ram_limit_stu = ram_limit_stu
        self.ram_limit_stugrp = ram_limit_stugrp
        self.cpu_limit_pu = cpu_limit_pu
        self.cpu_limit_grp = cpu_limit_grp
        self.cpu_limit_stu = cpu_limit_stu
        self.cpu_limit_stugrp = cpu_limit_stugrp
        self.prior = ['RTX6000', '2080', 'V100', 'RTX5000', '1080', 'P100', None, 'K80']

    @staticmethod
    def from_dict(d):
        i = Infrastructure(None, None, [None] * 4, [None] * 4, [None] * 4)
        for k, v in d.items():
            if k == 'nodes':
                setattr(i, k, [Node(**n) for n in v])
            else:
                setattr(i, k, v)
        return i

    def to_nested_dict(self):
        return {
            k: ([n.__dict__ for n in self.nodes] if k == 'nodes' else
                ([n.to_nested_dict() for n in self.maintenances] if k == 'maintenances' else v))
            for k, v in self.__dict__.items()
        }

    def __repr__(self):
        return "INFRASTRUCTURE\n" + "\n".join([str(x) for x in self.maintenances]) + "\n\n" + "\n".join([str(x) for x in self.nodes]) + \
            f"\n\nlimits:({self.gpu_limit_pu}:{self.gpu_limit_grp}),({self.gpu_limit_stu}:{self.gpu_limit_stugrp})"

    def get_sorted_nodes(self):

        return sorted(self.nodes, key=lambda x: self.prior.index(x.gpu_model) if x.gpu_model in self.prior else -1)
