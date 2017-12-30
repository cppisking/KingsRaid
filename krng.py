from __future__ import print_function

import json
import os
import sys

import nox

print('Nox Macro Generator v2.1')
print('By: cpp (Reddit: u/cpp_is_king, Discord: @cpp#0120)')
print('Paypal: cppisking@gmail.com')
print()

macro_name = None
file_path = None
desc = None

# These coordinate initial values are relative to a 1280x720 resolution, regardless of what
# your actual resolution is.
points = {
    'buy': (965, 652),
    'buy_confirm': (787, 520),
    'exit': (152, 32),
    'inventory' : (178, 644),
    'grind' : (839,629),
    'sell' : (1080,629),
    'grind_all' : (730,629),
    'grind_2' : (732,589),
    'grind_confirm' : (738,531),
    'dismiss_results' : (738,531),
    'enter_node' : (1190,629),
    'use_shop' : (636,561),
    'abandon_raid' : (848, 590),
    'start_raid' : (1183, 624),
    'start_adventure' : (1100, 660),
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

def confirm(properties = None, start_condition = None, notes = []):
    global macro_name
    global file_path
    global desc

    if properties is None:
        properties = {}

    print()
    if macro_name:
        print('Destination Macro Name: {0}'.format(macro_name))
    print('Destination File: {0}'.format(file_path))
    print('Selected Macro: {0}'.format(desc))
    if len(properties) > 0:
        print('Properties:')
        for (k,v) in properties.items():
            print('  {0}: {1}'.format(k, v))
        if start_condition is not None:
            print('  Start Condition: {0}'.format(start_condition))

        for n in notes:
            print('Note: {0}'.format(n))

    print('Press Enter to confirm or Ctrl+C to cancel. ', end = '')
    nox.do_input()

    print('************************************** WARNING *************************************************')
    print('* Please watch the macro for the first few cycles to make sure everything is working as        *\n'
          '* intended.  If you are selling or grinding gear, make sure your Sell All and Grind All screen *\n'
          '* is pre-configured with the appropriate values.  For extra security, make sure all valuable   *\n'
          '* items are locked.                                                                            *\n'
          '************************************************************************************************')

    nox.wait(500)

def grind_or_sell_all(is_grind):
    # Grind
    button = 'grind' if is_grind else 'sell'

    nox.click_button(button, 2500)

    # Grind all
    nox.click_button('grind_all', 2500)

    # Click the Grind button on the window that pops up
    nox.click_button('grind_2', 2500)

    # Confirmation
    nox.click_button('grind_confirm', 2500)

    if is_grind:
        # Click on the screen to get rid of the results
        nox.click_button('dismiss_results', 2500)

def gen_grindhouse():
    # The generated macro assumes you are on the Buy screen, Tier 3 is already selected, and an item is
    # highlighted.
    print()
    items_to_buy = nox.prompt_user_for_int(
        "How many items should be purchased each cycle?\n"
        "If you don't have at least this much inventory space the macro will de-sync.\n"
        "Number of items to purchase: ")

    print()
    buy_delay = nox.prompt_user_for_int("Enter the number of milliseconds between each click while purchasing\n"
                                        "items.  A lower number will make the macro run faster, but could cause\n"
                                        "the macro to get out of sync on slower machines.  If the macro doesn't\n"
                                        "register clicks properly while buying items, run the generator again\n"
                                        "and choose a higher number until you find what works.\n\n"
                                        "Milliseconds (Default=325): ", default=325)

    confirm(properties={'Items to buy' : items_to_buy, 'Delay' : buy_delay },
            start_condition='The macro should be started from the forge shop, with an item selected.')

    # Buy 300 items
    for i in range(0, items_to_buy):
        nox.click_button('buy', buy_delay)
        nox.click_button('buy_confirm', buy_delay)

    # Exit twice (to Orvel map)
    nox.click_button('exit', 1500)
    nox.click_button('exit', 1500)

    # Open inventory
    nox.click_button('inventory', 1500)

    grind_or_sell_all(True)

    # Exit back to Orvel world map
    nox.click_button('exit', 1500)

    # Re-enter the shop.  Delay set to 2500 here since there's an animated transition
    # that takes a little extra time
    nox.click_button('enter_node', 2500)

    # Click Use Shop button
    nox.click_button('use_shop', 1500)

def gen_raid_experimental():

    confirm()
    nox.click_button('start_raid', 10000)
    nox.click_button('stam_potion_confirm', 1000)
    nox.click_button('abandon_raid', 1000)
    
def gen_raid():
    confirm(start_condition='The macro can be started in a raid lobby or while a raid is in progress.')

    nox.click_button('start_raid', 5000)
    nox.click_button('confirm_insufficient_members', 500)
    nox.click_button('abandon_raid', 5000)
        
def gen_raid_leader():
    confirm(start_condition='The macro can be started in a raid lobby or while a raid is in progress.')

    for i in range(0, 10):
        nox.click_button('start_raid', 300)
    nox.click_button('confirm_insufficient_members', 500)
    nox.click_button('abandon_raid', 5000)

def manage_inventory(should_grind, should_sell):
    if should_grind:
        grind_or_sell_all(True)
    if should_sell:
        grind_or_sell_all(False)

def prompt_inventory_management_properties():
    choice = nox.prompt_choices(
        'Should I (G)rind All or (S)ell All?', ['G', 'S'])

    if choice.lower() == 'g':
        return (True, False)

    return (False, True)

def do_generate_inventory_management_for_adventure(should_grind, should_sell, use_potion):
    # At this point we're at the victory screen.  We need to click the Inventory button on the
    # left side.  This involves a loading screen and can take quite some time, so wait 15 seconds.
    nox.click_loc((80, 230), 15000)

    manage_inventory(should_grind, should_sell)

    # Exit back to Orvel map
    nox.click_button('exit', 3500)

    # Re-enter the map.  Since there's a loading transition, this takes a little extra time.
    nox.click_button('enter_node', 3500)

    # Prepare battle -> start adventure.
    nox.click_button('start_adventure', 3500)
    nox.click_button('start_adventure', 3500)

    # The stamina window may have popped up.  Use a potion
    if use_potion:
        nox.click_loc((688, 338), 2000)      # Stamina Potion.
        nox.click_loc((759, 558), 2000)      # Stamina Potion OK
        nox.click_button('start_adventure', 3500)
        nox.click_button('start_adventure', 3500)


def generate_inventory_management_for_adventure():
    print()

    (should_grind, should_sell) = prompt_inventory_management_properties()

    do_generate_inventory_management_for_adventure(should_grind, should_sell)

def gen_natural_stamina_farm():
    print()
    use_pot = nox.prompt_user_yes_no(
        "Should the macro automatically use a stamina potion when you run out?")

    inventory_management = nox.prompt_user_for_int(
        "Enter the frequency (in minutes) at which to manage inventory.\n"
        "To disable inventory management, press Enter without entering a value: ", min=1,
        default = -1)

    inv_management_sync = None
    properties={'Use Potion': use_pot}

    notes = []
    if inventory_management != -1:
        inv_management_sync = nox.prompt_user_for_int(
            'Enter the maximum amount of time (in whole numbers of minutes) it takes your team\n'
            'to complete a story dungeon.  (Default = 3): ', default = 3)
        (should_grind, should_sell) = prompt_inventory_management_properties()
        properties['Inventory Management Sync Time'] = '{0} minutes'.format(inv_management_sync)
        s = None
        if should_grind and should_sell:
            s = "Sell then grind"
        elif should_grind:
            s = "Grind"
        else:
            s = "Sell"
        properties['Manage Inventory'] = '{0} every {1} minutes'.format(s, inventory_management)
        notes=['When the macro is getting ready to transition to the inventory management\n'
                '      phase, it may appear the macro is stuck doing nothing on the victory screen.\n'
                '      This is intentional, and it can take up to {0} minutes before the transition\n'
                '      to the inventory screen happens.'.format(inv_management_sync)]
    else:
        properties['Manage Inventory'] = 'Never'

    confirm(
        properties=properties,
        start_condition='The macro should be started while a battle is in progress.',
        notes=notes)

    def generate_one_click_cycle():
        # Be careful with the x coordinate here so that it clicks in between items in the
        # inventory if your inventory is full.
        nox.click_loc((503, 352), 500)      # Continue (game pauses sometimes mid-battle)

        nox.click_loc((1204, 494), 500)     # Retry
        nox.click_loc((572, 467), 500)      # Single Repeat button.  Careful not to click the button that
                                            # edits the count of stamina potions to use.
        if use_pot:
            nox.click_loc((688, 338), 500)      # Stamina Potion.
            nox.click_loc((759, 558), 500)      # Stamina Potion OK

    if inventory_management == -1:
        # If we don't need to manage inventory, just generate a simple macro that can loop forever.
        generate_one_click_cycle()
    else:
        # If we do need to manage inventory, then first generate enough cycles of the normal story
        # repeat to fill up the entire specified number of minutes.
        nox.repeat_generator_for(generate_one_click_cycle, inventory_management * 60)

        # Then switch to a mode where we just try to get to the victory screen but not initiate a
        # repeat.  We do this by just clicking the continue button every second for 2 minutes.
        # Hopefully 3 minutes is enough to finish any story level.
        def get_to_victory_screen():
            # Continue (game pauses sometimes mid-battle)
            nox.click_loc((503, 352), 1000)

            # Need to make sure to click below the loot results so they get dismissed properly
            nox.click_loc((503, 500), 1000)

        nox.repeat_generator_for(get_to_victory_screen, inv_management_sync * 60)

        # At this point the Inventory button on the top left side of the victory should be clickable.
        # so initiate the process of clicking, grinding/selling, and getting back into the battle.
        do_generate_inventory_management_for_adventure(should_grind, should_sell, use_pot)


macro_generators = [
    ("NPC Gear Purchasing and Grinding", gen_grindhouse),
    # ("Natural Stamina Regen Raid Farming (Non-Leader) (Experimental!!!)", gen_raid_experimental),
    ("AFK Raid (Member)", gen_raid),
    ("AFK Raid (Leader)", gen_raid_leader),
    ("Story Repeat w/ Natural Stamina Regen", gen_natural_stamina_farm),
    ]

print()
for (n,(desc,fn)) in enumerate(macro_generators):
    print('{0}) {1}'.format(n+1, desc))

macro_number = nox.prompt_user_for_int('Enter the macro you wish to generate: ',
                                       min=1, max=len(macro_generators))

(macro_name, file_path) = nox.load_macro_file()

(desc, fn) = macro_generators[macro_number - 1]

# Generate the macro
fn()

# At this point we're back where we started and the macro can loop.
nox.close()

print('File {0} successfully written.'.format(file_path))
