'''
Helper functions for nicer terminal formatting using escape sequences.
'''

ANSI_ESCAPE = {
    'white': '',
    'purple': '\033[95m',
    'blue': '\033[94m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'end': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m'
}


def fmt(text, color='white', bold=False, underline=False):
    if bold:
        text = ANSI_ESCAPE['bold'] + text

    if underline:
        text = ANSI_ESCAPE['underline'] + text

    return ANSI_ESCAPE[color] + text + ANSI_ESCAPE['end']


def _ansi_demo():
    print(fmt('purple', color='purple'))
    print(fmt('blue', color='blue'))
    print(fmt('green', color='green'))
    print(fmt('yellow', color='yellow'))
    print(fmt('red', color='red'))
    print(fmt('bold', bold=True))
    print(fmt('underline', underline=True))
