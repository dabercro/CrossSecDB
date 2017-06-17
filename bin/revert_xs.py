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


def main(stdscr, history_dump):
    """
    Parameters:
    -----------
      stdscr (curses screen): The result of curses.initscr().
                              This allows the function to be wrapped.

      history_dump (dict): A dictionary of historic information for datasets.
                           It is the output of CrossSecDB.reader.dump_history.

    Returns:
    --------
      A list of tuples containing the information to be used in reverting or invalidating.
      Each tuple contains (sample, new cross section, new source, new comments, old cross section).
    """

    # Initialize window

    curses.use_default_colors()
    max_y, max_x = stdscr.getmaxyx()
    master_pad = curses.newpad(max_y, max_x - 8)

    # Historic information is displayed here
    history_pad = curses.newpad(1024, max_x - 12)

    # User input is displayed here
    input_pad = curses.newpad(1, max_x - 8)
    bottom = max_y - 2

    # This will be a list of tuples of
    # (sample, new_xs, new_source, new_comments, old_xs)
    output = []

    # Go through all the samples in alphabetical order

    for key in sorted(history_dump):
        master_pad.erase()
        master_pad.addstr('%s\n\n' % key, curses.A_STANDOUT)
        master_pad.addstr('Options from history (use up and down keys to scroll)', curses.A_BOLD)

        # We initialize options with the invalidation option
        options = {
            'i': {
                'cross_section': 0.0,
                }
            }

        # List all the historic entries
        for index, entry in enumerate(history_dump[key]):
            if not index:
                history_pad.addstr('Current entry\n', curses.A_BOLD)
            history_pad.addstr('%s:' % index, curses.A_BOLD)
            history_pad.addstr(' Cross Section: %s     Last Updated: %s\n' % \
                                   (entry['cross_section'], entry['last_updated']))
            history_pad.addstr('\n   Source: %s\n' % entry['source'])
            history_pad.addstr('\n   Comments: %s\n' % \
                                   ('\n' + ' '*13).join(textwrap.wrap(entry['comments'], max_x - 25)))

            history_pad.addstr('-' * (max_x - 12))

            options[str(index)] = entry

        # Give universal options
        master_pad.addstr(bottom - 9, 0, 'Universal Options', curses.A_BOLD)
        master_pad.addstr(bottom - 7, 2, 'i: ', curses.A_BOLD)
        master_pad.addstr('Invalidate (set cross section to 0.0)')
        master_pad.addstr(bottom - 5, 2, 'q: ', curses.A_BOLD)
        master_pad.addstr('Quit revert attempt')

        input_pad.addstr('Select an option (default 0, the current entry): ',
                         curses.A_BOLD)

        master_pad.refresh(0, 0, 2, 4, bottom, max_x - 8)
        history_pad.refresh(0, 0, 6, 6, bottom - 8, max_x - 12)
        input_pad.refresh(0, 0, bottom, 4, bottom + 2, max_x - 8)

        chosen = input_pad.getstr()

        # If quit return nothing to be changed
        if chosen == 'q':
            return []

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

            output.append((key, to_update['cross_section'], source, 
                                     comments, options['0']['cross_section']))

    if output:
        win.addstr('Review submission\n\n', curses.A_STANDOUT)

        for sample, xs, _, _, old_xs in output:
            win.addstr('%s: %s --> %s\n' % (sample, old_xs, xs))

        win.addstr(bottom, 0, 'Submit these changes? (y/n, default n): ',
                   curses.A_BOLD)
        submission = win.getstr()

        if submission == 'y':
            return output

    return []


if __name__ == '__main__':

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        print __doc__
        exit(0)

    # This crashes when trying to write too much to the screen
    # TODO: Change the window to a pad? and give ways to scroll to prevent crashes on overflow.
    args = reader.get_samples_like(sys.argv[2:], energy=ENERGY) \
        if sys.argv[1] == '--like' else sys.argv[1:]

    if not args:
        print 'No datasets matched your --like parameters.'
        exit(1)

    history_dump = reader.dump_history(args, energy=ENERGY)

    if not history_dump:
        print 'No history found for any of your arguments: %s' % args
        exit(2)

    values_to_change = curses.wrapper(main, history_dump)

    for sample, xs, source, comments, _ in values_to_change:
        inserter.put_xsec(sample, xs, source, comments, energy=ENERGY)
