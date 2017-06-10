#! /bin/bash

#
# Author: Daniel Abercrombie <dabercro@mit.edu>
#

# Note that this test depends on put_xs.py to work correctly.
# Not the best in terms of unit testing philosophy, but works fine for TDD...

ERRORS=0

export INDEX_SCRIPT=`dirname $0`/../web/index.php

# First check that a blank call returns a web page.
PAGE=`php $INDEX_SCRIPT`
test "${PAGE:0:15}" = '<!DOCTYPE HTML>' || ERRORS=$((ERRORS + 1))

# Now check that a bad call returns error
export QUERY_STRING="sample=FakeDataset"
RESULT=`php -r 'parse_str($_SERVER["QUERY_STRING"], $_GET); include "$_SERVER['INDEX_SCRIPT']";'`
test "$RESULT" = "ERROR: cross section missing for FakeDataset at energy 13 TeV." || ERRORS=$((ERRORS + 1))

# Now input dataset and check that it comes back
# Note that PHP will truncate extra zero digits after the decimal
put_xs.py "test" TestDataset 45.5
export QUERY_STRING="sample=TestDataset"
RESULT=`php -r 'parse_str($_SERVER["QUERY_STRING"], $_GET); include "$_SERVER['INDEX_SCRIPT']";'`
test "$RESULT" = "45.5" || ERRORS=$((ERRORS + 1))

# Check different energy fails
export QUERY_STRING="sample=FakeDataset&energy=8"
RESULT=`php -r 'parse_str($_SERVER["QUERY_STRING"], $_GET); include "$_SERVER['INDEX_SCRIPT']";'`
test "$RESULT" = "ERROR: cross section missing for FakeDataset at energy 8 TeV." || ERRORS=$((ERRORS + 1))

# Insert into other energy
ENERGY=8 put_xs.py "test" TestDataset 36.5
export QUERY_STRING="sample=TestDataset&energy=8"
RESULT=`php -r 'parse_str($_SERVER["QUERY_STRING"], $_GET); include "$_SERVER['INDEX_SCRIPT']";'`
test "$RESULT" = "36.5" || ERRORS=$((ERRORS + 1))

# Check that we still get webpage for sample
export QUERY_STRING="sample=TestDataset&browse=true"
PAGE=`php -r 'parse_str($_SERVER["QUERY_STRING"], $_GET); include "$_SERVER['INDEX_SCRIPT']";'`
test "${PAGE:0:15}" = '<!DOCTYPE HTML>' || ERRORS=$((ERRORS + 1))

exit $ERRORS
