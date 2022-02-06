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

    if updt > last_update:
        reload(readers.slurmreader)
        reload(view.slurm_list)
        reload(view.slurm_viz)
        reload(view.styles)
        last_update = updt

    try:
        inf = readers.slurmreader.read_infrastructure()
        jobs, _ = readers.slurmreader.read_jobs()


        Singleton.getInstance().rens = view.slurm_list.view_list(jobs, a_filter, stylefn=view.styles.crsstyler, width=Singleton.getInstance().left_width if hasattr(Singleton.getInstance(), 'left_width') else 72)
        Singleton.getInstance().nocc = view.slurm_viz.view_viz(inf, jobs, stylefn=view.styles.crsstyler, mode=Singleton.getInstance().view_mode if hasattr(Singleton.getInstance(), 'view_mode') else 'gpu')
    except:
        Singleton.getInstance().rens = 'Something went wrong'
        Singleton.getInstance().nocc = ':('


# configure singleton

Singleton.getInstance().signature = f"{program_name} v{version_number:.2f}"
Singleton.getInstance().fetch_subscriber.append(get_all)

wrapper(main)
