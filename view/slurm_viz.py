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

gpu_avail = '□'
gpu_occ = '■'
gpu_drain = '△'
gpu_pendr = '⧖'
gpu_down = '⨯'
gpu_paused = '◆'
gpu_name_chars = 12
gpu_box_chars = 16

mem_size = 16
mem_unit = 'ᴳ'
ram_occ = '█' # '▄'#
ram_occ_alt = '▀'
ram_avail = '░'
ram_drain = '△'
ram_pendr ='⧖'
ram_paused = '▚'
ram_down = '⨯'

numfont = '⁰¹²³⁴⁵⁶⁷⁸⁹'
# numfont = '𝟻𝟻𝟻𝟻𝟻𝟻𝟻𝟻𝟻𝟻'

def to_font(num):
    return ''.join([numfont[int(i)] for i in str(num)])

def get_ram_block(megs):
    return int(round(megs/1024/mem_size))

def view_viz(infrastructure, jobs, work=True, stylefn=cmdstyle, current_user=None, mode='gpu'):
    if mode == 'gpu':
        return view_viz_gpu(infrastructure, jobs, work, stylefn, current_user)
    else:
        return view_viz_ram(infrastructure, jobs, work, stylefn, current_user)

def view_viz_ram(infrastructure, jobs, work=True, stylefn=cmdstyle, current_user=None):
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
        highlighted_users += pd.DataFrame([(j.user, sum([get_ram_block(x.mem) for x in j.joblets])) for j in jobs if j.user != current_user and j.state in ['R', 'S']]).groupby(0).sum()[1].sort_values(ascending=False).iloc[:3].index.to_list()

        user_styles = dict(zip(highlighted_users, ['RED','YELLOW','GREEN','MAGENTA','BLUE']))
        students = [j.user for j in jobs if 'students' in j.partition and 'cvcs' not in j.account.lower()]
        for s in students:
            user_styles[s] = 'CYAN'

        cvcs_students = [j.user for j in jobs if 'cvcs' in j.account.lower()]
        for s in cvcs_students:
            user_styles[s] = 'BG_CYAN'

        stalled_jobs = sum([j.state == 'S' for j in jobs])
        total_jobs_prod = 0
        total_jobs_stud = 0

        # print jobs
        for n in nodes:
            joblet_icons = []
            occs = 0
            for j in sorted(jobs, key=lambda x: (x.partition, x.user)):
                for jj in j.joblets:
                    if n.name == jj.node:
                        if 'stu' in j.partition and 'prod' in j.partition:
                            total_jobs_stud += int(round((jj.mem) / 1024))
                        elif 'prod' in j.partition:
                            total_jobs_prod += int(round((jj.mem) / 1024))
                        occs += jj.mem
                        icon = ram_paused if j.state == 'S' else ram_occ
                        st = icon * get_ram_block(jj.mem)
                        joblet_icons.append((st, user_styles[j.user] if j.user in user_styles else None))
            joblet_icons += [(ram_drain if n.status == 'drain' else (ram_down if n.status == 'down' else (ram_pendr if n.reserved == 'pending' else ram_avail)), None)] * get_ram_block(n.mem - occs)
            
            jobsplit = [""]
            count = 0
            for ic, c in joblet_icons:
                for i in ic:
                    if count == gpu_box_chars - 3:
                        jobsplit.append("")
                        count = 0
                    bb = ram_occ_alt if len(jobsplit) > 1 and i == ram_occ else i
                    jobsplit[-1] += stylefn(c, bb) if c is not None else bb
                    count += 1
            # if count < gpu_box_chars:
            jobsplit[-1] += f'{to_font(int((n.mem-occs) / 1024))}'

            for i,l in enumerate(jobsplit):
                RetScope.return_string += f'{_format_to(n.name if i == 0 else "", gpu_name_chars, "right")}{"(" if n.reserved == "yes" and i == 0 else " "}{l}{")" if n.reserved == "yes" and i == (len(jobsplit) - 1) else ""}\n'

        # verify maintenance status
        onmain = False
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
        # cust_print(''.join([' ['+ ram_occ + 'run', paused + 'hld', drain + 'drn', down + 'dwn', '()res]']))
        cust_print(''.join(['['+ ram_occ + f'{mem_size}{mem_unit}', ram_paused + 'hld', ram_drain + 'drn', ram_pendr + 'pnd',  ram_down + 'dwn', '()res]']))
        gpuc = 'GREEN'
        # if infrastructure.gpu_limit_pu > 3:
        #     gpuc = 'YELLOW'
        # if infrastructure.gpu_limit_pu > 6:
        #     gpuc = 'GREEN'
        cust_print(' '.join(["  ram:", stylefn(gpuc,(f"{int(round(infrastructure.ram_limit_pu / 1024)):4d}{mem_unit}") 
            if not pd.isna(infrastructure.ram_limit_pu) else " ∞"), 
            " grp:", stylefn(gpuc,f"{total_jobs_prod:4d}{mem_unit}/{int(round(infrastructure.ram_limit_grp / 1024))}{mem_unit}" 
            if not pd.isna(infrastructure.ram_limit_grp) else " ∞")]))
        cust_print(' '.join([" Sram:", stylefn('CYAN',(f"{int(round(infrastructure.ram_limit_stu / 1024)):4d}{mem_unit}") 
            if not pd.isna(infrastructure.ram_limit_stu) else " ∞"),
            "Sgrp:", stylefn('CYAN',f"{total_jobs_stud:4d}{mem_unit}/{int(round(infrastructure.ram_limit_stugrp / 1024))}{mem_unit}" 
            if not pd.isna(infrastructure.ram_limit_stugrp) else " ∞")]))

        # print user list
        for u, c in user_styles.items():
            if c == 'CYAN' or c == 'BG_CYAN':
                continue
            cust_print(f" {stylefn(c, gpu_occ)} {stylefn('CYAN', u) if any(['stu' in j.partition for j in jobs if j.user == u]) else u} ({int(round(sum([sum([jj.mem / 1024 for jj in j.joblets if jj.node is not None]) for j in jobs if j.user == u])))}{mem_unit})")
        cust_print(f" {stylefn('CYAN', gpu_occ)} {stylefn('CYAN', 'students')}")
        cust_print(f" {stylefn('BG_CYAN', gpu_occ)} {stylefn('BG_CYAN', 'cvcs')}")
        
    else: # if infrastrcture_down
        # print emergency screen
        cust_print('  ◀ INFRASTRUCTURE IS DOWN ▶  ', 'BG_RED')
        cust_print(random.choice([flip, chunga, ogre]), 'GREEN')

    return RetScope.return_string

