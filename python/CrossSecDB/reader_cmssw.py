"""
Use this module for reading cross sections if you are running Python 2.7 with no MySQLdb.
It will not work in Python 2.6.

Author: Daniel Abercrombie <dabercro@mit.edu>
"""

import subprocess

def get_xsec(samples, cnf=None, energy=13, get_uncert=False):
    """
    This is a wrapper for the get_xs.py script, which can be run no matter which python version you are using.

    Parameters:
    -----------
      samples (list or str) - A list of samples or a single sample to get cross sections for.

      cnf (str) - Location of the MySQL connection configuration file.
                  (default None, see XSecConnection.__init__)

      energy (int) - Energy to determine the table to look up cross sections from.
                     (default 13)

      get_uncert (bool) - Determines whether or not to fetch uncertainties from the database too.

    Returns:
    --------
      By default, a list of cross sections, parallel to the list of samples.
      If the list is only one element long, or samples was not a list, just a float is returned.
      If get_uncertainties is set to True, this list is a list of tuples with cross section and absolute uncertainty.
      Or the lone float is a tuple.
    """

    if not isinstance(samples, list):
        samples = [samples]

    cnf_str = 'XSECCONF=%s' % cnf if cnf else ''
    samples_str = ' '.join(samples)

    stdout = subprocess.check_output('ENERGY=%i %s get_xs.py %s' % (energy, cnf_str, samples_str), shell=True)

    output = [float(line) for line in stdout.split('\n') if line.strip()]

    # Give people behavior they would expect
    if len(output) == 1:
        return output[0]

    return output
