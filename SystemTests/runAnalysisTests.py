#!/usr/bin/env python

# quick bit of help information
import sys
if len(sys.argv) > 1 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
  print "Usage: %s [OPTIONS]" % sys.argv[0]
  print
  print "Valid options are:"
  print "       -h,--help print this information"
  print "       --email   send an email with test status."
  sys.exit(0)

# Define some necessary paths
stressmodule_dir = '../../Code/Tools/StressTestFramework'
tests_dir = 'AnalysisTests'

# Import the stress manager definition
sys.path.append(stressmodule_dir)
import stresstesting
import EmailResultReporter as em

email_reporter = em.EmailResultReporter()
mgr = stresstesting.TestManager(tests_dir, output = [email_reporter])
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