def view_viz_gpu(infrastructure, jobs, work=True, stylefn=cmdstyle, current_user=None):
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
        highlighted_users += pd.DataFrame([(j.user, sum([x.n_gpus for x in j.joblets])) for j in jobs if j.user != current_user and j.state in ['R', 'S']]).groupby(0).sum()[1].sort_values(ascending=False).iloc[:3].index.to_list()

        user_styles = dict(zip(highlighted_users, ['RED','YELLOW','GREEN','MAGENTA','BLUE']))
        students = [j.user for j in jobs if 'students' in j.partition and 'cvcs' not in j.account.lower()]
        for s in students:
            user_styles[s] = 'CYAN'
        
        cvcs_students = [j.user for j in jobs if 'cvcs' in j.account.lower()]
        for s in cvcs_students:
            user_styles[s] = 'BG_CYAN'

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
                        if 'stu' in j.partition and 'prod' in j.partition:
                            total_jobs_stud += jj.n_gpus
                        elif 'prod' in j.partition:
                            total_jobs_prod += jj.n_gpus
                        occs += jj.n_gpus
                        icon = gpu_paused if j.state == 'S' else gpu_occ
                        st = icon + (('+' if len(j.joblets) > 1 else '-') + icon) * (jj.n_gpus-1)
                        joblet_icons.append((st, user_styles[j.user] if j.user in user_styles else None))
            joblet_icons += [(gpu_drain if n.status == 'drain' else (gpu_down if n.status == 'down' else (gpu_pendr if n.reserved == 'pending' else gpu_avail)), None)] * (n.n_gpus - occs)
            
            joblet_icons = [(ji[0] + (' ' if i != len(joblet_icons)-1 else ''), ji[1]) for i, ji in enumerate(joblet_icons)]

            jobsplit = [""]
            count = 0
            for ic, c in joblet_icons:
                for i in ic:
                    if count == gpu_box_chars:
                        jobsplit.append("")
                        count = 0
                    jobsplit[-1] += stylefn(c, i) if c is not None else i
                    count += 1

            for i,l in enumerate(jobsplit):
                RetScope.return_string += f'{_format_to(n.name if i == 0 else "", gpu_name_chars, "right")}{"(" if n.reserved == "yes" and i == 0 else " "}{l}{")" if n.reserved == "yes" and i == (len(jobsplit) - 1) else ""}\n'

        # verify maintenance status
        onmain = False
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
        cust_print(''.join([' ['+ gpu_occ + 'run', gpu_paused + 'hld', gpu_drain + 'drn', gpu_pendr + 'pnd', gpu_down + 'dwn', '()res]']))
        gpuc = 'RED'
        if infrastructure.gpu_limit_pu > 3:
            gpuc = 'YELLOW'
        if infrastructure.gpu_limit_pu > 6:
            gpuc = 'GREEN'
        cust_print(' '.join(["      gpu:", stylefn(gpuc,("%2d" % infrastructure.gpu_limit_pu) if not pd.isna(infrastructure.gpu_limit_pu) else " ∞"), " grp:", stylefn(gpuc,"%2d/%s") % (total_jobs_prod, ("%2d" % infrastructure.gpu_limit_grp) if not pd.isna(infrastructure.gpu_limit_grp) else " ∞")]))
        cust_print(' '.join(["     Sgpu:", stylefn('CYAN',("%2d" % infrastructure.gpu_limit_stu) if not pd.isna(infrastructure.gpu_limit_stu) else " ∞"), "Sgrp:", stylefn('CYAN',"%2d/%s") % (total_jobs_stud, ("%2d" % infrastructure.gpu_limit_stugrp) if not pd.isna(infrastructure.gpu_limit_stugrp) else " ∞")]))

        # print user list
        for u, c in user_styles.items():
            if c == 'CYAN' or c == 'BG_CYAN':
                continue
            cust_print(f" {stylefn(c, gpu_occ)} {stylefn('CYAN', u) if any(['stu' in j.partition for j in jobs if j.user == u]) else u} ({sum([sum([jj.n_gpus for jj in j.joblets if jj.node is not None]) for j in jobs if j.user == u])})")
        cust_print(f" {stylefn('CYAN', gpu_occ)} {stylefn('CYAN', 'students')}")
        cust_print(f" {stylefn('BG_CYAN', gpu_occ)} {stylefn('BG_CYAN', 'cvcs')}")
        
    else: # if infrastrcture_down
        # print emergency screen
        cust_print('  ◀ INFRASTRUCTURE IS DOWN ▶  ', 'BG_RED')
        cust_print(random.choice([flip, chunga, ogre]), 'GREEN')

    return RetScope.return_string

if __name__ == '__main__':
    import sys
    from readers.slurmreader import read_infrastructure
    from readers.slurmreader import read_jobs
    infr = read_infrastructure()
    jobs, _ = read_jobs()
    if len(sys.argv) > 1 and sys.argv[1] == 'work':
        print(view_viz_gpu(infr, jobs, work=True))
        print(view_viz_ram(infr, jobs, work=True))
    else:
        print(view_viz_gpu(infr, jobs))
        print(view_viz_ram(infr, jobs))
