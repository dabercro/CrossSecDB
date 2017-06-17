#! /bin/bash

CHECKARG=$1

if [ ! -z $CHECKARG ]
then

    perldoc -T "$0"
    exit 0

fi

HERE=`dirname $0`

TARGET=$HOME/public_html/CrossSecDB

test -d $TARGET || mkdir $TARGET

for f in $HERE/*
do

    if [ "$f" != "$0" ]
    then

        cp $f $TARGET

    fi

done

: <<EOF
=pod

=head1 CrossSecDB webpage installer

Simply installs all contents of this directory that are not this file
into your F<$HOME/public_html/CrossSecDB> location.

Calling the script with an argument will bring up this help menu.

=head1 Author

Daniel Abercrombie <dabercro@mit.edu>

=cut
 
EOF
