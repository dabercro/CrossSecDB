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

    # This will be a list of tuples of (sample, xs, comments, old_xs)
    values_to_change = []

    stdscr = curses.initscr()
    max_y, max_x = stdscr.getmaxyx()
    win = stdscr.subwin(max_y - 4, max_x - 8, 2, 4)
    bottom = max_y - 5

    for key in sorted(history_dump):
        win.addstr('%s\n' % key, curses.A_STANDOUT)

        options = {
            'i': {
                'cross_section': 0.0,
                }
            }

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

        win.addstr('\ni: Invalidate (set cross section to 0.0)\n\n', curses.A_BOLD)
        win.addstr('\nq: Quit revert attempt\n', curses.A_BOLD)

        win.addstr(bottom, 0, 'Select an option (default 0, the current entry): ',
                   curses.A_BOLD)

        chosen = win.getstr()

        win.erase()
        win.refresh()

        if chosen == 'q':
            values_to_change = []
            break

        elif chosen != '1' and chosen in options.keys():
            to_update = options[chosen]
            comments = 'Reverted to match entry from %s by revert_xs.py' %\
                to_update['last_updated'] \
                if to_update['cross_section'] else \
                'Dataset entry probably not valid. Set to 0.0.'
            values_to_change.append(key, to_update['cross_section'], comments,
                                    options['0']['cross_section'])

    if values_to_change:
        win.addstr('Review submission\n\n', curses.A_STANDOUT)

        for sample, xs, _, new_xs in values_to_change:
            win.addstr('%s: %s --> %s\n' % (sample, xs, new_xs))

        submission = win.addstr(bottom, 0, 'Submit these changes? (y/n, default n): ',
                                curses.A_BOLD)

        if submission != 'y':
            values_to_change = []

    curses.endwin()

    for sample, xs, comments, _ in values_to_change:
        reader.put_xsec(sample, xs, 'Reverted by revert_xs.py', comments, energy=ENERGY)


if __name__ == '__main__':

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        print __doc__
        exit(0)

    try:
        if sys.argv[1] == '--like':
            main(reader.get_samples_like(sys.argv[2:], energy=ENERGY))

        else:
            main(sys.argv[1:])

    except Exception as e:
        print e
        curses.endwin()
