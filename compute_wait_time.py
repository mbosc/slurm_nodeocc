#!/usr/local/anaconda3/bin/python
import os
import numpy as np
import sys

if len(sys.argv) > 1:
    user = sys.argv[1]
else:
    user = None

def get_sec(time_str):
    days_chks = time_str.split('-')
    if len(days_chks) > 1:
        days = days_chks[0]
        time_str = days_chks[1]
    else:
        days = 0
    h, m, s = time_str.split(':')
    return int(days) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)

def pprint_sec(sec):
    if sec<0:
        return '-1 hrs and -1 mins'
    h = sec // 3600
    m = (sec % 3600)
    m, s = m // 60, m % 60
    return '%d hrs and %02d mins' % (h, m)

print("  WAITING TIMES:")
for partition in ['prod', 'students-prod']:
  cmd = 'sacct --noheader -X -a --partition=%s --start=now-1weeks --format="Reserved"' % partition
  if user:
      cmd += ' --user %s' % user
  output = os.popen(cmd).readlines()
  wait_times = []

  for line in output:
      if ':' not in line:
          continue
      wait_times.append(get_sec(line.strip()))

  wait_times = np.asarray(wait_times)
  avg_wait_time = np.mean(wait_times) if len(wait_times)>0 else -1
  print("  Average on %s is %s" % (partition, pprint_sec(avg_wait_time)))

print("=================================================================================")
