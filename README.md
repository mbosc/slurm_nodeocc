# Slurm NodeOCC

TUI application for viewing the status of GPU allocations on a Slurm cluster

Contents:

+ `model/`: folder containing the fundamental classes definitions to model the Slurm cluster, its jobs and their portions;
+ `readers/`: folder containing the functions to parse Slurm infrastructure and jobs status from standard unix commands;
+ `view/slurm_list.py`: a simple list-based viewer of queued and allocated jobs;
+ `view/slurm_viz.py`: a graphic-based viewer of allocated jobs across Slurm topology;
+ `controller/controller.py`: the main entrypoint for the curses-based interactive TUI application.

Run it with: `python controller/controller.py`

Requirements: pandas, pycurses.