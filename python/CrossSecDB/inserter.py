"""
Author: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import logging
import subprocess
import socket

from email.mime.text import MIMEText

from . import XSecConnection

logger = logging.getLogger(__name__)

class BadInput(Exception):
    pass

def send_email(samples, cross_sections, updated, source, comments, energy):
    """
    Sends email reporting what was added to the database.
    """

    with open(os.path.join(os.path.dirname(__file__), 'emails.txt'), 'r') as email_file:
        emails = [line.strip() for line in email_file \
                      if line.strip() not in ['', 'email@example.com']]

    if emails:

        samples_string = '\n'
        for sample, xs in zip(samples, cross_sections):
            if sample in updated:
                samples_string += 'UPDATED '
            else:
                samples_string += 'NEW     '

            samples_string += '%s ---> %f\n' % (sample, xs)

        email_text = """
User %s has made the following entries into the cross section database at energy %i TeV:
%s
SOURCE:

%s

COMMENTS:

%s
""" % (os.environ.get('USER', '???'), energy, samples_string, source, comments)

        msg = MIMEText(email_text)
        msg['Subject'] = 'Cross section update'
        msg['From'] = '%s@%s' % (os.environ.get('USER', 'cmsprod'), socket.getfqdn().lower())
        msg['To'] = ','.join(emails)

        proc = subprocess.Popen(['sendmail', '-t'], stdin=subprocess.PIPE)
        proc.communicate(input=msg.as_string())


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

    # Put the inputs together

    many_input = [(sample, xs, source, comments) \
                      for sample, xs in zip(samples, cross_sections)]

    # Open connection. cnf=None goes to a central location.

    conn = XSecConnection(write=True, cnf=cnf)

    statement = """
                REPLACE INTO xs_{0}TeV (sample, cross_section, last_updated, source, comments)
                VALUES (%s, %s, NOW(), %s, %s)
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

    send_email(samples, cross_sections, updated, source, comments, energy)
