
from readers.slurmreader import read_jobs
from view.styles import cmdstyle, _format_to
import pandas as pd
import random
import numpy as np
from datetime import date

ogre = '''⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠸⣼⡿
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀ 
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉
    '''
flip = ''' ⣰⣾⣿⣿⣿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆
 ⣿⣿⣿⡿⠋⠄⡀⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠋⣉⣉⣉⡉⠙⠻⣿⣿
 ⣿⣿⣿⣇⠔⠈⣿⣿⣿⣿⣿⡿⠛⢉⣤⣶⣾⣿⣿⣿⣿⣿⣿⣦⡀⠹
 ⣿⣿⠃⠄⢠⣾⣿⣿⣿⠟⢁⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄
 ⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷
 ⣿⣿⣿⣿⣿⡟⠁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
 ⣿⣿⣿⣿⠋⢠⣾⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿
 ⣿⣿⡿⠁⣰⣿⣿⣿⣿⣿⣿⣿⣿⠗⠄⠄⠄⠄⣿⣿⣿⣿⣿⣿⣿⡟
 ⣿⡿⠁⣼⣿⣿⣿⣿⣿⣿⡿⠋⠄⠄⠄⣠⣄⢰⣿⣿⣿⣿⣿⣿⣿⠃
 ⡿⠁⣼⣿⣿⣿⣿⣿⣿⣿⡇⠄⢀⡴⠚⢿⣿⣿⣿⣿⣿⣿⣿⣿⡏⢠
 ⠃⢰⣿⣿⣿⣿⣿⣿⡿⣿⣿⠴⠋⠄⠄⢸⣿⣿⣿⣿⣿⣿⣿⡟⢀⣾
 ⢀⣿⣿⣿⣿⣿⣿⣿⠃⠈⠁⠄⠄⢀⣴⣿⣿⣿⣿⣿⣿⣿⡟⢀⣾⣿
 ⢸⣿⣿⣿⣿⣿⣿⣿⠄⠄⠄⠄⢶⣿⣿⣿⣿⣿⣿⣿⣿⠏⢀⣾⣿⣿
 ⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⠋⣠⣿⣿⣿⣿
 ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣼⣿⣿⣿⣿⣿
 ⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿
 ⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢁⣴⣿⣿⣿⣿⠗⠄⠄⣿⣿
 ⣆⠈⠻⢿⣿⣿⣿⣿⣿⣿⠿⠛⣉⣤⣾⣿⣿⣿⣿⣿⣇⠠⠺⣷⣿⣿
 ⣿⣿⣦⣄⣈⣉⣉⣉⣡⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⠉⠁⣀⣼⣿⣿⣿
 ⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣾⣿⣿⡿⠟
    '''
