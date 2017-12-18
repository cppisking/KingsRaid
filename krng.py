import sys

# If your Nox instance runs at something other than 1280x720 resolution, change this to whatever
# it is.
resolution = (1280,720)

# Don't change anything in this section unless you know what you're doing.
# ================================================================================================
time = 0
file = open(sys.argv[1], "w")

def coord(x, y):
    global resolution
    return (int(x*resolution[0]/1280.0), 
            int(y*resolution[1]/720.0))

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

    # This is the delay between pressing the button and releasing the button.  If you
    # set it to be too fast, the device won't register a click properly.  In my
    # experience 100ms is about as fast as you can get to have all clicks properly
    # registered.
    wait(100)
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:0:6ScRiPtSePaRaToR{2}\n".format(
        resolution[0], resolution[1], time))
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:0:6ScRiPtSePaRaToR{2}\n".format(
        resolution[0], resolution[1], time))
    file.write("0ScRiPtSePaRaToR{0}|{1}|MULTI:0:1ScRiPtSePaRaToR{2}\n".format(
        resolution[0], resolution[1], time))
    file.write("0ScRiPtSePaRaToR{0}|{1}|MSBRL:-1158647:599478ScRiPtSePaRaToR{2}\n".format(
        resolution[0], resolution[1], time))

    # This is the delay between finishing one click and beginning the next click.
    # This needs to account for how fast the game can transition from one screen
    # to the next.  For example, if you're repeatedly clicking a buy button with the
    # game not really doing anything between each click, this can be very low.  On
    # the other hand, if a click causes the game to transition from one screen to
    # another (e.g. using a portal and the game having to load into Orvel and load an
    # entirely new area) then it should be fairly high because you don't want the next
    # click to happen while the game is still transitioning.
    wait(wait_milliseconds)
    

# The generated macro assumes you are on the Buy screen, Tier 3 is already selected,
# and an item is highlighted.
wait(500)

# ===========================================================================================

# You can edit the 3rd argument to each function below to adjust timings based on the speed
# of your machine.  If your machine is very fast and Nox runs smoothly, you can lower some
# of the numbers.  If you find that clicks are getting missed or registered at the wrong
# time, you can raise some of the numbers.  You want them to be as low as possible while
# still registering every click.  This will produce the fastest macro.

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

# Re-enter the shop.  Delay should be a bit higher here since there's an animated
# transition from Orvel to the forge screen that takes a little extra time.
click(file, enter_forge_btn, 2000)

# Click Use Shop button
click(file, use_shop_btn, 1000)

# At this point we're back where we started and the macro can loop.

file.close()
