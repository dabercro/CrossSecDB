import os
import logging

from . import XSecConnection

logger = logging.getLogger(__name__)

class BadInput(Exception):
    pass

def put_xsec(samples, cross_sections, source, comments='', cnf=None, energy=13):
    """
    Places samples with parallel list, cross_sections into database.
    Source of the cross sections must be given.
    Comments are optional, but can be useful.

    Parameters:
    -----------
      samples (list or str) - A sample or list of samples to update the cross sections for.

      cross_sections (list or float) - A cross section or list of cross sections.
                                       If a list, it must be parallel to the samples list.

      source (str) - Documentation of where the cross section value came from.
                     Cannot be blank.

      comments (str) - Additional comments.
                       (default blank)

      cnf (str) - Location of the MySQL connection configuration file.
                  (default None, see XSecConnection.__init__)

      energy (int) - Energy to determine the table to insert the cross sections into.
                     (default 13)
    """

    # Pass lists to keep rest of logic clean

    if not isinstance(samples, list):
        return put_xsec([samples], cross_sections, source, comments, cnf, energy)
    if not isinstance(cross_sections, list):
        return put_xsec(samples, [cross_sections], source, comments, cnf, energy)

    # Check inputs

    if not source:
        raise BadInput('Source of cross sections recommended for proper documentation.')
    if len(samples) != len(cross_sections):
        raise BadInput('Samples and cross sections are different length lists.')
    if cnf and not os.path.exists(cnf):
        raise BadInput('Configuration file %s does not exist' % cnf)
    for xs in cross_sections:
        if xs < 0:
            raise BadInput('Negative cross section %s detected' % xs)
    if energy not in [7, 8, 13, 14]:
        raise BadInput('Invalid energy %i' % energy)

    # Connect. Default to Dan's xsec configuration on the T3.
    # Otherwise, use the passed cnf or the environment variable XSECCONF

    many_input = [(sample, xs, source, comments) \
                      for sample, xs in zip(samples, cross_sections)]

    conn = XSecConnection(write=True, cnf=cnf)

    statement = """
                REPLACE INTO xs_{0}TeV (sample, cross_section, last_updated, source, comments)
                VALUES (%s, %s, NOW(), %s, %s)
                """.format(energy)

    logger.debug('About to execute\n%s\nwith\n%s', statement, many_input)
    
    conn.curs.executemany(statement, many_input)
    conn.conn.commit()
