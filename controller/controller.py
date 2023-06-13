import sys
import os
conf_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(conf_path)
sys.path.append(conf_path)
from curses import wrapper
from view.curses_multiwindow import main, Singleton

from importlib import reload
import readers.slurmreader 
import view.slurm_list
import view.slurm_viz
import view.styles

import time
import argparse

parser = argparse.ArgumentParser(description='Visualize slurm jobs')
parser.add_argument('--debug', action='store_true', help='Enable logging')
args = parser.parse_args()

# export args
Singleton.getInstance(args)

last_update = os.path.getmtime(conf_path + "/view/slurm_viz.py")
if os.path.getmtime(conf_path + "/view/slurm_list.py") > last_update:
    last_update = os.path.getmtime(conf_path + "/view/slurm_list.py")
if os.path.getmtime(conf_path + "/view/styles.py") > last_update:
    last_update = os.path.getmtime(conf_path + "/view/styles.py")
if os.path.getmtime(conf_path + "/readers/slurmreader.py") > last_update:
    last_update = os.path.getmtime(conf_path + "/readers/slurmreader.py")

program_name = "nodeocc"
version_number = 1.00

def get_all(a_filter):
    global last_update
    # watch for reload
    updt = os.path.getmtime(conf_path + "/view/slurm_viz.py")
    updt = max(updt, os.path.getmtime(conf_path + "/view/slurm_list.py"))
    updt = max(updt, os.path.getmtime(conf_path + "/view/styles.py"))
    updt = max(updt, os.path.getmtime(conf_path + "/readers/slurmreader.py"))

    instance = Singleton.getInstance()
    instance.timeme(f"Starting update")

    if updt > last_update:
        reload(readers.slurmreader)
        reload(view.slurm_list)
        reload(view.slurm_viz)
        reload(view.styles)
        last_update = updt

    instance.timeme(f"- reload")

    try:
        inf = readers.slurmreader.read_infrastructure()
        instance.timeme(f"- infrastructure load")

        jobs, _ = readers.slurmreader.read_jobs()
        instance.timeme(f"- jobs list read")
        
        instance.rens = view.slurm_list.view_list(jobs, a_filter, stylefn=view.styles.crsstyler, width=instance.left_width if hasattr(instance, 'left_width') else 72, jit=instance.job_id_type if hasattr(instance, 'job_id_type') else 'agg')
        instance.timeme(f"- print job list")

        instance.nocc = view.slurm_viz.view_viz(inf, jobs, stylefn=view.styles.crsstyler, mode=instance.view_mode if hasattr(instance, 'view_mode') else 'gpu')
        instance.timeme(f"- view nodeocc")

    except Exception as e:
        instance.err(f"Exception: {e}")
        instance.rens = 'Something went wrong'
        instance.nocc = ':('


# configure singleton

Singleton.getInstance().signature = f"{program_name} v{version_number:.2f}"
Singleton.getInstance().fetch_subscriber.append(get_all)

wrapper(main)
