#! /usr/bin/env python

import os
import unittest
import MySQLdb

from CrossSecDB import inserter
from CrossSecDB import reader

# TODO: Finish writing tests

class TestInsertRead(unittest.TestCase):

    def setUp(self):
        """
        At the beginning of each test, start with a fresh database
        """
        conn = MySQLdb.connect(read_default_file=\
                                   os.environ.get('XSECCONF', os.path.join(os.path.dirname(__file__), 'my.cnf')),
                               read_default_group='mysql-crosssec-writer',
                               db='cross_sections')

        curs = conn.cursor()

        # Quickly parse our .sql file to setup a database for tests
        with open(os.path.join(os.path.dirname(__file__), '../db/cross_sections.sql'),'r') as sql_file:
            for line in \
                    ''.join([line.strip() for line in sql_file if line[:2] != '--']).split(';'):
                if line:
                    curs.execute(line)

        conn.close()

    def test_defaults(self):
        """
        This is just a test to check that inserting
        and reading under normal operations behaves
        appropriately.
        """
        # We can put in cross sections one at a time
        inserter.put_xsec('TestDataSet', 45.0, 'test')
        self.assertEqual(reader.get_xsec('TestDataSet'), 45.0)

        # We can also put in parallel lists
        inserter.put_xsec(['Test1', 'Test2'], [10.0, 20.0], 'test')
        self.assertEqual(reader.get_xsec('Test1'), 10.0)
        self.assertEqual(reader.get_xsec('Test2'), 20.0)

        self.assertEqual(reader.get_xsec(['TestDataSet', 'Test1', 'Test2']),
                         [45.0, 10.0, 20.0])

    def test_negative_xsec(self):
        """
        This is to test that an exception is raised
        when someone puts in a negative cross section
        """
        pass

    def test_other_energy(self):
        """
        This is a test to check that the non-default
        energy tables work as intended.
        """
        pass

    def test_no_source(self):
        """
        When someone doesn't supply a source for their
        cross section the insertion should fail
        """
        pass

    def test_all_fields_full(self):
        """
        Just check that the date, source, and comments fields are correctly filled.
        """
        pass

if __name__ == '__main__':
    unittest.main()
