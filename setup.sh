#! /bin/bash

#
# A simple script to modify your .bashrc to use this tool
#
# Author: Daniel Abercrombie <dabercro@mit.edu>
#

LOCATION=`dirname $0`

if [ -f $HOME/.bashrc ]
then
    PROFILE=$HOME/.bashrc
else
    echo "Cannot find your .bashrc!"
    exit 1
fi

source $PROFILE

TARGET=$LOCATION/python

case ":$PYTHONPATH:" in

    *:$TARGET:*)
        echo " # Python already is included."
	;;

    *)
        echo "# Adding to PYTHONPATH"
	echo "" >> $PROFILE
	echo "# Python objects in CrossSecDB" >> $PROFILE
	echo "export PYTHONPATH=\$PYTHONPATH:"$TARGET >> $PROFILE
	;;

esac

TARGET=$LOCATION/bin

case ":$PATH:" in

    *:$TARGET:*)
        echo " # Executables are already included."
	;;

    *)
        echo "# Adding to PATH"
	echo "" >> $PROFILE
	echo "# Executables in CrossSecDB" >> $PROFILE
	echo "export PATH=\$PATH:"$TARGET >> $PROFILE
	;;

esac

echo "# Setup complete..."
echo "# Now source your $PROFILE to update your PATH and PYTHONPATH."
