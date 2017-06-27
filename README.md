# MIT Cross Section DB

[![Build Status](https://travis-ci.org/MiT-HEP/CrossSecDB.svg?branch=master)](https://travis-ci.org/MiT-HEP/CrossSecDB)

This repository holds tools for centralized updating and fetching of cross sections at MIT.
Analyses throughout CMS have a variety of formats for storing their Monte Carlos cross sections.
This is an attempt to store these cross sections in a clean, machine-friendly, and documented way.

To access the Python tools, place ``CrossSecDB/python`` in your ``$PYTHONPATH``.
To access CLIs provided, place ``CrossSecDB/bin`` in your ``$PATH``.
In addition, the ``MySQLdb`` Python package must be installed on the machine you are using.
If it's not installed, you can always add it with:

    pip install -r CrossSecDB/requirements.txt

If you are on the Tier-3, ``MySQLdb`` should already be installed on your machine.
You can easily add an existing installation to your path by running the ``setup.sh`` inside the location.

### Note on running inside CMSSW environment

Note, all the python executables use the system Python, ``/usr/bin/python``, in the shebang.
This way, you will be able to access the command line tools while using CMSSW.
However, using the Python modules within your own script that is using the CMSSW may fail since CMSSW does not have ``MySQLdb`` installed.
For reading the database, make the following replacement in the examples:

``from CrossSecDB.reader import get_xsec`` with ``from CrossSecDB.reader_cmssw import get_xsec``

## Reading Cross Sections

The main motivation for this repository is to provide an exceptionally lazy tool to find cross sections.
For example, if I don't know the most recent cross section for ``WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8``,
instead of clicking around Sid's GitHub repos, I would like to type:

    $ get_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8
    61527.0

(Result is according to PandaCore at the time of writing. Also, all units are assumed to be pb.)

TODO: Add optional unit definition for input and output.

In addition to a Python Command Line Interface, functions in Python modules are provided for use.
A curl interface is also available for anyone who wants their analysis code to access information from outside the Tier-3.

A C++ header interface is planned as well for anyone who wants their analysis code to access information on the fly.

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

For those that like dumping things with system calls or just checking interactively, a command line interface is also available.
It's used just as desired in the motivation section above:

    $ get_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8
    61527.0

    $ get_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8 ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1
    61527.0
    35.85

More usage information (like how to access alternate energies) can be gathered by
calling the script without any arguments or with ``-h`` or ``--help`` as the first argument.

### Web API

Centralized cross sections can also be accessed from anywhere over the internet.
A webpage is available at the link at the top of the central repository.

In addition, a machine-friendly curl interface has been implimented.
This is used the same way as ``get_xs.py``:

    $ web_get_xs.sh WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8
    61527

    $ web_get_xs.sh WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8 ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1
    61527
    35.85

Note that when compared to ``get_xs.py``, this interface truncates trailing 0s after the decimal.

More usage information (like how to access alternate energies) can be gathered by
calling the script without any arguments or with ``-h`` or ``--help`` as the first argument.

### C++ header file

TODO: Create C++ header and tests

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

There's also a command line interface that can be used the following way:

    put_xs.py "Source is README from this repo" WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8 61527.0

More usage information (like how to access alternate energies) can be gathered by
calling the script without any arguments or with ``-h`` or ``--help`` as the first argument.

### Reverting Cross Sections

Cross sections can also be "updated" by reverting to old cross sections.
Use ``revert_xs.py`` and follow the instructions on the screen.
Here are some examples on how to call it.

    revert_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8
    ENERGY=8 revert_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8
    revert_xs.py WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8 ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1
    revert_xs.py --like 'ST_%'

## Contributing

Immediate improvements should be found the following way:

    grep -R "TODO" .

Try to format your comments accordingly.
Please write tests to prove that what you wrote works.
