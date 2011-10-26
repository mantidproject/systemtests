#!/usr/bin/env python

import sys

# Define some necessary paths
stressmodule_dir = '../StressTestFramework'
tests_dir = '../SystemTests/AnalysisTests'
#tests_dir = '../DummyTests'
# Import the stress manager definition
sys.path.append(stressmodule_dir)
import stresstesting

reporter = stresstesting.XmlResultReporter()
mgr = stresstesting.TestManager(tests_dir, output = [reporter])
mgr.executeTests()

success = reporter.reportStatus()

xml_report = open('../logs/SystemTestsReport.xml','w')
xml_report.write(reporter.getResults())
xml_report.close()

print 'All tests passed? ' + str(success)
if success==False:
	sys.exit(1)
