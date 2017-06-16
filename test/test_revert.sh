#! /bin/bash

#
# Author: Daniel Abercrombie <dabercro@mit.edu>
#

ERRORS=0

# First put the TestDataset twice

put_xs.py 'source: test' TestDataset 10.0
sleep 2
put_xs.py 'source: test' TestDataset 20.0

test `get_xs.py TestDataset` = "20.0" || ERRORS=$((ERRORS + 1))

# Now try to revert
# We pick from the menu 1 to get to the old cross section
# 0 is the current cross section

printf "1\ny\n" | revert_xs.py TestDataset

test `get_xs.py TestDataset` = "10.0" || ERRORS=$((ERRORS + 1))

# Now we want to invalidate
# Now that the revert is included, the invalidate option should be 'i'

printf "i\ny\n" | revert_xs.py TestDataset

# This should fail that there is no valid cross section

get_xs.py TestDataset && ERRORS=$((ERRORS + 1))

# Let's try a different energy

ENERGY=8 put_xs.py 'source: test' TestDataset 8.0
sleep 2
ENERGY=8 put_xs.py 'source: test' TestDataset 18.0

printf "1\ny\n" | ENERGY=8 revert_xs.py TestDataset

test `ENERGY=8 get_xs.py TestDataset` = "8.0" || ERRORS=$((ERRORS + 1))

# Finally, let's make sure that running over an invalid dataset allows us to recover
# Option 0 is keep the same as invalid, and option 1 is most recent "20.0"

printf "1\ny\n" | revert_xs.py TestDataset

test `get_xs.py TestDataset` = "20.0" || ERRORS=$((ERRORS + 1))

# Finally, we want a real non-existent database to cause an error

echo "About to cause crash on purpose. Use Ctrl + C if this hangs."

revert_xs.py TestDataset && ERRORS=$((ERRORS + 1))

# Now let's test --like!

put_xs.py 'source: test' Like1 20.0
put_xs.py 'source: test' Like2 30.0
sleep 2
put_xs.py 'source: test' Like1 25.0
put_xs.py 'source: test' Like2 35.0

test `get_xs.py Like1` = "25.0" || ERRORS=$((ERRORS + 1))
test `get_xs.py Like2` = "35.0" || ERRORS=$((ERRORS + 1))

printf "2\n2\ny\n" | revert_xs.py --like 'Like%'

test `get_xs.py Like1` = "20.0" || ERRORS=$((ERRORS + 1))
test `get_xs.py Like2` = "20.0" || ERRORS=$((ERRORS + 1))

echo "About to cause crash on purpose. Use Ctrl + C if this hangs."

revert_xs.py --like 'NotThere%' && ERRORS=$((ERRORS + 1))

exit $ERRORS
