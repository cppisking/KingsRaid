# KingsRaid

**About**

`krng.py` and `nox.py` constitute a program that can generate macros that can be used with Nox.  It's important to understand that this program is not -- itself -- a macro.  It does not interact with Nox or King's Raid.  It does not click anything.  Instead, this program *creates* macros that Nox understands.  Think of it as doing the equivalent of opening your Macro recorder in Nox, clicking around a bunch of times, and saving the Macro.  If you do that in Nox, Nox saves a file to your disk that contains instructions that it processes every time you click the play button to run the macro.  All this program is doing is outputting that same file.

Why do we need this?  Why not just use Nox's built-in Macro recorder?

This is a good question.  This is helpful for several reasons.

1. Some people are scared of creating Macros, thinking they'll do something wrong, or just don't feel like figuring out how to get it working.

2. Some macros are impractical to create manually.  Imagine making a Macro to buy and sell 300 items, then go to your inventory and grind them.  You would have to click buy and sell 300 times by hand.  That's pretty annoying.  Furthermore, it would run slowly.  It probably takes you a full second between clicks, or 750ms minimum, and after 300 clicks you're going to be getting tired, slowing you down further.  An automatically generated macro make all clicks as fast as the game will recognize them.  For a Macro that needs to run a long time this could shave literal hours off of your time.

3. Some macros are outright *impossible* to create manually.  A good example of this is the stamina farming macro included in this script, which will take advantage of natural stamina regen **and** use a stamina potion (but only when necessary) **and** sell your inventory for you periodically so you can run forever.  This requires complex sequences of actions and very precise clicks to avoid hitting "bad" locations.  This would be impossible to create by hand.

4. It's open source, so people can contribute.  If you have an idea for a macro, submit an issue on the tracker.  Or if you know Python, try your hand at submitting a pull request.

**Instructions**

1. Right click these two links:
   * [krng.py](https://raw.githubusercontent.com/cppisking/KingsRaid/master/krng.py)
   * [nox.py](https://raw.githubusercontent.com/cppisking/KingsRaid/master/nox.py)
   
   and save them in the same folder on your computer.

2. Install [Python 3.5 or higher](https://www.python.org/).  Just because 2.7 works now, doesn't mean it will in the future!  I plan to break support for Python 2.  Use Python 3.

3. Double click `krng.py` in Windows Explorer.

4. Answer the questions.

5. Profit!

Patches welcome.  Do not use the experimental macros unless you know what you're doing, or maybe you want to help me develop them.  That's just my testbed for new ideas.
