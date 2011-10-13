import os
import sys
from xml.dom.minidom import getDOMImplementation

# Define some necessary paths
stressmodule_dir = '../StressTestFramework'
tests_dir = '../SystemTests/AnalysisTests'
#tests_dir = '../DummyTests'
# Import the stress manager definition
sys.path.append(stressmodule_dir)
import stresstesting

#os.chdir('SystemTests')

class XmlResultReporter(stresstesting.ResultReporter):

	_time_taken = 0.0
	_errors = 0
	_failures = 0
	
	def __init__(self):
		self._doc = getDOMImplementation().createDocument(None,'testsuite',None)

	def reportStatus(self):
		return self._failures == 0

	def getResults(self):
		docEl = self._doc.documentElement
		docEl.setAttribute('name','SystemTests')
		docEl.setAttribute('tests',str(len(docEl.childNodes)))
		docEl.setAttribute('errors',str(self._errors))
		docEl.setAttribute('failures',str(self._failures))
		docEl.setAttribute('time',str(self._time_taken))
		return self._doc.toxml()

	def dispatchResults(self, result):
		''' This relies on the order and names of the items to give the correct output '''
		test_name = result.name.split('.')
		if len(test_name) > 1:
			class_name = '.'.join(test_name[:-1])
			name = test_name[-1]
		else:
			class_name = result.name
			name = result.name
		elem = self._doc.createElement('testcase')
		elem.setAttribute('classname',class_name)
		elem.setAttribute('name',name)
		if result.status != 'success':
			self._failures += 1
			failEl = self._doc.createElement('failure')
			failEl.setAttribute('file',result.filename)
			output = ''
			if len(result.output) > 0:
				output += result.output
			if len(output) > 0:
				failEl.appendChild(self._doc.createTextNode(output))
			elem.appendChild(failEl)
		time_taken = 0.0
		for t in result.resultLogs():
			if t[0] == 'iteration time_taken':
				time_taken = float(t[1].split(' ')[1])
				self._time_taken += time_taken
		elem.setAttribute('time',str(time_taken))
		elem.setAttribute('totalTime',str(time_taken))
		self._doc.documentElement.appendChild(elem)

reporter = XmlResultReporter()
mgr = stresstesting.TestManager(tests_dir, output = [reporter])
mgr.executeTests()

success = reporter.reportStatus()

xml_report = open('../logs/SystemTestsReport.xml','w')
xml_report.write(reporter.getResults())
xml_report.close()

print 'All tests passed? ' + str(success)
if success==False:
	sys.exit(1)
