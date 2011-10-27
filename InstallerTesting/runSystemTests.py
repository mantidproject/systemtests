#!/usr/bin/env python

# set up the command line options
VERSION = "1.1"
DEFAULT_FRAMEWORK_LOC = "../StressTestFramework"
import optparse
parser = optparse.OptionParser("Usage: %prog [options]", None,
                               optparse.Option, VERSION, 'error', "")
parser.add_option("-m", "--mantidpath", dest="mantidpath",
                  help="Location of mantid build")
parser.add_option("", "--email", action="store_true",
                  help="send an email with test status.")
parser.add_option("", "--frameworkLoc",
		  help="location of the stress test framework (default=%s)" % DEFAULT_FRAMEWORK_LOC)
parser.add_option("", "--disablepropmake", action="store_false", dest="makeprop",
                  help="By default this will move your properties file out of the way and create a new one. This option turns off this behavior.")
parser.set_defaults(frameworkLoc=DEFAULT_FRAMEWORK_LOC, mantidpath=None)
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
mgr = stresstesting.TestManager(mtdconf.testDir, output = [reporter])
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
print 'All tests passed? ' + str(success)
if success==False:
	sys.exit(1)
