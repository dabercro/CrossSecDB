#! /usr/bin/python

"""
Usage:

  revert_xs.py [--like] SAMPLE [SAMPLE ...]

This tool creates a session that you can use to easily revert
cross sections in the central database to old values.
It also allows for invalidation of cross sections.

Using the '--like' flag will allow you to place a simple SQL
LIKE statement to get a list of samples.
All you need to know is that SQL uses '%' as wildcards.
If you do this, all arguments will be used to generate lists with LIKE.

By default, the my.cnf configuration file is a centrally maintained one.
To point to your own file, set the environment variable $XSECCONF to the location.

Also by default, the samples are read off of the 13 TeV table.
To change energies, set the environment variable $ENERGY to something different.

Example:

  XSECCONF=$HOME/my.cnf ENERGY=8 revert_xs.py --like 'DM%'

Author:

  Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import sys
import curses
import textwrap

from CrossSecDB import reader
from CrossSecDB import inserter


ENERGY = int(os.environ.get('ENERGY', 13))


def main(args):
    """
    Parameters:
    -----------
      args (list): A list of samples to run the revert tool over.
                   This is not a "star-arg" because a list is a more natural
                   container to be throwing around in the rest of the script.
    """

    if not args:
        print 'No datasets matched your --like parameters.'
        exit(1)

    history_dump = reader.dump_history(args, energy=ENERGY)

    if not history_dump:
        print 'No history found for any of your arguments: %s' % args
        exit(2)

    # This will be a list of tuples of
    # (sample, new_xs, new_source, new_comments, old_xs)
    values_to_change = []

    # Initialize window

    stdscr = curses.initscr()
    max_y, max_x = stdscr.getmaxyx()
    win = stdscr.subwin(max_y - 4, max_x - 8, 2, 4)
    bottom = max_y - 5

    # Go through all the samples in alphabetical order

    for key in sorted(history_dump):
        win.addstr('%s\n' % key, curses.A_STANDOUT)

        # We initialize options with the invalidation option
        options = {
            'i': {
                'cross_section': 0.0,
                }
            }

        # List all the historic entries
        for index, entry in enumerate(history_dump[key]):
            if not index:
                win.addstr('\nCurrent entry\n', curses.A_BOLD)
            win.addstr('%s:' % index, curses.A_BOLD)
            win.addstr(' Cross Section: %s     Last Updated: %s\n' % \
                           (entry['cross_section'], entry['last_updated']))
            win.addstr('\n   Source: %s\n' % entry['source'])
            win.addstr('\n   Comments: %s\n' % \
                       ('\n' + ' '*13).join(textwrap.wrap(entry['comments'], max_x - 25)))

            win.addstr('-' * (max_x - 8))

            options[str(index)] = entry

        # Give universal options
        win.addstr('\ni: Invalidate (set cross section to 0.0)\n', curses.A_BOLD)
        win.addstr('\nq: Quit revert attempt\n', curses.A_BOLD)

        win.addstr(bottom, 0, 'Select an option (default 0, the current entry): ',
                   curses.A_BOLD)

        chosen = win.getstr()

        win.erase()
        win.refresh()

        # If quit, clear the values to change
        if chosen == 'q':
            values_to_change = []
            break

        # Otherwise, add any changes to the list to change
        elif chosen != '0' and chosen in options.keys():
            to_update = options[chosen]
            if to_update['cross_section']:
                source = 'Reverted by revert_xs.py'
                comments = 'Reverted to match entry from %s by revert_xs.py' %\
                    to_update['last_updated']
            else:
                source = 'Invalidated by revert_xs.py'
                comments = 'Dataset entry probably not valid. Set to 0.0.'

            values_to_change.append((key, to_update['cross_section'], source, 
                                     comments, options['0']['cross_section']))

    if values_to_change:
        win.addstr('Review submission\n\n', curses.A_STANDOUT)

        for sample, xs, _, _, old_xs in values_to_change:
            win.addstr('%s: %s --> %s\n' % (sample, old_xs, xs))

        win.addstr(bottom, 0, 'Submit these changes? (y/n, default n): ',
                   curses.A_BOLD)
        submission = win.getstr()

        if submission != 'y':
            values_to_change = []

    curses.endwin()

    for sample, xs, source, comments, _ in values_to_change:
        inserter.put_xsec(sample, xs, source, comments, energy=ENERGY)


if __name__ == '__main__':

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        print __doc__
        exit(0)

    # This crashes when trying to write too much to the screen
    # TODO: Change the window to a pad? and give ways to scroll to prevent crashes on overflow.
    try:
        if sys.argv[1] == '--like':
            main(reader.get_samples_like(sys.argv[2:], energy=ENERGY))

        else:
            main(sys.argv[1:])

    except Exception as e:
        print e
        curses.endwin()
