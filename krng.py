from __future__ import print_function

import json
import os
import sys

import nox

# These coordinate initial values are relative to a 1280x720 resolution, regardless of what
# your actual resolution is.
points = {
    'buy': (965, 652),
    'buy_confirm': (787, 520),
    'exit': (152, 32),
    'inventory' : (178, 644),
    'grind' : (839,629),
    'grind_all' : (730,629),
    'grind_2' : (732,589),
    'grind_confirm' : (738,531),
    'dismiss_results' : (738,531),
    'enter_forge' : (641,525),
    'use_shop' : (636,561),
    'abandon_raid' : (848, 590),
    'start_raid' : (1183, 624),
    'stam_potion_select' : (641,379),
    'stam_potion_confirm' : (635,546),
    'confirm_insufficient_members' : (635,546)
}

rects = {
    'exit_raid' : ((1171, 596), (1233, 654)),
    'abandon_raid' : ((766, 589), (883, 641)),
    'bid_raid' : ((905, 589), (1025, 641)),
    'start_raid' : ((999, 621), (1182, 671)),
    'raid_hero_lineup' : ((125, 182), (1151, 404)),
    'raid_hero_select' : ((81, 483), (390, 683)),
    'claim_reward' : ((766, 589), (1025, 641)),
    'raid_info' : ((853, 615), (977, 680)),
    'stam_potion' : ((593,292), (686, 387)),
    'stam_potion_raid_5' : ((593,292), (675, 387)),
}

nox.initialize(points, rects)

def gen_grindhouse():
    # The generated macro assumes you are on the Buy screen, Tier 3 is already selected, and an item is
    # highlighted.
    print()
    items_to_buy = nox.prompt_user_for_int(
        "How many items should be purchased each cycle?\n"
        "If you don't have at least this much inventory space the macro will de-sync.\n"
        "Number of items to purchase: ")

    # Buy 300 items
    for i in range(0, items_to_buy):
        nox.click_button('buy', 275)
        nox.click_button('buy_confirm', 275)

    # Exit twice (to Orvel map)
    nox.click_button('exit', 1000)
    nox.click_button('exit', 1000)

    # Open inventory
    nox.click_button('inventory', 1000)

    # Grind
    nox.click_button('grind', 1000)

    # Grind all
    nox.click_button('grind_all', 1000)

    # Click the Grind button on the window that pops up
    nox.click_button('grind_2', 1000)

    # Confirmation
    nox.click_button('grind_confirm', 1000)

    # Click on the screen to get rid of the results
    nox.click_button('dismiss_results', 1000)

    # Exit back to Orvel world map
    nox.click_button('exit', 1000)

    # Re-enter the shop.  Delay set to 2000 here since there's an animated transition
    # that takes a little extra time
    nox.click_button('enter_forge', 2000)

    # Click Use Shop button
    nox.click_button('use_shop', 1000)

def gen_raid_experimental():
    # This macro can be started any time during a raid cycle.  You can be on the party
    # room screen, in the raid, on the loot screen, etc.  But you must *at least* have
    # your heroes ready on deck.

    # Wait for 5 seconds here to give the leader time to click start
    nox.click_button('start_raid', 10000)

    # The stamina potion window may or may not be up now.  If it is we want to click the
    # potion, but if it's not we must *not* click the potion because that would remove
    # hero 5 from the roster.  But we cannot guarantee what state the click sequence is
    # in when we get here.  For example, we may have just returned to the lobby and the
    # next click is going to be the stamina potion use.  That would remove hero 5 (if it
    # is ours) from the roster, so we have to be clever.

    # What we do here is click the "start raid" button *twice* with a very low delay.
    # 
    # - If the leader has started battle, this does nothing.
    # - If the stamina window was already up, this does nothing.
    # - If we were in the "prepared" state, this un-readies us and re-readies us.
    #   When we loop back around, we will un-ready for 10s, and then execute both of these
    #   again which will ready -> un-ready and so every other cycle we should be ready.

    # - If we arrive at the lobby in this state and we need a stamina potion, this will pop
    #   up the stamina potion window and the next click does nothing.  If we don't need a
    #   stamina potion, these two clicks will ready us and then un-ready us so that we prepare
    #   on the loop-around.
    nox.click_button('start_raid', 250)

    # - If we arrive at the lobby in this state and we need a stamina potion, this will pop
    #   up the stamina potion window.  If we don't need a stamina potion the leader will have
    #   a very short window 
    nox.click_button('start_raid', 250)

    # Note that it is still possible for the game to return back to the battle screen right
    # here, but since there are only 300ms between this click and the previous, it is much
    # less likely than when there are 5s.
    nox.click_button('stam_potion_select', 1000)
    nox.click_button('stam_potion_confirm', 1000)
    nox.click_button('abandon_raid', 1000)
    
def gen_raid():
    nox.click_button('start_raid', 5000)
    nox.click_button('confirm_insufficient_members', 500)
    nox.click_button('abandon_raid', 5000)

def gen_natural_stamina_farm():
    nox.click_loc((935, 175), 500)
    nox.click_loc((1201, 509), 500)
    nox.click_loc((490, 410), 500)
    nox.click_loc((1055, 650), 500)

macro_generators = [
    ("NPC Gear Purchasing and Grinding", gen_grindhouse),
    # ("Natural Stamina Regen Raid Farming (Non-Leader) (Experimental!!!)", gen_raid_experimental),
    ("Raid Farming (Traditional)", gen_raid),
    ("Story Repeat (No Stamina Potion / Natural Stamina Regen)", gen_natural_stamina_farm)
    ]

print()
for (n,(desc,fn)) in enumerate(macro_generators):
    print('{0}) {1}'.format(n+1, desc))

macro_number = nox.prompt_user_for_int('Enter the macro you wish to generate: ',
                                       min=1, max=len(macro_generators))

(macro_name, file_path) = nox.load_macro_file()

(desc, fn) = macro_generators[macro_number - 1]

print()
if macro_name:
    print('Destination Macro Name: {0}'.format(macro_name))
print('Destination File: {0}'.format(file_path))
print('Selected Macro: {0}'.format(desc))
print('Press Enter to confirm or Ctrl+C to cancel. ', end = '')
nox.do_input()

nox.wait(500)

# Generate the macro
fn()

# At this point we're back where we started and the macro can loop.
nox.close()

print('File {0} successfully written.'.format(file_path))