chunga= '''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣧⠀⠀⠀⢰⡿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡟⡆⠀⠀⣿⡇⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⣿⠀⢰⣿⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡄⢸⠀⢸⣿⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡇⢸⡄⠸⣿⡇⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⢸⡅⠀⣿⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣥⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡿⡿⣿⣿⡿⡅⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠉⠀⠉⡙⢔⠛⣟⢋⠦⢵⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣄⠀⠀⠁⣿⣯⡥⠃⠀⢳⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡇⠀⠀⠀⠐⠠⠊⢀⠀⢸⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⡿⠀⠀⠀⠀⠀⠈⠁⠀⠀⠘⣿⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣷⡀⠀⠀
⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣧⠀
⠀⠀⠀⡜⣭⠤⢍⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢛⢭⣗
⠀⠀⠀⠁⠈⠀⠀⣀⠝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠠⠀⠀⠰⡅
⠀⠀⠀⢀⠀⠀⡀⠡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠔⠠⡕
⠀⠀⠀⠀⣿⣷⣶⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀
⠀⠀⠀⠀⠘⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠊⠉⢆⠀⠀⠀
⠀⢀⠤⠀⠀⢤⣤⣽⣿⣿⣦⣀⢀⡠⢤⡤⠄⠀⠒⠀⠁⠀⠀⠀⢘⠔⠀
⠀⠀⠀⡐⠈⠁⠈⠛⣛⠿⠟⠑⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠉⠑⠒⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''

avail = '□'
occ = '■'
drain = '△'
down = '⨯'
paused = '◆'
name_chars = 12
box_chars = 16


def view_viz(infrastructure, jobs, work=True, stylefn=cmdstyle, current_user=None):
    # this is for hot reload
    if not work:
        return "UPDATE IN PROGRESS - PLZ W8 M8 B8"
    
    # who is the current user?
    if current_user is None:
        import os
        current_user = os.path.basename(os.environ['HOME'])

    nodes = infrastructure.get_sorted_nodes()
    infrast_down = all([x.status == 'down' for x in nodes])

    class RetScope:
        return_string = ''
    def cust_print(thing, style=None):
        RetScope.return_string += (thing if style is None else stylefn(style,thing)) + '\n'

    if not infrast_down:
        highlighted_users = [current_user]
        highlighted_users += pd.DataFrame([(j.user, sum([x.n_gpus for x in j.joblets])) for j in jobs if j.user != current_user]).groupby(0).sum()[1].sort_values(ascending=False).iloc[:3].index.to_list()

        user_styles = dict(zip(highlighted_users, ['RED','YELLOW','GREEN','MAGENTA','BLUE']))
        
        stalled_jobs = sum([j.state == 'S' for j in jobs])
        total_jobs_prod = 0
        total_jobs_stud = 0

        # print jobs
        for n in nodes:
            joblet_icons = []
            occs = 0
            for j in jobs:
                for jj in j.joblets:
                    if jj.n_gpus == 0:
                        continue
                    if n.name == jj.node:
                        if 'stu' in j.partition:
                            total_jobs_stud += jj.n_gpus
                        else:
                            total_jobs_prod += jj.n_gpus
                        occs += jj.n_gpus
                        icon = paused if j.state == 'S' else occ
                        st = icon + (('+' if len(j.joblets) > 1 else '-') + icon) * (jj.n_gpus-1)
                        joblet_icons.append((st, user_styles[j.user] if j.user in user_styles else None))
            joblet_icons += [(drain if n.status == 'drain' else (down if n.status == 'down' else avail), None)] * (n.n_gpus - occs)
            
            joblet_icons = [(ji[0] + (' ' if i != len(joblet_icons)-1 else ''), ji[1]) for i, ji in enumerate(joblet_icons)]

            jobsplit = [""]
            count = 0
            for ic, c in joblet_icons:
                for i in ic:
                    if count == box_chars:
                        jobsplit.append("")
                        count = 0
                    jobsplit[-1] += stylefn(c, i) if c is not None else i
                    count += 1

            for i,l in enumerate(jobsplit):
                RetScope.return_string += f'{_format_to(n.name if i == 0 else "", name_chars, "right")}{"(" if n.reserved and i == 0 else " "}{l}{")" if n.reserved and i == (len(jobline) - 1) else ""}\n'

        # verify maintenance status
        onmain = False
        if len(infrastructure.maintenances):
            next_maintenance = sorted(infrastructure.maintenances, key=lambda x: x.start_time)[0]
            time_to_maintenance = (next_maintenance.start_time - np.datetime64('now')).astype(int)
            time_to_maintenance -= (1e9 * 60 * 60) * 2 # TODO fix timezone
            if time_to_maintenance < 0 and (next_maintenance.end_time - np.datetime64('now')).astype(int) > 0:
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

        # print banner
        if onmain:
            cust_print('  ◀ ONGOING  MAINTENANCE ▶    ', 'BG_MAGENTA')
        elif len(infrastructure.maintenances):
            cust_print('  ◀ MAINTENANCE  in %4s ▶    ' % waitString, 'BG_MAGENTA')
        elif len(jobs) == 0:
            cust_print('         ◀ NO  JOBS ▶         ','BG_GREEN')
        elif stalled_jobs / len(jobs) > 0.5:
            cust_print('       ◀ JOBS ON HOLD ▶       ','BG_YELLOW')
        else:
            cust_print('')

        # print summary
        cust_print(' '.join([' ['+ occ + 'run', paused + 'hld', drain + 'drn', down + 'dwn', '()res]']))
        gpuc = 'RED'
        if infrastructure.gpu_limit_pu > 3:
            gpuc = 'YELLOW'
        if infrastructure.gpu_limit_pu > 6:
            gpuc = 'GREEN'
        cust_print(' '.join(["      gpu:", stylefn(gpuc,("%2d" % infrastructure.gpu_limit_pu) if not pd.isna(infrastructure.gpu_limit_pu) else " ∞"), " grp:", stylefn(gpuc,"%2d/%s") % (total_jobs_prod, ("%2d" % infrastructure.gpu_limit_grp) if not pd.isna(infrastructure.gpu_limit_grp) else " ∞")]))
        cust_print(' '.join(["     Sgpu:", stylefn('CYAN',("%2d" % infrastructure.gpu_limit_stu) if not pd.isna(infrastructure.gpu_limit_stu) else " ∞"), "Sgrp:", stylefn('CYAN',"%2d/%s") % (total_jobs_stud, ("%2d" % infrastructure.gpu_limit_stugrp) if not pd.isna(infrastructure.gpu_limit_stugrp) else " ∞")]))

        # print user list
        for u, c in user_styles.items():
            cust_print(f" {stylefn(c, occ)} {stylefn('CYAN', u) if any(['stu' in j.partition for j in jobs if j.user == u]) else u} ({sum([sum([jj.n_gpus for jj in j.joblets if jj.node is not None]) for j in jobs if j.user == u])})")
        cust_print(f" {stylefn('CYAN', occ)} {stylefn('CYAN', 'students')}")
        
    else: # if infrastrcture_down
        # print emergency screen
        cust_print('  ◀ INFRASTRUCTURE IS DOWN ▶  ', 'BG_RED')
        cust_print(random.choice([flip, chunga, ogre]), 'GREEN')

    return RetScope.return_string

if __name__ == '__main__':
    import sys
    from readers.slurmreader import read_infrastructure
    infr = read_infrastructure()
    jobs, _ = read_jobs()
    if len(sys.argv) > 1 and sys.argv[1] == 'work':
        print(view_viz(infr, jobs, work=True))
    else:
        print(view_viz(infr, jobs))
