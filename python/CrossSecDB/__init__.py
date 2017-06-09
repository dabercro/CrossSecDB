import os
import logging
import MySQLdb

class XSecConnection(object):
    """
    A simple short-lived connector for cross section database
    """

    def __init__(self, write=False, cnf=None):

        which_user = 'writer' if write else 'reader'
        default_file = cnf or os.environ.get('XSECCONF', '/home/dabercro/xsec.cnf')
        self.logger = logging.getLogger('Connection_%s_%s' % (which_user, default_file))

        self.logger.debug('Opening connection')
        self.conn = MySQLdb.connect(read_default_file=default_file,
                                    read_default_group='mysql-crosssec-%s' % which_user,
                                    db='cross_sections')
        self.curs = self.conn.cursor()

    def __del__(self):
        self.logger.debug('Closing connection')
        self.conn.close()
