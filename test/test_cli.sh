#! /bin/bash

ERRORS=0

# First, let's make sure querying for fake stuff doesn't work
get_xs.py some fake dataset names && ERRORS=$((ERRORS + 1))

# Next, let's input some things
put_xs.py "test" TestDataset 45.0 || ERRORS=$((ERRORS + 1))
put_xs.py --comments="Here are some with comments" "Testing lists" test1 10.0 test2 20.0 || ERRORS=$((ERRORS + 1))

# Make sure the output is right
test `get_xs.py TestDataset` = "45.0" || ERRORS=$((ERRORS + 1))

# I want this to fail first
test `ENERGY=8 get_xs.py TestDataset` = "45.0" && ERRORS=$((ERRORS + 1))

# Now let's make it pass
ENERGY=8 put_xs.py "test" TestDataset 45.0 || ERRORS=$((ERRORS + 1))
test `ENERGY=8 get_xs.py TestDataset` = "45.0" || ERRORS=$((ERRORS + 1))

# This should pass, but I'm too lazy to check the results
get_xs.py test1 test2 || ERRORS=$((ERRORS + 1))

exit $ERRORS
