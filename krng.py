from __future__ import print_function

import json
import os
import sys

# If your Nox instance runs at something other than 1280x720 resolution, change this to whatever
# it is.
resolution = (1280,720)

def do_input():
    if sys.version_info >= (3,0):
        return input()
    return raw_input()

# Don't change anything in this section unless you know what you're doing.
# ==================================================================================================================
def find_nox_install():
    app_data = os.environ.get('LOCALAPPDATA', None)
    if not app_data:
        print('Could not get local app data folder.  Exiting...')
        sys.exit(1)
    nox_folder = os.path.join(app_data, 'Nox', 'record')
    if not os.path.exists(nox_folder):
        print('Could not find Nox installation folder.  Exiting...')
        sys.exit(1)
    if not os.path.exists(os.path.join(nox_folder, 'records')):
        print('Invalid Nox installation folder.  Exiting...')
        sys.exit(1)
    return nox_folder

def is_integer(s, min, max):
    try:
        n = int(s)
        return n >= min and n <= max
    except:
        pass
 
    return False

def select_macro_interactive(json_obj):
    if len(json_obj) == 0:
        print('The file {0} contains no macros.  Record a dummy macro in Nox and try again.')
        sys.exit(1)
    index = 0
    keys = list(json_obj.keys())
    if len(json_obj) > 1:
        while True:
            for (n,key) in enumerate(keys):
                print('{0}) {1}'.format(n+1, json_obj[key]['name']))
            print('Enter the macro you wish to overwrite: ', end = '')
            value = do_input()
            if is_integer(value, 1, len(json_obj)):
                index = int(value) - 1
                break
            print('Invalid entry.  Please choose a number from 1 to {0}'.format(len(json_obj)))
    key = keys[index]
    return key


def get_nox_macro_interactive():
    nox_folder = find_nox_install()
    print('Found nox local appdata at {0}'.format(nox_folder))
    records_file = os.path.join(nox_folder, 'records')
    fp = open(records_file, 'r')
    json_obj = json.load(fp)
    macro_key = select_macro_interactive(json_obj)
    macro_file = os.path.join(nox_folder, macro_key)

    name = json_obj[macro_key]['name']

    print('The macro "{0}" ({1}) will be overwritten.  Press Enter to continue, or Ctrl+C to cancel.'.format(name, macro_file), end = '')
    do_input()

    return macro_file


time = 0

def coord(x, y):
    global resolution
    return (int(x*resolution[0]/1280), 
            int(y*resolution[1]/720))

buy_btn = coord(965,652)
buy_confirm_btn = coord(787,520)
exit_btn = coord(152, 32)
inventory_btn = coord(178, 644)
grind_btn = coord(839,629)
grind_all_btn = coord(730,629)
grind_btn_2 = coord(732,589)
grind_confirm_btn = coord(738,531)
dismiss_results = coord(738,531)
enter_forge_btn = coord(641,525)
use_shop_btn = coord(636,561)
    
def wait(amount):
    global time
    time = time + amount

def click(file, loc, wait_milliseconds):
    global resolution
    global time
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:1:0:{2}:{3}ScRiPtSePaRaToR{4}\n".format(
        resolution[0], resolution[1], loc[0], loc[1], time))

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

file_path = None
if len(sys.argv) < 2:
    file_path = get_nox_macro_interactive()
else:
    file_path = sys.argv[1]

file = open(file_path, 'w')
# The generated macro assumes you are on the Buy screen, Tier 3 is already selected, and an item is
# highlighted.
wait(500)

# ==================================================================================================================

# Buy 300 items
for i in range(0, 300):
    click(file, buy_btn, 275)
    click(file, buy_confirm_btn, 275)

# Exit twice (to Orvel map)
click(file, exit_btn, 1000)
click(file, exit_btn, 1000)

# Open inventory
click(file, inventory_btn, 1000)

# Grind
click(file, grind_btn, 1000)

# Grind all
click(file, grind_all_btn, 1000)

# Click the Grind button on the window that pops up
click(file, grind_btn_2, 1000)

# Confirmation
click(file, grind_confirm_btn, 1000)

# Click on the screen to get rid of the results
click(file, dismiss_results, 1000)

# Exit back to Orvel world map
click(file, exit_btn, 1000)

# Re-enter the shop.  Delay set to 2000 here since there's an animated transition
# that takes a little extra time
click(file, enter_forge_btn, 2000)

# Click Use Shop button
click(file, use_shop_btn, 1000)

# At this point we're back where we started and the macro can loop.

file.close()

print('File {0} successfully written.'.format(file_path))
