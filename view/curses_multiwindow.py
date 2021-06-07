import os
from importlib import reload
import time
import curses
import threading

a_filter_values = [None, 'me', 'prod', 'stud']

class Singleton:
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Singleton.__instance == None:
            Singleton()
        return Singleton.__instance
    
    def __init__(self):
        """ Virtually private constructor. """
        if Singleton.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Singleton.__instance = self
        self.voff = 0
        self.mouse_state = {}

        self.nocc = ""
        self.rens = ""
        
        self.fetch_subscriber = []
        
    def fetch(self, a_filter):

        for f in self.fetch_subscriber:
            f(a_filter_values[a_filter])


    def add_button(self, y, x, width, action):
            if y not in self.mouse_state:
                self.mouse_state[y] = {}
            if type(width) == str:
                width = len(width)
            for j in range(x, x+width):
                self.mouse_state[y][j] = action

        
class Buffer(object):

    def __init__(self, window, lines, screen):
        self.window = window
        self.lines = lines
        self.buffer = [""]
        self.screen = screen

    def write(self, text):
        lines = text.split("\n")
        self.buffer[-1] += lines[0]
        self.buffer.extend(lines[1:])
        self.refresh()

    def writeln(self, text):
        self.write(text + "\n")

    def input(self, text = ""):
        return self._input(text, lambda: self.window.getstr().decode('utf-8'))

    def input_chr(self, text = ""):
        return self._input(text, lambda: chr(self.window.getch()))

    def _input(self, text, get_input):
        self.write(text)
        input = get_input()
        self.writeln(input)
        return input

    def refresh(self,voff=0,usevoff=False):
        self.window.erase()
        off = max(0,((self.lines-2) - len(self.buffer)) // 2)
        if usevoff and voff < 0:
            Singleton.getInstance().voff = 0
        elif usevoff and voff > len(self.buffer) - self.lines + 2:
            Singleton.getInstance().voff = len(self.buffer) - self.lines + 2
        
        voff = max(min(voff, len(self.buffer) - self.lines + 2), 0)
        for nr, line in enumerate(self.buffer[voff:voff+self.lines-2]):#self.buffer[-self.lines+2:]):
            lastcol = 2
            xacc = 1
            
            for chunk in line.split('<*'):
                if ':*>' in chunk:
                    
                    color = int(chunk[0:chunk.index('~')])
                    chunk_segments = chunk[chunk.index('~')+1:].split(':*>')
                    self.window.addstr(nr + off + 1, xacc, chunk_segments[0], curses.color_pair(color) | (curses.A_REVERSE if color > 9 else 0))
                    xacc += len(chunk_segments[0])
                    
                    if len(chunk_segments[1]) > 0:
                        self.window.addstr(nr + off + 1, xacc, chunk_segments[1])
                        xacc += len(chunk_segments[1])
                else:
                    self.window.addstr(nr + off + 1, xacc, chunk)
                    xacc += len(chunk)
        if len(self.buffer) > self.lines - 2:
            self.screen.addstr(self.lines-2, Singleton.getInstance().xoffset + 30, ' ▼ SCROLL ▲ ' , curses.color_pair(2) | curses.A_REVERSE)
            Singleton.getInstance().add_button(self.lines-2, Singleton.getInstance().xoffset + 31, 'D', ord('s'))
            Singleton.getInstance().add_button(self.lines-2, Singleton.getInstance().xoffset + 40, 'U', ord('w'))
        self.window.border()
        self.window.noutrefresh()

def process_mouse():
    try:
        _, x, y, _, bstate = curses.getmouse()

        if bstate & curses.BUTTON1_RELEASED != 0:
            ms = Singleton.getInstance().mouse_state
            if y in ms and x in ms[y]:
                return True, ms[y][x]
        return False, -1
    except:
        return False, -1


def main(stdscr):
    # Clear screen
    stdscr.clear()
    curses.noecho()
    curses.curs_set(0)
    stdscr.timeout(2000)
    _ = curses.mousemask(1)

    
    curses.use_default_colors()
    # colors
    curses.init_pair(1, 3, 0)
    # curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, -1, -1)
    # curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    curses.init_pair(3, 1, -1)
    # curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, 3, -1)
    # curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, 2, -1)
    # curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, 5, -1)
    # curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, 4, -1)
    # curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(8, 6, -1)
    # curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    curses.init_pair(10, 3, -1)
    # curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(11, 3, -1)
    # curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(12, 3, -1)
    # curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(13, 5, -1)
    # curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_MAGENTA)

    # status
    k = -1
    refreshtime = time.time() - 60
    lastconf = None
    a_filter = 0
    outdated = True
    Singleton.getInstance().fetch(a_filter)

    def theres_changelog():
        # if not os.path.exists('/nas/softechict-nas-2/mboschini/cool_scripts/nodeocc_ii_changelog/%s.txt' % version):
        #     return False
        # if not os.path.exists(os.path.expanduser('~') + '/.nodeocc_ii/last_clog.txt'):
        #     return True
        # with open(os.path.expanduser('~') + '/.nodeocc_ii/last_clog.txt') as f:
        #     lastver = f.read().strip()
        # if lastver != version:
        #     return True
        # else:
        #     return False
        return False

    # def get_changelog():
    #     return '/nas/softechict-nas-2/mboschini/cool_scripts/nodeocc_ii_changelog/%s.txt' % version

    # def save_changelog():
    #     os.makedirs(os.path.expanduser('~') + '/.nodeocc_ii/', exist_ok=True)
    #     with open(os.path.expanduser('~') + '/.nodeocc_ii/last_clog.txt', 'w') as f:
    #         f.write(version)

    # def save_version(vv):
    #     os.makedirs(os.path.expanduser('~') + '/.nodeocc_ii/', exist_ok=True)
    #     with open(os.path.expanduser('~') + '/.nodeocc_ii/last_ver_not.txt', 'w') as f:
    #         f.write(vv)

    def theres_newversion():
        # if os.path.exists('/nas/softechict-nas-2/mboschini/cool_scripts/nodeocc_ii_last_release.txt'):
        #     with open('/nas/softechict-nas-2/mboschini/cool_scripts/nodeocc_ii_last_release.txt') as f:
        #         lastver = f.read().strip()
        #     if version < lastver:
        #         if os.path.exists(os.path.expanduser('~') + '/.nodeocc_ii/last_ver_not.txt'):
        #             with open(os.path.expanduser('~') + '/.nodeocc_ii/last_ver_not.txt') as f:
        #                 lastver_n = f.read().strip()
        #             if lastver_n == lastver:
        #                 return False
        #         return lastver
        # return False
        return False

    if theres_changelog():
        with open(get_changelog()) as f:
            chlog = f.readlines()
        while k == -1:
            stdscr.refresh()
            for i, line in enumerate(chlog):
                stdscr.addstr(i, 0, line)
            try:
                k = stdscr.getch()
            except:
                k = ord('z')
        save_changelog()

    k = -1
    vv = theres_newversion()
    if vv != False:
        while k == -1:
            stdscr.refresh()
            stdscr.addstr(1, 0, 'NEW VERSION AVAILABLE')
            stdscr.addstr(2, 0, 'nodeocc_ii v%s' % vv)
            stdscr.addstr(4, 0, 'PRESS ANY KEY TO CONTINUE...')
            try:
                k = stdscr.getch()
            except:
                k = ord('z')
        save_version(vv)

    stdscr.clear()
    k = -1
    s_lines,s_columns = stdscr.getmaxyx()
    while k != ord('q') and k != 'q':
        
        valid_mouse = False
        if k == curses.KEY_MOUSE:
            valid_mouse, ck = process_mouse()
            if valid_mouse:
                k = ck
                
            if k == ord('q'): break


        Singleton.getInstance().mouse_state = {}

        lines,columns = stdscr.getmaxyx()
        if k == ord('y'):
            stdscr.clear()

        if columns < 104:
            try:
                k = stdscr.getch()
            except:
                k = ord('z')
            stdscr.addstr(1, 1, "MINIMUM TERM. WIDTH")
            stdscr.addstr(2, 1, "REQUIRED: 104")
            stdscr.addstr(3, 1, "CURRENT: " + str(columns))
            stdscr.refresh()
            continue

        # process input
        # RIGHT
        if k == ord('d') or k == 261: 
            a_filter = (a_filter + 1) % len(a_filter_values)
            Singleton.getInstance().voff = 0
            outdated = True
        # LEFT
        elif k == ord('a') or k == 260:
            a_filter = (a_filter + 3) % len(a_filter_values)
            Singleton.getInstance().voff = 0
            outdated = True
        elif valid_mouse and type(k) == str and k.startswith('AF_'):
            a_filter = int(k.split('AF_')[1])
        # DOWN
        elif k == ord('s') or k == 258:
            Singleton.getInstance().voff += 1
        # UP
        elif k == ord('w') or k == 259:
            Singleton.getInstance().voff -= 1
        outdated = outdated or time.time() - refreshtime > 2
        
        xoffset = (columns - 104) //2
        Singleton.getInstance().xoffset = xoffset

        # fetch state in separate thread
        if outdated:
            threading.Thread(target=Singleton.getInstance().fetch, args=(a_filter,)).start()
            outdated = False
            refreshtime = time.time()
            

        # update state (recompute lines for safety)
        if lines != s_lines or columns != s_columns:
            stdscr.clear()
            s_columns = columns
            s_lines = lines
            
        half_width = int(columns / 2)
        stdscr.refresh()

        left_window = curses.newwin(lines-1, 72, 0, xoffset)
        left_buffer = Buffer(left_window, lines, stdscr)
        right_window = curses.newwin(lines-1,31, 0, xoffset + 73)
        right_buffer = Buffer(right_window, lines, stdscr)
            
            
        left_buffer.write(Singleton.getInstance().rens)
        right_buffer.write(Singleton.getInstance().nocc)
        right_buffer.refresh()
        left_buffer.refresh(Singleton.getInstance().voff, True)
        lastconf = (lines,columns)
        
        # render menu
        stdscr.addstr(lines-1,xoffset + 1 + 0, '◀')
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 0, '◀', ord('a'))
        stdscr.addstr(lines-1,xoffset + 1 + 2, 'ALL', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[a_filter] == None else 0))

        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 2, 'ALL', 'AF_0')

        stdscr.addstr(lines-1,xoffset + 1 + 6, 'ME', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[a_filter] == 'me' else 0))
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 6, 'ME', 'AF_1')
        stdscr.addstr(lines-1,xoffset + 1 + 9, 'PROD', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[a_filter] == 'prod' else 0))
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 9, 'PROD', 'AF_2')
        stdscr.addstr(lines-1,xoffset + 1 + 14,'STUD', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[a_filter] == 'stud' else 0))
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 14,'STUD', 'AF_3')
        stdscr.addstr(lines-1,xoffset + 1 + 19, '▶')
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 19, '▶', ord('d'))
        stdscr.addstr(lines-1,xoffset + 1 + 20, ' ' * (columns - 22 - xoffset))
        
        stdscr.addstr(lines-1,xoffset + 1 + 53,'[Q:QUIT]', curses.color_pair(2))
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 53,'[Q:QUIT]', ord('q'))

        stdscr.addstr(lines-1,xoffset + 1 + 61,'[Y:REDRAW]', curses.color_pair(2))
        Singleton.getInstance().add_button(lines-1,xoffset + 1 + 61,'[Y:REDRAW]', ord('y'))
        
        signature = Singleton.getInstance().signature
        stdscr.addstr(lines-1,xoffset + 1 + min(103, columns)-1-len(signature), signature)
        

        stdscr.refresh()
        curses.doupdate()
        try:
            k = stdscr.getch()
        except:
            k = ord('z')

