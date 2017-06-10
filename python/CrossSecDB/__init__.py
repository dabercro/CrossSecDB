import os
import logging
import MySQLdb

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
