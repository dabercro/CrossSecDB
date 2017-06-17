#! /bin/bash

#
# Author: Daniel Abercrombie <dabercro@mit.edu>
#

TESTDIR=`dirname $0`

export XSECCONF=$TESTDIR/my.cnf

COUNTFAIL=0

# Run all the test scripts in the test directory

for TESTSCRIPT in $TESTDIR/test_*.??
do

    mysql --defaults-file=$TESTDIR/my.cnf --defaults-group-suffix=-crosssec-writer -Dcross_sections < $TESTDIR/../db/cross_sections.sql
    $TESTSCRIPT

    # Check the results

    RESULT=$?

    if [ $RESULT -ne 0 ]
    then

        COUNTFAIL=$((COUNTFAIL + 1))
        tput setaf 1 2> /dev/null
        echo "FAILED: $TESTSCRIPT with exit code $RESULT"

    else

        tput setaf 2 2> /dev/null
        echo "PASSED: $TESTSCRIPT"

    fi

    tput sgr0 2> /dev/null

done

echo "Finishing test with number of errors: $COUNTFAIL"

exit $COUNTFAIL
