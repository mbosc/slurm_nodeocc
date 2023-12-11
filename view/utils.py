import numpy as np
import re


def is_student_viz(user):
    return user.user_group in ('studenti', 'tesisti') and not is_cvcs_viz(user)


def is_cvcs_viz(user):
    return re.search(r'cvcs|ai4a2023', user.account.lower()) is not None


def is_dev(job):
    return job.partition == 'all_serial'


def is_prod(job):
    return job.partition == 'all_usr_prod'


def to_datetime(time_str):
    return np.datetime64(re.match(r'\d+\s+(.*)\n', str(time_str)).group(1))


def to_datetime(time_str):
    return np.datetime64(re.match(r'\d+\s+(.*)\n', str(time_str)).group(1))


def maintenance_status(infrastructure):
    onmain = False
    waitString = ''
    if len(infrastructure.maintenances):
        # time format: '0   2023-12-04 14:00:00\nName: StartTime, dtype: datetime64[ns]'
        next_maintenance = sorted(infrastructure.maintenances, key=lambda x: to_datetime(x['start_time']))[0]
        start_time = to_datetime(next_maintenance['start_time'])
        end_time = to_datetime(next_maintenance['end_time'])
        time_to_maintenance = (start_time - np.datetime64('now')).astype(float)
        # TODO: fix timezone
        if time_to_maintenance < 0 and (end_time - np.datetime64('now')) > 0:
            onmain = True
        else:
            tt_d = int(time_to_maintenance / (60 * 60 * 24))
            tt_h = int(time_to_maintenance % (60 * 60 * 24) / (60 * 60))
            tt_m = int(time_to_maintenance % (60 * 60) / 60)
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
