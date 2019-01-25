#! /bin/bash

# Check the first sample for existence or help flags

SAMPLE=$1

if [ -z $SAMPLE ] || [ "$SAMPLE" = "-h" ] || [ "$SAMPLE" = "--help" ] 
then

    perldoc -T "$0"
    exit 0

fi

# Set a default energy, if not set in environment

if [ -z $ENERGY ]
then

    ENERGY=13

fi

exitcode=0

while [ "$SAMPLE" != "" ]
do

    # Get the result from the database
    output=`curl "http://t3serv001.mit.edu/~dabercro/CrossSecDB/?sample=$SAMPLE&energy=$ENERGY" 2> /dev/null`

    # Check that the output is valid
    # If not, increment the exit code
    if grep ERROR <(echo $output) > /dev/null
    then
        exitcode=$(($exitcode + 1))
    fi

    # Echo the output, no matter what it was
    echo $output

    shift              # Get the next sample
    SAMPLE=$1

done

exit $exitcode

: <<EOF

=pod

=head1 Usage

    web_get_xs.sh SAMPLE [SAMPLE [SAMPLE ...]]

Print the cross sections for a list of samples.
The output is sent to STDOUT, and separated by newlines.
By default, the samples are read off of the 13 TeV table.
To change energies, set the environment variable C<$ENERGY> to something different.

=head1 Examples

    web_get_xs.sh sample_stored_at_MIT
    web_get_xs.sh sample1 sample2
    ENERGY=8 web_get_xs.sh low_energy_sample_stored_at_MIT

=head1 Important Notes

This should be used from remote locations, such as LXPLUS.
If running on the T3, it will probably be faster to use F<get_xs.py>.
However, the nice part of this script is that is can be run from any
place with curl installed.

=head1 Author

Daniel Abercrombie <dabercro@mit.edu>

=cut

EOF
