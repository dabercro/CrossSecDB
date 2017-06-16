#!/bin/bash

INPUT=$1

OUTPUT_FILE=xsec_output.txt

if ! [ $CMSSW_BASE ] || ! [ $INPUT ]
then

  echo "Usage: xsec.sh INPUT"
  echo "(Need CMSSW environment)"
  exit 1

fi

if [ -e x509up_u$(id -u) ]
then

  export X509_USER_PROXY=$PWD/x509up_u$(id -u)

elif ! [ -e /tmp/x509up_u$(id -u) ]
then

  echo "X509 user proxy not found."
  exit 1

fi

get_xsec () {

    DATASET=$1

    if [ ${DATASET:0:1} = "/" ]
    then

        CMSNAME=$DATASET

    else

        CMSNAME=/${DATASET//+/\/}

    fi

    echo $CMSNAME

    for FILE in $(das_client --query "file dataset=$CMSNAME" | grep "/store")
    do
        FILES=$FILES" inputFiles=root://cms-xrd-global.cern.ch/$FILE"
    done

    OUTPUT=$(cmsRun genxsec.py $FILES 2>&1 | grep "final cross section")
    XS=$(echo $OUTPUT | awk '{ print $7 }')

    echo "put_xs.py --comments=\"./xsec.sh $CMSNAME ---> $OUTPUT\" \"unmodified GenXSecAnalyzer\" `echo $DATASET | awk -F '/' '{ print $2 }'` $XS" >> $OUTPUT_FILE

}

if [ -f $INPUT ]
then

    OUTPUT_FILE=$INPUT.out

    while read DATASET
    do

        get_xsec $DATASET

    done < $INPUT

else

    get_xsec $INPUT

fi

:<<EOF

=pod

=head1 Description

Takes a dataset or list of datasets and outputs a number of put_xs.py commands that will update the central database with the GenXSecAnalyzer results.

=head1 Usage

    ./xsec <DATASET or LISTE> [DATASET ...]

DATASET can either be in the standard CMS notation (/Process/Conditions/DataTier) or the MIT notation (Process+Conditions+DataTier).
This script will translate any MIT notation to the CMS notation before further processing.
Alternatively, you can give the name of a file as the first parameter that contains a list of datasets in either format.

If the input is individual datasets, the output commands with either be placed in a file called F<xsec_output.txt>.
Otherwise, the output will be placed in the same location as the input file with `F<.out>' appended to the end of the name.

After the output is generated, open a new window and run:

    bash xsec_output.txt

to put the cross sections into the central database.

=head1 Authors

Yutaro Iiyama <yutaro.iiyama@cern.ch> and Daniel Abercrombie <dabercro@mit.edu>

=cut

EOF
