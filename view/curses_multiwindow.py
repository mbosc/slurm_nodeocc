import os
import time
import curses
import logging
from logging.handlers import RotatingFileHandler
import socket
from view import update_views

a_filter_values = [None, 'me', 'prod', 'stud', 'cvcs']

class Singleton:
    __instance = None
    @staticmethod 
    def getInstance(args=None):
        """ Static access method. """
        if Singleton.__instance == None:
            Singleton(args)
        if args != None:
            Singleton.__instance.args = args
        return Singleton.__instance
    
    # destructor
    def __del__(self):
        if self.args.master:
            if len([f for f in os.listdir('/nas/softechict-nas-2/mboschini/cool_scripts/new_nodeocc/') if f.endswith('.port')])>0:
                os.remove(f'/nas/softechict-nas-2/mboschini/cool_scripts/new_nodeocc/{str(self.port)}.port')
    
    def __init__(self, args=None):
        """ Virtually private constructor. """
        if Singleton.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Singleton.__instance = self
        self.voff = 0
        self.mouse_state = {}

        self.nocc = ""
        self.rens = ""
        
        self.fetch_fn = None
        self.view_mode = 'gpu'
        self.job_id_type = 'agg'
        self.args = args

        self.show_account = False
        self.show_prio = False
        self.time = 5

        self.inf = None
        self.jobs = []
        self.a_filter = 0
        
        if self.args.daemon_only:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        # set logging file
        elif self.args.debug:
            # create rotating file handler
            handler = RotatingFileHandler(os.path.expanduser('~') + '/.nodeocc_ii/log.txt', maxBytes=5*1024*1024, backupCount=2, mode='w')
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', 
                                handlers=[handler])
            
        if self.args.master:
            # check if any .port file exists    
            if len([f for f in os.listdir('/nas/softechict-nas-2/mboschini/cool_scripts/new_nodeocc/') if f.endswith('.port')]) > 0:
                raise Exception("Master already running")
            self.port = self.create_socket_as_master()
        else:
            # check if any .port file exists    
            if len([f for f in os.listdir('/nas/softechict-nas-2/mboschini/cool_scripts/new_nodeocc/') if f.endswith('.port')]) == 0:
                raise Exception("No master running")

            self.port = int([f for f in os.listdir('/nas/softechict-nas-2/mboschini/cool_scripts/new_nodeocc/') if f.endswith('.port')][0].split('.')[0])
            self.open_socket_as_slave(self.port)

    def create_socket_as_master(self):
        # create udp socket for broadcasting
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # check if kernel version
        # is 3.9 or above
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        else:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Enable broadcasting mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.sock.bind(('', 0))

        self.port = self.sock.getsockname()[1]
        self.sock.settimeout(11)
        self.log(f"Socket created as master on port {self.port}")

        # get pid of current process
        self.pid = os.getpid()

        # create file to store port
        with open(f'/nas/softechict-nas-2/mboschini/cool_scripts/new_nodeocc/{self.port}.port', "w") as f:
            f.write(str(self.pid))

        return self.port
    
    def open_socket_as_slave(self, port):
        # create udp socket for broadcasting
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # check if kernel version
        # is 3.9 or above
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        else:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #sock listen on port
        self.sock.bind(('', port))

        self.sock.settimeout(6.5)

        self.sock.setblocking(False)

        self.log(f"Socket opened on port {self.port}")

        return self.port

    def timeme(self, msg=None):
        if not hasattr(self, '_ctime'):
            self._ctime = time.time()
            if msg is not None:
                self.log(msg)
        else:
            _ntime = time.time()
            self.log(f"{msg} took {_ntime - self._ctime:.2f} seconds")
            self._ctime = _ntime

    def err(self, msg):
        if self.args.debug or self.args.daemon_only:
            logging.error(msg)

    def log(self, msg):
        if self.args.debug or self.args.daemon_only:
            logging.info(msg)
        
    async def fetch(self):
        _ctime = time.time()
        
        if self.fetch_fn is not None:
            inf, jobs = await self.fetch_fn()#a_filter_values[self.a_filter])
            self.inf = inf if inf is not None else self.inf
            self.jobs = jobs if jobs is not None else self.jobs

        _delta_t = time.time() - _ctime
        self.log(f"Fetch took {_delta_t:.2f} seconds")

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
        instance = Singleton.getInstance()
        self.window.erase()
        off = max(0,((self.lines-2) - len(self.buffer)) // 2)
        if usevoff and voff < 0:
            instance.voff = 0
        elif usevoff and voff > len(self.buffer) - self.lines + 2:
            instance.voff = len(self.buffer) - self.lines + 2
        
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
                    try:
                        self.window.addstr(nr + off + 1, xacc, chunk)
                    except Exception as e:
                        instance.err(e)
                        pass
                    xacc += len(chunk)
        if len(self.buffer) > self.lines - 2:
            self.screen.addstr(self.lines-2, instance.xoffset + instance.left_width // 2 - 6, ' ▼ SCROLL ▲ ' , curses.color_pair(2) | curses.A_REVERSE)
            instance.add_button(self.lines-2, instance.xoffset + 31, 'D', ord('s'))
            instance.add_button(self.lines-2, instance.xoffset + 40, 'U', ord('w'))
        
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

async def main(stdscr):
    # Clear screen
    instance = Singleton.getInstance()
    instance.log(f"MAIN")
    stdscr.clear()
    curses.noecho()
    curses.curs_set(0)

    stdscr.nodelay(True)
    # timedelta_refresh  = instance.time
    # stdscr.timeout(int(timedelta_refresh*1000))
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

    curses.init_pair(15, -1, 6)
    # curses.init_pair(15, curses.COLOR_WHITE, curses.COLOR_CYAN) (reversed because >9)
    # status
    k = -1

    instance.a_filter = 0
    outdated = True

    await instance.fetch()

    k = -1
    
    stdscr.clear()
    k = -1
    s_lines,s_columns = stdscr.getmaxyx()
    while k != ord('q') and k != 'q':
        await instance.fetch()

        update_views(instance, a_filter_values[instance.a_filter])

        valid_mouse = False
        if k == curses.KEY_MOUSE:
            valid_mouse, ck = process_mouse()
            if valid_mouse:
                k = ck
                
            if k == ord('q'): break


        instance.mouse_state = {}

        lines,columns = stdscr.getmaxyx()
        if k == ord('y'):
            stdscr.clear()

        totsize = 106
        if instance.show_account:
            totsize += 10
        if instance.show_prio:
            totsize += 8
        
        if columns < totsize:
            try:
                k = stdscr.getch()
            except:
                k = ord('z')
            stdscr.addstr(1, 1, "MINIMUM TERM. WIDTH")
            stdscr.addstr(2, 1, f"REQUIRED: {totsize}")
            stdscr.addstr(3, 1, "CURRENT: " + str(columns))
            stdscr.refresh()
            continue

        # process input
        # RIGHT
        if k == ord('d') or k == 261: 
            instance.a_filter = (instance.a_filter + 1) % len(a_filter_values)
            instance.voff = 0
            outdated = True
        # LEFT
        elif k == ord('a') or k == 260:
            instance.a_filter = (instance.a_filter + (len(a_filter_values)-1)) % len(a_filter_values)
            instance.voff = 0
            outdated = True
        elif valid_mouse and type(k) == str and k.startswith('AF_'):
            instance.a_filter = int(k.split('AF_')[1])
        # DOWN
        elif k == ord('s') or k == 258:
            instance.voff += 1
        # UP
        elif k == ord('w') or k == 259:
            instance.voff -= 1
        outdated = outdated #or time.time() - refreshtime > timedelta_refresh

        if k == ord('g'):
            instance.view_mode = "gpu" if instance.view_mode == "ram" else "ram"
        if k == ord('j'):
            instance.job_id_type = "true" if instance.job_id_type == "agg" else "agg"
        
        if k == ord('t'):
            instance.show_account = not instance.show_account
        if k == ord('p'):
            instance.show_prio = not instance.show_prio
        if k == ord('h'):
            if instance.time == 2:
                instance.time = 5
            elif instance.time == 5:
                instance.time = 10
            elif instance.time == 10:
                instance.time = 20
            elif instance.time == 20:
                instance.time = 2
            # stdscr.timeout(int(instance.time*1000))

        xoffset = 0#(columns - 104) //2
        instance.xoffset = xoffset

        # await instance.fetch()
            
        # update state (recompute lines for safety)
        if lines != s_lines or columns != s_columns:
            stdscr.clear()
            s_columns = columns
            s_lines = lines
            
        stdscr.refresh()


        left_width = columns - 33 #72
        instance.left_width = left_width
        left_window = curses.newwin(lines-1, left_width, 0, xoffset)
        left_buffer = Buffer(left_window, lines, stdscr)
        right_window = curses.newwin(lines-1,31, 0, xoffset + left_width + 1)
        right_buffer = Buffer(right_window, lines, stdscr)
            
            
        left_buffer.write(instance.rens)
        right_buffer.write(instance.nocc)
        right_buffer.refresh()
        left_buffer.refresh(instance.voff, True)
        lastconf = (lines,columns)
        
        # render menu
        stdscr.addstr(lines-1,xoffset + 1 + 0, '◀')
        instance.add_button(lines-1,xoffset + 1 + 0, '◀', ord('a'))
        stdscr.addstr(lines-1,xoffset + 1 + 2, 'ALL', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[instance.a_filter] == None else 0))

        instance.add_button(lines-1,xoffset + 1 + 2, 'ALL', 'AF_0')

        stdscr.addstr(lines-1,xoffset + 1 + 6, 'ME', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[instance.a_filter] == 'me' else 0))
        instance.add_button(lines-1,xoffset + 1 + 6, 'ME', 'AF_1')
        stdscr.addstr(lines-1,xoffset + 1 + 9, 'PROD', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[instance.a_filter] == 'prod' else 0))
        instance.add_button(lines-1,xoffset + 1 + 9, 'PROD', 'AF_2')
        stdscr.addstr(lines-1,xoffset + 1 + 14,'STUD', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[instance.a_filter] == 'stud' else 0))
        instance.add_button(lines-1,xoffset + 1 + 14,'STUD', 'AF_3')
        stdscr.addstr(lines-1,xoffset + 1 + 19,'CVCS', curses.color_pair(2) | (curses.A_REVERSE if a_filter_values[instance.a_filter] == 'cvcs' else 0))
        instance.add_button(lines-1,xoffset + 1 + 19,'CVCS', 'AF_4')

        stdscr.addstr(lines-1,xoffset + 1 + 24, '▶')
        instance.add_button(lines-1,xoffset + 1 + 24, '▶', ord('d'))
        stdscr.addstr(lines-1,xoffset + 1 + 25, ' ' * (columns - 27 - xoffset))

        # stdscr.addstr(lines-1,xoffset + 1 + 19, '▶')
        # instance.add_button(lines-1,xoffset + 1 + 19, '▶', ord('d'))
        # stdscr.addstr(lines-1,xoffset + 1 + 20, ' ' * (columns - 22 - xoffset))

        
        stdscr.addstr(lines-1,left_width - 18,'[Q:QUIT]', curses.color_pair(2))
        instance.add_button(lines-1,left_width - 18,'[Q:QUIT]', ord('q')) #53

        stdscr.addstr(lines-1,left_width - 18 + 8,'[Y:REDRAW]', curses.color_pair(2))
        instance.add_button(lines-1,left_width - 18 + 8,'[Y:REDRAW]', ord('y'))

        stdscr.addstr(0, columns - 12, '[G:' , curses.color_pair(2))
        stdscr.addstr(0, columns - 9, 'GPU' , curses.color_pair(2) | (curses.A_REVERSE if instance.view_mode == 'gpu' else 0))
        stdscr.addstr(0, columns - 9 + 3, 'RAM' , curses.color_pair(2) | (curses.A_REVERSE if instance.view_mode == 'ram' else 0))
        stdscr.addstr(0, columns - 9 + 6, ']' , curses.color_pair(2))
        instance.add_button(0,columns - 12,'[G:GPURAM]', ord('g'))

        stdscr.addstr(lines-1, xoffset + 25 + 2, '[J:' , curses.color_pair(2))
        stdscr.addstr(lines-1, xoffset + 25 + 2+3, 'AGG' , curses.color_pair(2) | (curses.A_REVERSE if instance.job_id_type == 'agg' else 0))
        stdscr.addstr(lines-1, xoffset + 25 + 2+3+3, 'TRUE' , curses.color_pair(2) | (curses.A_REVERSE if instance.job_id_type == 'true' else 0))
        stdscr.addstr(lines-1, xoffset + 25 + 2+3+3+4, ']' , curses.color_pair(2))
        instance.add_button(lines-1,xoffset+25+2,'[J:AGGTRUE]', ord('j'))

        stdscr.addstr(lines-1, xoffset + 37 + 2, '[P:' , curses.color_pair(2))
        stdscr.addstr(lines-1, xoffset + 37 + 2+3, 'PRIORITY' , curses.color_pair(2) | (curses.A_REVERSE if instance.show_prio else 0))
        stdscr.addstr(lines-1, xoffset + 37 + 2+3+8, ']' , curses.color_pair(2))
        instance.add_button(lines-1,xoffset+37+2,'[P:PRIORITY]', ord('p'))

        stdscr.addstr(lines-1, xoffset + 50 + 2, '[T:' , curses.color_pair(2))
        stdscr.addstr(lines-1, xoffset + 50 + 2+3, 'ACCOUNT' , curses.color_pair(2) | (curses.A_REVERSE if instance.show_account else 0))
        stdscr.addstr(lines-1, xoffset + 50 + 2+3+7, ']' , curses.color_pair(2))
        instance.add_button(lines-1,xoffset+50+2,'[T:ACCOUNT]', ord('t'))

        stdscr.addstr(lines-1, xoffset + 62 + 2, '[H:' , curses.color_pair(2))
        stdscr.addstr(lines-1, xoffset + 62 + 2+3, '2' , curses.color_pair(2) | (curses.A_REVERSE if instance.time==2 else 0))
        stdscr.addstr(lines-1, xoffset + 62 + 2+3+1, '5' , curses.color_pair(2) | (curses.A_REVERSE if instance.time==5 else 0))
        stdscr.addstr(lines-1, xoffset + 62 + 2+3+2, '10' , curses.color_pair(2) | (curses.A_REVERSE if instance.time==10 else 0))
        stdscr.addstr(lines-1, xoffset + 62 + 2+3+4, '20' , curses.color_pair(2) | (curses.A_REVERSE if instance.time==20 else 0))
        stdscr.addstr(lines-1, xoffset + 62 + 2+3+6, 's]' , curses.color_pair(2))
        instance.add_button(lines-1,xoffset+62+2+3+6,'[H:251020s]', ord('h'))

        signature = instance.signature
        stdscr.addstr(lines-1,columns-2-len(signature), signature)
        
        stdscr.refresh()
        curses.doupdate()
        try:
            k = stdscr.getch()
        except:
            k = ord('z')

    
