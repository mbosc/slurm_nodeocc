import numpy as np
import re

def is_student_viz(user):
    return 'students' in user.partition and re.search(r'cvcs|ai4a2023', user.account.lower()) is None

def is_cvcs_viz(user):
    return re.search(r'cvcs|ai4a2023', user.account.lower()) is not None

def maintenance_status(infrastructure):
    onmain = False
    waitString = ''
    if len(infrastructure.maintenances):
        next_maintenance = sorted(infrastructure.maintenances, key=lambda x: x.start_time)[0]
        time_to_maintenance = (next_maintenance.start_time - np.datetime64('now')).astype(int)
        time_to_maintenance -= (1e9 * 60 * 60) * 2 # TODO fix timezone
        if time_to_maintenance < 0 and (next_maintenance.end_time - np.datetime64('now')).seconds > 0:
            onmain = True
        else:
            tt_d = int(time_to_maintenance / (1e9 * 60 * 60 * 24))
            tt_h = int(time_to_maintenance % (1e9 * 60 * 60 * 24) / (1e9 * 60 * 60))
            tt_m = int(time_to_maintenance % (1e9 * 60 * 60) / (1e9 * 60))
            if tt_d > 0:
                waitString = '%dd' % tt_d
            elif tt_h > 0:
                waitString = '%dh' % tt_h
            else:
                waitString = '%dm' % tt_m
    return onmain, waitString

numfont = '⁰¹²³⁴⁵⁶⁷⁸⁹'

def to_font(num):
    if num < 0:
        return '⁻' + to_font(-num)
    return ''.join([numfont[int(i)] for i in str(num)])
