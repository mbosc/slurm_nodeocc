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
import json
import argparse
import traceback
from model.infrastructure import Infrastructure
from model.job import Job

BEGIN_DELIM = "!{$"
END_DELIM_ENCODED = "!}$".encode('utf-8')
MAX_BUF = 65535
MAX_MSG_LEN = 8*1024*1024

parser = argparse.ArgumentParser(description='Visualize slurm jobs')
parser.add_argument('--debug', action='store_true', help='Enable logging')
parser.add_argument('--master', action='store_true', help='Enable logging')
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
        if args.master:
            inf = readers.slurmreader.read_infrastructure()
            instance.timeme(f"- infrastructure load")

            jobs, _ = readers.slurmreader.read_jobs()
            instance.timeme(f"- jobs list read")

            # send data to clients (if any)
            msg = json.dumps({'inf': inf.to_nested_dict(), 'jobs': [j.to_nested_dict() for j in jobs]})

            # msg to bytes
            msg = msg.encode('utf-8')
            msg_len = len(msg)
            msg = (str(msg_len)+BEGIN_DELIM).encode('utf-8') + msg + END_DELIM_ENCODED
            instance.timeme(f"- msg encoded with len {str(msg_len)}")

            instance.sock.sendto(msg ,('<broadcast>', instance.port))
            instance.timeme(f"- broadcast")
        else:
            instance.timeme(f"- listening for data")
            
            # listen for data from master
            data, addr = instance.sock.recvfrom(MAX_BUF)

            if BEGIN_DELIM in data.decode('utf-8'):
                msg_len = int(data.decode('utf-8').split(BEGIN_DELIM)[0]) 
                msg_len += len(str(msg_len)) + 2
                instance.timeme(f"about to receive {msg_len} bytes")
                while END_DELIM_ENCODED not in data:
                    buf_len = min(MAX_BUF, msg_len - len(data))
                    instance.timeme(f"bytes remaining {msg_len - len(data)} - receiving")
                    data += instance.sock.recvfrom(buf_len)[0]

                    if len(data) > MAX_MSG_LEN:
                        instance.err(f"Message too long, aborting")
                        return

                data = data.split(END_DELIM_ENCODED)[0]
                # data = data[:msg_len]
                data = data.decode('utf-8')
                data = data.split(BEGIN_DELIM)[1]
            
                msg = json.loads(data)
                inf = Infrastructure.from_dict(msg['inf'])
                jobs = [Job.from_dict(j) for j in msg['jobs']]
                instance.timeme(f"- receive")
            else:
                instance.timeme(f"- no data")
                return
        
        instance.rens = view.slurm_list.view_list(jobs, a_filter, stylefn=view.styles.crsstyler, width=instance.left_width if hasattr(instance, 'left_width') else 72, jit=instance.job_id_type if hasattr(instance, 'job_id_type') else 'agg')
        instance.timeme(f"- print job list")

        instance.nocc = view.slurm_viz.view_viz(inf, jobs, stylefn=view.styles.crsstyler, mode=instance.view_mode if hasattr(instance, 'view_mode') else 'gpu')
        instance.timeme(f"- view nodeocc")

    except Exception as e:
        instance.err(f"Exception: {e}")
        instance.err(traceback.format_exc())
        instance.rens = 'Something went wrong'
        instance.nocc = ':('


# configure singleton

Singleton.getInstance().signature = f"{program_name} v{version_number:.2f}"
Singleton.getInstance().fetch_subscriber.append(get_all)

wrapper(main)
