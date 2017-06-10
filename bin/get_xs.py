#! /usr/bin/env python

"""
Usage:

  get_xs.py SAMPLE [SAMPLE [SAMPLE ...]]

Print the cross sections for a list of samples.
The output is sent to STDOUT, and separated by newlines.

By default, the my.cnf configuration file is a centrally maintained one.
To point to your own file, set the environment variable $XSECCONF to the location.

Also by default, the samples are read off of the 13 TeV table.
To change energies, set the environment variable $ENERGY to something different.

Example:

  XSECCONF=$HOME/my.cnf ENERGY=8 get_xs.py sample_i_definitely_stored_elsewhere
"""

import os
import sys

from CrossSecDB.reader import get_xsec

if __name__ == '__main__':

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        print __doc__
        exit(0)

    energy = int(os.environ.get('ENERGY', 13))

    output = get_xsec(sys.argv[1:], energy=energy)

    if isinstance(output, list):
        for xs in output:
            print xs

    else:
        print output
