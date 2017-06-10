# MIT Cross Section DB

This repository holds tools for centralized updating and fetching of cross sections at MIT.
Analyses throughout CMS have a variety of formats for storing their Monte Carlos cross sections.
This is an attempt to store these cross sections in a clean, machine-friendly, and documented way.

## Reading Cross Sections

The main motivation for this repository is to provide an exceptionally lazy tool to find cross sections.
For example, if I don't know the most recent cross section for ``WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8``,
instead of clicking around Sid's GitHub repos, I would like to type:

    $ get_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8
    61527.0

(Result is according to PandaCore at the time of writing.)

In addition to a Python Command Line Interface (in progress), functions in Python modules are provided for use.

C++ header and PHP cUrl/browser interface planned as well for anyone who wants their analysis code to access information on the fly.

### Python module

Cross sections can be retrieved from the central database very easily once this package is installed:

    from CrossSecDB.reader import get_xsec

    print get_xsec('WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8')
    print get_xsec(['WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', 'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'])

This would give an output like:

    61527.0
    [61527.0, 35.85]

You can always

    print get_xsec.__doc__

for addition, up to date documentation.

### Python script

TODO

### C++ header file

TODO

### Web API

TODO

## Updating Cross Sections

To encourage contribution to the centralized database, scripts for sending updates are also fun and easy to use.
These are provided only through Python interfaces.
Using the Python module would look something like this:

    from CrossSecDB.inserter import put_xsec

    print put_xsec.__doc__

    put_xsec('WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', 61527.0, source='README from this repo')

From the docstring, you might learn that parallel lists work as well:

    import process
    from CrossSecDB.inserter import put_xsec

    samples = []
    xs = []

    for key, val in process.processes.items():
        if 'mad' not in key and 'pythia' not in key:
            continue
        samples.append(key)
        xs.append(val[2])

    put_xsec(samples, xs, '/home/dhsu/CMSSW_8_0_26_patch1/src/PandaCore/Tools/python/processes.py')

Easy!

## Contributing

The easiest way to find improvements that need to be made is the following:

    grep -R "TODO" .
