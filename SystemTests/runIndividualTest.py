#!/usr/bin/env python

info = '''
This is provided for testing purposes. It allows you to run the single test
given as an argument.
It can be useful for debugging because the errors do not alway 'get out' of
the sub-process used for running the tests in the regular way
'''
VERSION = "1.1"

import optparse
import os
import sys
from systemtestlib import *

# set up command line parser
parser = optparse.OptionParser("Usage: %prog [options] filename[.testName]", None,
                      optparse.Option, VERSION, 'error', info)
parser.add_option("-m", "--mantidpath", dest="mantidpath",
                  help="Location of mantid build")
(options, args) = parser.parse_args()

# add the correct paths
try:
    setMantidPath(options.mantidpath)
except RuntimeError, e:
    parser.error(e)

tests_dir = os.path.join(locateSourceDir(), 'AnalysisTests')

# Find these first
sys.path.insert(0,tests_dir)
if os.path.isdir("../StressTestFramework"):
    sys.path.insert(0,"../StressTestFramework")
# Ensure we pick up the correct version of the Framework (Works around a Mac issue at the moment)
sys.path.insert(0, os.environ['MANTIDPATH'])
from MantidFramework import *
mtd.initialise()
from stresstesting import MantidStressTest

setDataDirs(mtd)

# select the test to run
try:
    test_to_run = args[0]
except:
    parser.error("Need to supply test to run")
test_to_run = os.path.split(test_to_run)[1]
pieces = test_to_run.split('.')
if len(pieces) == 2:
    test_module = pieces[0]
    test_to_run = pieces[1]
    if test_to_run == 'py': 
        test_to_run = None
elif len(pieces) == 1:
    test_module = test_to_run
    test_to_run = None # Indicates run all in module
else:
    parser.error()

# run the test
module = __import__(test_module)
attributes = dir(module)
passed = []
failed = []
for name in attributes:
    attr = getattr(module, name)
    if hasattr(attr, 'execute') and issubclass(attr,MantidStressTest):
        if test_to_run is not None and name != test_to_run:
            continue
        test_name = test_module + '.' + name
        obj = attr() # Create an object
        obj.execute()
        outcome = obj.doValidation()
        if outcome == True: 
            outcome = 'Passed'
            passed.append(test_name)
        else: 
            outcome = 'FAILED'
            failed.append(test_name)

        msg = '*** %s ... %s'
        print msg % (test_name,outcome)

# Print a summary if any tests failed
percent = 1.-float(len(failed))/float(len(passed)+len(failed))
percent = int(100. * percent)
summary = "%d%s tests passed, %d tests failed out of %d" % \
          (percent, '%', len(failed), len(passed))
print
if len(failed) > 0:
    print summary
    print 'The following tests FAILED:'
    for name in failed:
        print ' '*4 + name
elif len(passed) == 0:
    print 'No tests found!!'
else:
    print summary
