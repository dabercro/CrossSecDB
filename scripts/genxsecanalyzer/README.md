# GenXSecAnalyzer tool

This simple pair of scripts uses the GenXSecAnalyzer to generate commands
that will place calculated cross sections into the central database.
The script itself requires that you use CMSSW to calculate the cross sections.
The commands must then be run in a separate shell because `MySQLdb` is not installed in CMSSW's Python.

Up to date details about the script and how to run it can be obtained by running.

    perldoc xsec.sh

### Note about running time

If the script is taking too long for you, you may like to edit the das_client query in xsec.sh.
By adding a flag like --limit=10, a limited number of files will be run on.

### Warning

This script is not automatically tested.
It requires CMSSW to work, and that would be a pain to set up on Travis-CI.
At the time of writing, it works fine with CMSSW_8_0_X.
However, knowing CMS, this script might break at any time.
It may be worth checking the output file before running it.
