import sys
import os
conf_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(conf_path)
sys.path.append(conf_path)
import readers.slurmreader 
import time
import types
import json

username = os.environ['USER']
if not os.path.exists(f'/tmp/noccfifo_{username}'):
    print('Fifo does not exist, creating...')
    os.mkfifo(f'/tmp/noccfifo_{username}')

while True:
    inf = readers.slurmreader.read_infrastructure()
    jobs, _ = readers.slurmreader.read_jobs()

    combo = types.SimpleNamespace()
    combo.inf = inf.__dict__
    combo.jobs = [j.__dict__ for j in jobs]

    with open(f'/tmp/noccfifo_{username}', 'w') as f:
        f.write(json.dumps(combo.__dict__) + '\n')
    print('Wrote to fifo')