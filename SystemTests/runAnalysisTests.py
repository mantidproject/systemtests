#!/usr/bin/env python

from systemtestlib import *

# quick bit of help information
VERSION = "1.1"
import optparse
parser = optparse.OptionParser("Usage: %prog [options]", None,
                               optparse.Option, VERSION, 'error', "")
parser.add_option("-m", "--mantidpath", dest="mantidpath",
                  help="Location of mantid build")
parser.add_option("", "--email", action="store_true",
                  help="send an email with test status.")
parser.add_option("", "--runtimeDataDir", action="store_true",
                  help="Detect and declare DataDirectory for the mantid framework at runtime. Default = False")
(options, args) = parser.parse_args()

# add the correct paths
try:
  setMantidPath(options.mantidpath)
except RuntimeError, e:
  parser.error(e)

# initialise the mantid framework
from MantidFramework import *
mtd.initialise()
setDataDirs(mtd)

# Import the stress manager definition
import stresstesting

if options.runtimeDataDir:
  dataDirs = getDataDirs()
else:
  dataDirs = []

email_reporter = stresstesting.EmailResultReporter()
mgr = stresstesting.TestManager(locateTestsDir(), output = [email_reporter],
                                dataDirs=dataDirs)
mgr.executeTests()

success = True
try:
  if sys.argv[1] == '--email':
    success = email_reporter.sendEmail()
  else:
    success = email_reporter.reportStatus()
except IndexError:
  success = email_reporter.reportStatus()

import os
import datetime
try:
  os.rename('logs/analysisTests.log','logs/analysisTests'+ str(datetime.date.today()) +'.log')
except OSError:
  pass

print 'All tests passed? ' + str(success)
if success==False:
  sys.exit(1)
