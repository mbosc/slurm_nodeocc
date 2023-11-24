import os
import numpy as np

def get_sec(time_str):
    days_chks = time_str.split('-')
    if len(days_chks) > 1:
        days = days_chks[0]
        time_str = days_chks[1]
    else:
        days = 0
    h, m, s = time_str.split(':')
    return int(days) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)

def get_wait_time(partition):
    assert partition in ['prod', 'students-prod']
    cmd = 'sacct --noheader -X -a --partition=%s --start=now-1weeks --format="Reserved"' % partition

    output = os.popen(cmd).readlines()
    wait_times = []

    for line in output:
        if ':' not in line:
            continue
        wait_times.append(get_sec(line.strip()))

    wait_times = np.asarray(wait_times)
    avg_wait_time = np.mean(wait_times) if len(wait_times)>0 else -1
    return avg_wait_time