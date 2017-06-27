"""
Author: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import logging
import subprocess
import socket
import MySQLdb

from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# Some enums
ABS_UNCERTAINTY, REL_UNCERTAINTY = range(2)

class BadInput(Exception):
    pass

class XSecConnection(object):
    """
    A simple short-lived connector for cross section database
    """

    def __init__(self, write=False, cnf=None):
        """
        Parameters:
        -----------
          write (bool) - Lets the connection know what permissions to log onto the server with.
                         (default False)

          cnf (str) - The location of the configuration file with the default login parameters.
                      The default location should be maintained to log onto a central server.
        """

        default_file = cnf or os.environ.get('XSECCONF', '/home/dabercro/xsec.cnf')
        which_user = 'writer' if write else 'reader'

        self.logger = logging.getLogger('Connection_%s_%s' % (which_user, default_file))

        self.logger.debug('Opening connection')
        self.conn = MySQLdb.connect(read_default_file=default_file,
                                    read_default_group='mysql-crosssec-%s' % which_user,
                                    db='cross_sections')
        self.curs = self.conn.cursor()

    def __del__(self):
        self.logger.debug('Closing connection')
        self.conn.close()

def send_email(samples, cross_sections, uncertainties, updated, source, comments, energy):
    """
    Sends email reporting what was added to the database.
    """

    with open(os.path.join(os.path.dirname(__file__), 'emails.txt'), 'r') as email_file:
        emails = [line.strip() for line in email_file \
                      if line.strip() not in ['', 'email@example.com']]

    if emails:

        samples_string = '\n'
        for sample, xs in zip(samples, zip(cross_sections, uncertainties)):
            if sample in updated:
                samples_string += 'UPDATED '
            else:
                samples_string += 'NEW     '

            samples_string += '%s ---> %s +- %s\n' % (sample, xs[0], xs[1])

        email_text = """
User %s has made the following entries into the cross section database at energy %i TeV:
%s
SOURCE:

%s

COMMENTS:

%s
""" % (os.environ.get('USER', '???'), energy, samples_string,
       '\n\n'.join(set(source)), '\n\n'.join(set(comments)))

        msg = MIMEText(email_text)
        msg['Subject'] = 'Cross section update'
        msg['From'] = '%s@%s' % (os.environ.get('USER', 'cmsprod'), socket.getfqdn().lower())
        msg['To'] = ','.join(emails)

        proc = subprocess.Popen(['sendmail', '-t'], stdin=subprocess.PIPE)
        proc.communicate(input=msg.as_string())


def put_xsec(samples, cross_sections, source, comments='', cnf=None, energy=13,
             uncertainties=None, unc_type=ABS_UNCERTAINTY):
    """
    Places samples with parallel list, cross_sections into database.
    Source of the cross sections must be given.
    Comments are optional, but can be useful.

    Parameters:
    -----------
      samples (list or str) - A sample or list of samples to update the cross sections for.

      cross_sections (list or float) - A cross section or list of cross sections.
                                       If a list, it must be parallel to the samples list.

      source (str or list) - Documentation of where the cross section value came from.
                             Cannot be blank. If a list, must be parallel to samples.

      comments (str or list) - Additional comments. (default blank)
                               If a list, must be parallel to samples.

      cnf (str) - Location of the MySQL connection configuration file.
                  (default None, see XSecConnection.__init__)

      energy (int) - Energy to determine the table to insert the cross sections into.
                     (default 13)

      uncertainties (list or float) - These are uncertainties in the cross sections.
                                      If not given, they are inserted as 0.0.
                                      If a list, it must be parallel to the samples list.

      unc_type (enum) - The type of uncertainty that is being inserted. Valid options:
                        * ABS_UNCERTAINTY: For an absolute uncertainty in the cross section
                        * REL_UNCERTAINTY: For a relative uncertainty where 1.0 is 100%
    """

    # Pass lists to keep rest of logic clean

    if not isinstance(samples, list):
        samples = [samples]
    if not isinstance(cross_sections, list):
        cross_sections = [cross_sections]
    if not isinstance(source, list):
        source = [source] * len(samples)
    if not isinstance(comments, list):
        comments = [comments] * len(samples)

    # Check the uncertainties input
    if uncertainties is None:
        uncertainties = [0.0] * len(samples)
    elif not isinstance(uncertainties, list):
        uncertainties = [uncertainties]

    # If inputting relative uncertainty, replace with absolute
    if unc_type == REL_UNCERTAINTY:
        uncertainties = [xs * unc for xs, unc in zip(cross_sections, uncertainties)]


    # Check inputs

    for src in source:
        if not src:
            raise BadInput('Source of cross sections recommended for proper documentation.')
    if len(samples) != len(cross_sections):
        raise BadInput('Samples and cross sections are different length lists.')
    if len(samples) != len(source):
        raise BadInput('Samples and sources are different length lists.')
    if len(samples) != len(comments):
        raise BadInput('Samples and comments are different length lists.')

    if cnf and not os.path.exists(cnf):
        raise BadInput('Configuration file %s does not exist' % cnf)
    for xs in cross_sections:
        if xs < 0:
            raise BadInput('Negative cross section %s detected' % xs)
    if energy not in [7, 8, 13, 14]:
        raise BadInput('Invalid energy %i' % energy)

    # Put the inputs together

    many_input = [(sample, cross_sections[index], uncertainties[index], source[index], comments[index]) \
                      for index, sample in enumerate(samples)]

    # Open connection. cnf=None goes to a central location.

    conn = XSecConnection(write=True, cnf=cnf)

    statement = """
                REPLACE INTO xs_{0}TeV (sample, cross_section, uncertainty, last_updated, source, comments)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                """.format(energy)

    logger.debug('About to execute\n%s\nwith\n%s', statement, many_input)
    
    conn.curs.executemany(statement, many_input)

    # Now we want to copy into the new table.
    # We do this copying to ensure that the update time is the same between the two.

    history_stmt = """
                   INSERT INTO xs_{0}TeV_history SELECT * FROM xs_{0}TeV WHERE sample=%s
                   """.format(energy)

    # At the same time, we count the number of entries for each sample,
    # so we know if the new entry is an update or not.

    count_stmt = """
                 SELECT COUNT(*) FROM xs_{0}TeV_history WHERE sample=%s
                 """.format(energy)

    updated = []

    for sample in samples:
        conn.curs.execute(history_stmt, (sample,))
        conn.curs.execute(count_stmt, (sample,))
        
        if conn.curs.fetchone()[0] > 1:
            updated.append(sample)

    conn.conn.commit()

    # Send an email

    send_email(samples, cross_sections, uncertainties, updated, source, comments, energy)
