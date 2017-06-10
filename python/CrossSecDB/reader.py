import logging

from . import XSecConnection

logger = logging.getLogger(__name__)

class NoMatchingDataset(Exception):
    pass

def get_xsec(samples, cnf=None, energy=13):
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

    Returns:
    --------
      By default, a list of cross sections, parallel to the list of samples.
      If the list is only one element long, or samples was not a list, just a float is returned.
    """

    if not isinstance(samples, list):
        return get_xsec([samples], cnf, energy)

    # Connect. Default to Dan's xsec configuration on the T3.
    # Otherwise, use the passed cnf or the environment variable XSECCONF

    conn = XSecConnection(write=False, cnf=cnf)

    output = []

    for sample in samples:
        query = 'SELECT cross_section FROM xs_%sTeV WHERE sample=%s'
        params = (energy, sample)

        logger.debug('About to execute\n%s\nwith\n%s', query, params)
        conn.curs.execute(query, params)

        check = conn.curs.fetchone()

        if check is None:
            raise NoMatchingDataset('No matching dataset found for sample %s at energy %s' % (sample, energy))

        output.append(check[0])

    # Give people behavior they would expect
    if len(output) == 1:
        return output[0]

    return output
