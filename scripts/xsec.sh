#!/bin/bash

INPUT=$1

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

    for FILE in $(das_client --query "file dataset=$CMSNAME" --limit 2 | grep "/store")
    do
        FILES=$FILES" inputFiles=root://cms-xrd-global.cern.ch/$FILE"
    done

    cmsRun genxsec.py $FILES 2>&1

}

if [ -f $INPUT ]
then

    while read DATASET
    do

        get_xsec $DATASET

    done < $INPUT

else

    get_xsec $INPUT

fi