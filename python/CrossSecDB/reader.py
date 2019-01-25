"""
Author: Daniel Abercrombie <dabercro@mit.edu>
"""

import logging

from .inserter import XSecConnection

logger = logging.getLogger(__name__)

class InvalidDataset(Exception):
    pass

class NoMatchingDataset(Exception):
    pass

def dump_history(samples, cnf=None, energy=13):
    """
    Get a list of historical information for each dataset.

    Parameters:
    -----------
      samples (list or str) - A list of samples or a single sample to get cross sections for.

      cnf (str) - Location of the MySQL connection configuration file.
                  (default None, see XSecConnection.__init__)

      energy (int) - Energy to determine the table to look up cross sections from.
                     (default 13)

    Returns:
    --------
      A dictionary of historical information for each dataset.
      Each key of the dictionary is a sample name from the samples passed.
      The values under these keys are lists of dictionaries containing the history.
      These lists contain the following information (with the verbatim keys):

        - cross_section
        - last_updated
        - source
        - comments

      The list is sorted with the most recent update first.
    """

    if not isinstance(samples, list):
        return dump_history([samples], cnf, energy)

    conn = XSecConnection(write=False, cnf=cnf)

    output = {}

    query = """
            SELECT cross_section, last_updated, source, comments, uncertainty
            FROM xs_{0}TeV_history WHERE sample=%s
            ORDER BY last_updated DESC
            """.format(energy)

    for sample in samples:
        conn.curs.execute(query, (sample,))

        to_add = [
            {
                'cross_section': result[0],
                'last_updated': result[1],
                'source': result[2],
                'comments': result[3],
                'uncertainty': result[4]
            } for result in conn.curs.fetchall()
        ]

        if to_add:
            output[sample] = to_add

    return output


def get_samples_like(patterns, cnf=None, energy=13, history=True):
    """
    Get the list of samples that are like a given patter or list of patterns.
    This searches the history table by default due to its use in revert_xs.py.

    Parameters:
    -----------
      patterns (list or str) - A list of patterns or a single pattern to match.

      cnf (str) - Location of the MySQL connection configuration file.
                  (default None, see XSecConnection.__init__)

      energy (int) - Energy to determine the table to look up cross sections from.
                     (default 13)

    Returns:
    --------
      A list of samples that matches the pattern.
    """

    if not isinstance(patterns, list):
        return get_samples_like([patterns], cnf, energy)

    conn = XSecConnection(write=False, cnf=cnf)

    output = []

    # Let's get which table we want to query

    table_suffix = '_history' if history else ''
    query = 'SELECT sample FROM xs_{0}TeV{1} WHERE sample LIKE %s'.format(energy, table_suffix)

    for pattern in patterns:
        conn.curs.execute(query, (pattern,))
        output.extend([result[0] for result in conn.curs.fetchall()])

    return output


def get_xsec(samples, cnf=None, energy=13, get_uncert=False):
    """
    Get the cross sections from the central database.
    Can be a list or a single sample.

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

    # Connect. Default to Dan's xsec configuration on the T3.
    # Otherwise, use the passed cnf or the environment variable XSECCONF

    conn = XSecConnection(write=False, cnf=cnf)

    output = []

    values = 'cross_section, uncertainty' if get_uncert else 'cross_section'
    query = 'SELECT {0} FROM xs_{1}TeV WHERE sample=%s'.format(values, energy)

    for sample in samples:
        logger.debug('About to execute: %s \nwith %s', query, sample)
        conn.curs.execute(query, (sample,))

        check = conn.curs.fetchone()
        logger.debug('Result: %s', check)

        if check is None:
            raise NoMatchingDataset('No matching dataset found for sample %s at energy %s TeV' % (sample, energy))

        if len(check) == 1:
            output.append(check[0])
        else:
            output.append(check)

    # If there is a zero in the output, that means it is invalid
    if False in output:
        raise InvalidDataset('Dataset %s is invalid! (cross section = 0)', samples[output.index(False)])

    # Give people behavior they would expect
    if len(output) == 1:
        return output[0]

    return output
