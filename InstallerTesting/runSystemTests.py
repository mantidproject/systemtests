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
parser.add_option("", "--runtimeDataDir", action="store_true",
                  help="Detect and declare DataDirectory for the mantid framework at runtime. Default = False")
parser.add_option("", "--frameworkLoc",
		  help="location of the stress test framework (default=%s)" % DEFAULT_FRAMEWORK_LOC)
parser.set_defaults(frameworkLoc=DEFAULT_FRAMEWORK_LOC, mantidpath=None)
(options, args) = parser.parse_args()


# import the stress testing framework
import sys
sys.path.append(options.frameworkLoc)
import stresstesting

mtdconf = stresstesting.MantidFrameworkConfig(options.mantidpath)
mtdconf.config()

# run the tests
reporter = stresstesting.XmlResultReporter()
mgr = stresstesting.TestManager(mtdconf.testDir, output = [reporter])
try:
  mgr.executeTests()
except KeyboardInterrupt:
  pass

# report the errors
success = reporter.reportStatus()
xml_report = open(os.path.join(mtdconf.saveDir, "SystemTestsReport.xml"),'w')
xml_report.write(reporter.getResults())
xml_report.close()

# put the configuratoin back to its original state
mtdconf.restoreconfig()

print
print 'Attempted %d tests' % mgr.totalTests
print 'All tests passed? ' + str(success)
if success==False:
	sys.exit(1)
