def _format_to(st, width, dir='left'):
        ts = str(st)[:width]
        if dir == 'left':
            return ts + ' ' * (width - len(ts))
        else:
            return ' ' * (width - len(ts)) + ts

def cmdstyle(color, string):
    """
    style formatting function for unix terminals
    """
    strings = string.split('\n')
    styles = {
        'RED' : lambda x: '\033[31m' + str(x) + '\033[0m',
        'YELLOW' : lambda x: '\033[33m' + str(x) + '\033[0m',
        'GREEN' : lambda x: '\033[32m' + str(x) + '\033[0m',
        'MAGENTA' : lambda x: '\033[35m' + str(x) + '\033[0m',
        'BLUE' : lambda x: '\033[34m' + str(x) + '\033[0m',

        'LRED' : lambda x: '\033[91m' + str(x) + '\033[0m',
        'LYELLOW' : lambda x: '\033[93m' + str(x) + '\033[0m',
        'LGREEN' : lambda x: '\033[92m' + str(x) + '\033[0m',
        'LMAGENTA' : lambda x: '\033[95m' + str(x) + '\033[0m',
        'LBLUE' : lambda x: '\033[94m' + str(x) + '\033[0m',
        'LCYAN' : lambda x: '\033[96m' + str(x) + '\033[0m',
        'LWHITE' : lambda x: '\033[97m' + str(x) + '\033[0m',

        'CYAN' : lambda x: '\033[36m' + str(x) + '\033[0m',
        'BG_CYAN': lambda x: '\033[33m' + str(x) + '\033[0m',
        'WHITE' : lambda x: '\033[37m' + str(x) + '\033[0m',

        'BG_RED': lambda x: '\033[41m\033[37m' + str(x) + '\033[0m',
        'BG_GREEN': lambda x: '\033[42m\033[37m' + str(x) + '\033[0m',
        'BG_YELLOW': lambda x: '\033[43m' + str(x) + '\033[0m',
        'BG_MAGENTA': lambda x: '\033[45m\033[37m' + str(x) + '\033[0m'

    }
    return '\n'.join([styles[color](x) for x in strings])

def crsstyler(color, string):
    """
    custom style formatting function for curses applications
    """
    strings = string.split('\n')
    styles = {
        'RED' : lambda x: '<*3~' + str(x) + ':*>',
        'YELLOW' : lambda x: '<*4~' + str(x) + ':*>',
        'GREEN' : lambda x: '<*5~' + str(x) + ':*>',
        'MAGENTA' : lambda x: '<*6~' + str(x) + ':*>',
        'BLUE' : lambda x: '<*7~' + str(x) + ':*>',

        'LRED' : str,
        'LYELLOW' : str,
        'LGREEN' : str,
        'LMAGENTA' : str,
        'LBLUE' : str,
        'LCYAN' : str,
        'LWHITE' : str,
        'LBG_CYAN' : str,

        'CYAN' : lambda x: '<*8~' + str(x) + ':*>',
        'BG_CYAN': lambda x: '<*15~' + str(x) + ':*>',
        'WHITE' : lambda x: '<*2~' + str(x) + ':*>',

        'BG_RED':       lambda x: '<*10~' + str(x) + ':*>',
        'BG_GREEN':     lambda x: '<*11~' + str(x) + ':*>',
        'BG_YELLOW':    lambda x: '<*12~' + str(x) + ':*>',
        'BG_MAGENTA':   lambda x: '<*13~' + str(x) + ':*>'
    }
    return '\n'.join([styles[color](x) for x in strings])

def mockstyler(color, string):
    """
    mock style formatting function for debug purposes
    """
    return string
