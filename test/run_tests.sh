#! /bin/bash

TESTDIR=`dirname $0`

COUNTFAIL=0

# Run all the test scripts in the test directory

for TESTSCRIPT in $TESTDIR/test_*
do

    $TESTSCRIPT

    # Check the results

    if [ $? -ne 0 ]
    then

        COUNTFAIL=$((COUNTFAIL + 1))
        echo "FAILED: $TESTSCRIPT"

    else

        echo "PASSED: $TESTSCRIPT"

    fi

done

echo "Finishing test with number of errors: $COUNTFAIL"

exit $COUNTFAIL
