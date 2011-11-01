#!/usr/bin/env python

# set up the command line options
VERSION = "1.1"
DEFAULT_FRAMEWORK_LOC = "../StressTestFramework"

info = []
info.append("This program will configure mantid run all of the system tests located in")
info.append("the 'SystemTests/AnalysisTests' directory and log the results in 'logs/'.")
info.append("This program will create a temporary 'Mantid.user.properties' file which")
info.append("it will rename to 'Mantid.user.properties.systest' upon completion. The")
info.append("current version of the code does not print to stdout while the test is")
info.append("running, so the impatient user may ^C to kill the process. In this case")
info.append("all of the tests that haven't been run will be marked as skipped in the")
info.append("full logs.")

import optparse
parser = optparse.OptionParser("Usage: %prog [options]", None,
                               optparse.Option, VERSION, 'error', ' '.join(info))
parser.add_option("-m", "--mantidpath", dest="mantidpath",
                  help="Location of mantid build")
parser.add_option("", "--email", action="store_true",
                  help="send an email with test status.")
parser.add_option("", "--frameworkLoc",
		  help="location of the stress test framework (default=%s)" % DEFAULT_FRAMEWORK_LOC)
parser.add_option("", "--disablepropmake", action="store_false", dest="makeprop",
                  help="By default this will move your properties file out of the way and create a new one. This option turns off this behavior.")
parser.add_option("-R", "--tests-regex", dest="testsInclude",
                  help="String specifying which tests to run. Simply uses 'string in testname'.")
parser.add_option("-E", "--excluderegex", dest="testsExclude",
                  help="String specifying which tests to not run. Simply uses 'string in testname'.")
parser.set_defaults(frameworkLoc=DEFAULT_FRAMEWORK_LOC, mantidpath=None, makeprop=True)
(options, args) = parser.parse_args()

# import the stress testing framework
import sys
import os
sys.path.append(options.frameworkLoc)
import stresstesting

mtdconf = stresstesting.MantidFrameworkConfig(options.mantidpath)
if options.makeprop:
  mtdconf.config()

# run the tests
reporter = stresstesting.XmlResultReporter()
mgr = stresstesting.TestManager(mtdconf.testDir, output = [reporter],
                                testsInclude=options.testsInclude, testsExclude=options.testsExclude)
try:
  mgr.executeTests()
except KeyboardInterrupt:
  mgr.markSkipped("KeyboardInterrupt")

# report the errors
success = reporter.reportStatus()
xml_report = open(os.path.join(mtdconf.saveDir, "SystemTestsReport.xml"),'w')
xml_report.write(reporter.getResults())
xml_report.close()

# put the configuratoin back to its original state
if options.makeprop:
  mtdconf.restoreconfig()

print
percent = 1.-float(mgr.failedTests)/float(mgr.totalTests)
percent = int(100. * percent)
print "%d%s tests passed, %d tests failed out of %d (%d skipped)" % \
          (percent, '%', mgr.failedTests, mgr.totalTests, mgr.skippedTests)
if mgr.skippedTests == mgr.totalTests:
  print "All tests were skipped"
  success = False # fail if everything was skipped
print 'All tests passed? ' + str(success)
if success==False:
	sys.exit(1)
