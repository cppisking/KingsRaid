from __future__ import print_function

import json
import os
import re
import sys
    
# Don't change anything in this file unless you know what you're doing.
# ==================================================================================================================

file = None
button_points = {}
button_rects = {}
resolution = (1280,720)
time = 0

def do_input():
    if sys.version_info >= (3,0):
        return input()
    return raw_input()

def wait(amount):
    global time
    time = time + amount

def error(message):
    print(message)
    do_input()
    sys.exit(1)

def repeat_generator_for(fn, seconds):
    global time
    initial = time
    milliseconds = seconds * 1000

    while time - initial < milliseconds:
        fn()

def click_loc(loc, wait_milliseconds):
    global file
    global resolution
    global time

    def scale(xy):
        global resolution
        return (int(xy[0]*resolution[0]/1280), 
                int(xy[1]*resolution[1]/720))

    x, y = scale(loc)
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:1:0:{2}:{3}ScRiPtSePaRaToR{4}\n".format(
        resolution[0], resolution[1], x, y, time))

    # This is the delay between pressing the button and releasing the button.  If you set it to be too fast,
    # the device won't register a click properly.  In my experience 100ms is about as fast as you can get
    # to have all clicks properly registered.
    wait(100)
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:0:6ScRiPtSePaRaToR{2}\n".format(resolution[0], resolution[1], time))
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:0:6ScRiPtSePaRaToR{2}\n".format(resolution[0], resolution[1], time))
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:0:1ScRiPtSePaRaToR{2}\n".format(resolution[0], resolution[1], time))
    file.write("0ScRiPtSePaRaToR{0}|{1}|MSBRL:-1158647:599478ScRiPtSePaRaToR{2}\n".format(resolution[0], resolution[1], time))

    # This is the delay between finishing one click and beginning the next click.  This needs to account
    # for how fast the game can transition from one screen to the next.  For example, if you're repeatedly
    # clicking a buy button with the game not really doing anything between each click, this can be very
    # low.  On the other hand, if a click causes the game to transition from one screen to another (e.g.
    # using a portal and the game having to load into Orvel and load an entirely new area) then it should
    # be fairly high.
    wait(wait_milliseconds)

def click_button(button, wait_milliseconds):
    global button_points
    loc = button_points[button]
    return click_loc(loc, wait_milliseconds)

def click_rect(rect, wait_milliseconds, dont_click = None):
    '''Click a single rectangle, optionally *not* clicking in any one of a list of rectangles'''

    global button_rects
    coords = button_rects[rect]
    centerx = int((coords[0][0] + coords[1][0]) / 2)
    centery = int((coords[0][1] + coords[1][1]) / 2)
    return click_loc((centerx, centery), wait_milliseconds)

def click_rects(rect_list, wait_milliseconds, dont_click = None):
    '''Click a list of rectangles, one after the other with a specified delay between each click.
       By passing a list for the `dont_click` argument, the algorithm will guarantee *not* to click
       any point in the specified list of rectangles.'''
    for r in rect_list:
        click_rect(r, wait_milliseconds, dont_click=dont_click)

def prompt_user_for_int(message, default=None, min=None, max=None):
    result = None
    while True:
        print(message, end='')
        result = do_input()

        if default is not None and len(result) == 0:
            result = default
            break

        if not is_integer(result):
            print('Value is not an integer.')
            continue

        result = int(result)
        if min is not None and result < min:
            print('Invalid value.  Must be at least {0}'.format(min))
            continue

        if max is not None and result > max:
            print('Invalid value.  Must be no larger than {0}'.format(max))
            continue

        break
    return int(result)

def prompt_choices(message, choices, default=None):
    result = default
    choice_str = '/'.join(choices)
    default_str = ' (default={0})'.format(default) if default else ''

    lower_choices = [x.lower() for x in choices]

    message = '{0} ({1}){2}: '.format(message, choice_str, default_str)
    while True:
        print(message, end='')
        input = do_input()
        if len(input) == 0:
            if default is not None:
                return default
            continue

        input = input.lower()
        if input in lower_choices:
            return input

    return None

def prompt_user_yes_no(message, default=False):
    result = default
    message = "{0} (Y/N) (default={1}): ".format(message, "Y" if default else "N")
    while True:
        print(message, end='')
        input = do_input()
        if len(input) == 0:
            result = default
            break
        input = input.lower()
        if input == 'n':
            result = False
            break
        if input == 'y':
            result = True
            break
    return result

def find_nox_install():
    app_data = None
    if sys.platform == 'darwin':
        user_dir = os.path.expanduser('~')
        app_data = os.path.join(user_dir, 'Library', 'Application Support')
    elif sys.platform == 'win32':
        app_data = os.environ.get('LOCALAPPDATA', None)

    if not app_data:
        error('Could not get local app data folder.  Exiting...')

    nox_folder = os.path.join(app_data, 'Nox', 'record')
    if not os.path.exists(nox_folder):
        nox_folder = os.path.join(app_data, 'Nox App Player', 'record')

    if not os.path.exists(nox_folder):
        error('Could not find Nox installation folder.  Exiting...')

    if not os.path.exists(os.path.join(nox_folder, 'records')):
        error('Nox folder {0} does not contain a "records" file.  Exiting...'.format(nox_folder))
    return nox_folder

def is_integer(s):
    try:
        n = int(s)
        return True
    except:
        pass
 
    return False

def select_macro_interactive(json_obj):
    if len(json_obj) == 0:
        error('The records file contains no macros.  Record a dummy macro in Nox and try again.')
    index = 0
    keys = list(json_obj.keys())
    if len(json_obj) > 1:
        print()
        for (n,key) in enumerate(keys):
            print('{0}) {1}'.format(n+1, json_obj[key]['name']))
        value = prompt_user_for_int('Enter the macro you wish to overwrite: ', min=1, max=len(json_obj))
        index = value - 1
    key = keys[index]
    return key

def select_resolution_interactive():
    global resolution
    while True:
        print('Enter your emulator resolution (or press Enter for 1280x720): ', end = '')
        res = do_input().strip()
        if len(res) == 0:
            resolution = (1280, 720)
            return
        else:
            match = re.fullmatch(r'(\d+)x(\d+)', res)
            if match is not None and is_integer(match[1]) and is_integer(match[2]):
                resolution = (int(match[1]), int(match[2]))
                return

def get_nox_macro_interactive():
    nox_folder = find_nox_install()
    records_file = os.path.join(nox_folder, 'records')
    fp = open(records_file, 'r')
    json_obj = json.load(fp)
    macro_key = select_macro_interactive(json_obj)
    macro_file = os.path.join(nox_folder, macro_key)

    name = json_obj[macro_key]['name']

    fp.close()
    return (name, macro_file)

def initialize(points, rects):
    global button_points
    global button_rects
    select_resolution_interactive()

    button_points = points
    button_rects = rects

def load_macro_file():
    global file
    name = None
    file_path = None
    if len(sys.argv) < 2:
        (name, file_path) = get_nox_macro_interactive()
    else:
        file_path = sys.argv[1]

    file = open(file_path, 'w')
    return (name, file_path)

def close():
    global file
    file.close()
