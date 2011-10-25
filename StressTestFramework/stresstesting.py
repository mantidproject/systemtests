'''
Mantid stress testing framework. This module contains all of the necessary code
to run sets of stress tests on the Mantid framework by executing scripts directly
or by importing them into MantidPlot.

Copyright &copy; 2009 STFC Rutherford Appleton Laboratories

This file is part of Mantid.

Mantid is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

Mantid is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

File change history is stored at: <https://svn.mantidproject.org/mantid/trunk/Code>.
'''

import sys
import os
import types
import re
import time
import datetime
import platform
import subprocess
import tempfile

#########################################################################
# The base test class.
#########################################################################
class MantidStressTest(object):
    '''Defines a base class for stress tests, providing functions
    that should be overridden by inheriting classes to perform tests.
    '''

    # Define a delimiter when reporting results
    DELIMITER = '|'
    
    # Define a prefix for reporting results
    PREFIX = 'RESULT'

    def __init__(self):
        # A list of things not to check when validating
        self.disableChecking = []
        # Whether or not to strip off whitespace when doing simple ascii diff
        self.stripWhitespace = True
        # Tolerance
        self.tolerance = 0.00000001
    
    def runTest(self):
        raise NotImplementedError('"runTest(self)" should be overridden in a derived class')

    def validate(self):
        '''
        Override this to provide a pair of workspaces which should be checked for equality
        by the doValidation method.
        The overriding method should return a pair of strings. This could be two workspace
        names, e.g. return 'workspace1','workspace2', or a workspace name and a nexus
        filename (which must have nxs suffix), e.g. return 'workspace1','GEM00001.nxs'.
        '''
        return None

    def validateMethod(self):
        '''
        Override this to specify which validation method to use. Look at the validate* methods to 
        see what allowed values are.
        '''
        return "WorkspaceToNeXus"

    def maxIterations(self):
        '''Override this to perform more than 1 iteration of the implemented test.'''
        return 1

    def reportResult(self, name, value):
        '''
        Send a result to be stored as a name,value pair
        '''
        print self.PREFIX + self.DELIMITER + name + self.DELIMITER + str(value) + '\n',
        
    def execute(self):
        '''
        Run the defined number of iterations of this test
        '''
        # Start timer
        start = time.time()
        countmax = self.maxIterations() + 1
        for i in range(1, countmax):
            istart = time.time()
            self.runTest()
            delta_t = time.time() - istart
            self.reportResult('iteration time_taken', str(i) + ' %.2f' % delta_t)
        delta_t = float(time.time() - start)
        # Finish
        #self.reportResult('time_taken', '%.2f' % delta_t)
        
    def __prepASCIIFile(self, filename):
        """
        Prepare an ascii file for comparison using difflib.
        """
        handle = open(filename, mode='r')
        stuff = handle.readlines()
        if self.stripWhitespace:
            stuff = [line.strip() for line in stuff]
        handle.close()
        return stuff

    def validateASCII(self):
        """
        Validate ASCII files using difflib.
        """
        (measured, expected) = self.validate()
        measured = self.__prepASCIIFile(measured)
        expected = self.__prepASCIIFile(expected)

        # calculate the difference
        import difflib
        diff = difflib.Differ().compare(measured, expected)
        result = []
        for line in diff:
            if line.startswith('+') or line.startswith('-') or line.startswith('?'):
                result.append(line)

        # print the difference
        if len(result) > 0:
            if self.stripWhitespace:
                msg = "(whitespace striped from ends)"
            else:
                msg = ""
            print "******************* Difference in files", msg
            print "\n".join(result)
            print "*******************"
            return False
        else:
            return True

    def validateWorkspaceToNeXus(self):
        '''
        Assumes the second item from self.validate() is a nexus file and loads it 
        to compare to the supplied workspace.
        '''
        valNames = list(self.validate())
        from mantidsimple import LoadNexus, mtd
        workspace2 = valNames[1]
        if workspace2.endswith('.nxs'):
            LoadNexus(workspace2,"RefFile")
            workspace2 = "RefFile"
        else:
            raise RuntimeError("Should supply a NeXus file: %s" % workspace2)
        valNames[1] = "RefFile"
        return self.validateWorkspaces(valNames)

    def validateWorkspaceToWorkspace(self):
        '''
        Assumes the second item from self.validate() is an existing workspace
        to compare to the supplied workspace.
        '''
        valNames = list(self.validate())
        return self.validateWorkspaces(valNames)

    def validateWorkspaces(self, valNames=None):
        '''
        Performs a check that two workspaces are equal using the CheckWorkspacesMatch
        algorithm. Loads one workspace from a nexus file if appropriate.
        Returns true if: the workspaces match 
                      OR the validate method has not been overridden.
        Returns false if the workspace do not match. The reason will be in the log.
        '''
        if valNames is None:
            valNames = self.validate()

        from mantidsimple import SaveNexus, mtd
        checker = mtd.createAlgorithm("CheckWorkspacesMatch")
        checker.setPropertyValue("Workspace1",valNames[0])
        checker.setPropertyValue("Workspace2",valNames[1])
        checker.setPropertyValue("Tolerance", str(self.tolerance))
        for d in self.disableChecking:
            checker.setPropertyValue("Check"+d,"0")
        checker.execute()
        if checker.getPropertyValue("Result") != 'Success!':
            print self.__class__.__name__
            SaveNexus(valNames[0],self.__class__.__name__+'-mismatch.nxs')
            return False
                    
        return True

    def doValidation(self):
        """
        Perform validation. This selects which validation method to use by the result of validateMethod()
        and validate(). If validate() is not overridden this will return True.
        """
        # if no validation is specified then it must be ok
        if self.validate() == None:
            return True

        # switch based on validation methods
        method = self.validateMethod().lower()
        if "validateworkspacetonexus".endswith(method):
            return self.validateWorkspaceToNeXus()
        elif "validateworkspacetoworkspace".endswith(method):
            return self.validateWorkspaceToWorkspace()
        elif "validateascii".endswith(method):
            return self.validateASCII()
        else:
            raise RuntimeError("invalid validation method '%s'" % self.validateMethod())
    
    def returnValidationCode(self,code):
        """
        Calls doValidation() and returns 0 in success and code if failed. This will be used as return code
        from the calling python subprocess
        """
        if self.doValidation():
            return 0
        else:
            return code

    def cleanup(self):
        '''
        This function is called after a test has completed and can be used to clean up,
        i.e. remove workspaces etc
        '''
        pass
    
#########################################################################
# A class to store the results of a test 
#########################################################################
class TestResult(object):
    '''
    Stores the results of each test so that they can be reported later.
    '''
    
    def __init__(self):
        self._results = []
        self.name = ''
        self.filename = ''
        self.date = ''
        self.status = ''
        self.time_taken = ''
        self.total_time = ''
        self.output = ''
        self.err = ''
    
    def addItem(self, item):
        '''
        Add an item to the store, this should be a list containing 2 entries: [Name, Value]
        '''
        self._results.append(item)
        
    def resultLogs(self):
        '''
        Get the map storing the results
        '''
        return self._results

#########################################################################
# A base class to support report results in an appropriate manner
#########################################################################
class ResultReporter(object):
    '''
    A base class for results reporting. In order to get the results in an
    appropriate form, subclass this class and implement the dispatchResults 
    method.
    '''

    def __init__(self):
        '''Initialize a class instance, e.g. connect to a database'''
        pass

    def dispatchResults(self, result):
        raise NotImplementedError('"dispatchResults(self, result)" should be overridden in a derived class')

#########################################################################
# A class to report results as formatted text output
#########################################################################
class TextResultReporter(ResultReporter):
    '''
    Report the results of a test using standard out
    '''
    
    def dispatchResults(self, result):
        '''
        Print the results to standard out
        '''
        nstars = 30
        print '*' * nstars
        for t in result.resultLogs():
            print '\t' + str(t[0]).ljust(15) + '->  ', str(t[1])
        print '*' * nstars

#########################################################################
# A base class for a TestRunner
#########################################################################
class PythonTestRunner(object):
    '''
    A base class to serve as a wrapper to actually run the tests in a specific 
    environment, i.e. console, gui
    '''
    SEGFAULT_CODE = 139
    VALIDATION_FAIL_CODE = 99
    NOT_A_TEST = 98

    def __init__(self, need_escaping = False):
        self._mtdpy_header = ''
        self._test_dir = ''
        # Get the path that this module resides in so that the tests know about it
        self._framework_path = ''
        for p in sys.path:
            if 'Framework' in p:
                self._framework_path =  os.path.abspath(p).replace('\\','/')
        # A string to prefix the code with
        self._code_prefix = ''
        self._using_escape = need_escaping

    def commandString(self, pycode):
        '''
        Return the appropriate command to pass to subprocess.Popen
        '''
        raise NotImplementedError('"commandString(self)" should be overridden in a derived class')

    def setMantidDir(self, mtdheader_dir):
        # Store the path to MantidPythonAPI
        self._mtdpy_header = os.path.abspath(mtdheader_dir).replace('\\','/')

    def setTestDir(self, test_dir):
        self._test_dir = os.path.abspath(test_dir).replace('\\','/')

    def createCodePrefix(self):
        if self._using_escape == True:
            esc = '\\'
        else:
            esc = ''

        self._code_prefix = 'import sys, time\n'
        self._code_prefix += 'sys.path.insert(0, ' + esc + '"' + self._mtdpy_header + esc + '")\n' + \
        'sys.path.append(' + esc + '"' + self._framework_path + esc + '")\n' + \
        'sys.path.append(' + esc + '"' + self._test_dir + esc + '")\n' + \
        'from MantidFramework import *\n' + \
        'mtd.initialise()\n'
        
    def getCodePrefix(self):
        '''
        Return a prefix to the code that will be executed
        '''
        return self._code_prefix

    def spawnSubProcess(self, cmd):
        '''
        Spawn a new process and run the given command within it
        '''
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        std_out, std_err = proc.communicate()
        return proc.returncode, std_out, std_err 
    
    def start(self, pycode):
        '''
        Run the given test code in a new subprocess
        '''
        raise NotImplementedError('"run(self, pycode)" should be overridden in a derived class')
    
#########################################################################
# A runner class to execute the tests on using the command line interface
#########################################################################
class PythonConsoleRunner(PythonTestRunner):
    '''
    This class executes tests within a Mantid environment inside a standalone python
    interpreter
    '''
    
    def __init__(self):
        PythonTestRunner.__init__(self, True)

    def start(self, pycode):
        '''
        Run the code in a new instance of a python interpreter
        '''
        return self.spawnSubProcess('python -c \"' + self.getCodePrefix() + pycode + '\"')

#########################################################################
# A runner class to execute the tests on using the command line interface
#########################################################################
class MantidPlotTestRunner(PythonTestRunner):
    '''
    This class executes tests within the Python scripting environment inside 
    MantidPlot
    '''
    
    def __init__(self, mtdplot_dir):
        PythonTestRunner.__init__(self)
        mtdplot_bin = mtdplot_dir + '/MantidPlot'
        if os.name == 'nt':
            mtdplot_bin += '.exe'
        self._mtdplot_bin = os.path.abspath(mtdplot_bin).replace('\\','/')
        
    def start(self, pycode):
        '''
        Run the code in a new instance of the MantidPlot scripting environment
        '''
        # The code needs wrapping in a temporary file so that it can be passed to MantidPlot,
        # along with the redirection of the scripting output to stdout
        # On Windows, just using the file given back by tempfile doesn't work as the name is mangled to a short version where
        # all characters after a space are replace by ~. So on windows use put the file in the current directory
        if os.name == 'nt':
            loc = '.'
        else:
            loc = ''
        # MG 11/09/2009: I tried the simple tempfile.NamedTemporaryFile() method but this didn't work
        # on Windows so I had to be a little long winded about it
        fd, tmpfilepath = tempfile.mkstemp(suffix = '.py', dir = loc, text=True)

        os.write(fd, 'import sys\nsys.stdout = sys.__stdout__\n' + self.getCodePrefix() + pycode)
        retcode, output, err = self.spawnSubProcess('"' +self._mtdplot_bin + '" -xq \'' + tmpfilepath + '\'') 
        # Remove the temporary file
        os.close(fd)
        os.remove(tmpfilepath)
        return retcode, output, err
                
#########################################################################
# A class to tie together a test and its results
#########################################################################
class TestSuite(object):
    '''
    Tie together a test and its results.
    '''
    def __init__(self, modname, testname, filename = None):
        self._modname = modname
        self._fullname = modname + '.' + testname

        self._result = TestResult()
        # Add some results that are not linked to the actually test itself
        self._result.name = self._fullname
        if filename:
            self._result.filename = filename
        else:
            self._result.filename = self._fullname
        self._result.addItem(['test_name', self._fullname])
        sysinfo = platform.uname()
        self._result.addItem(['host_name', sysinfo[1]])
        self._result.addItem(['environment', self.envAsString()])

    def envAsString(self):
        if os.name == 'nt':
            system = platform.system().lower()[:3]
            arch = platform.architecture()[0][:2]
            env = system + arch
        elif os.name == 'mac':
            env = platform.mac_ver()[0]
        else:
            env = platform.dist()[0]
        return env

    def execute(self, runner):
        pycode = 'import ' + self._modname + '\n'\
                 + "from stresstesting import MantidStressTest\n"\
                 + "if not hasattr(" + self._fullname + ", 'execute') or not issubclass(" + self._fullname + ",MantidStressTest): sys.exit("+str(PythonTestRunner.NOT_A_TEST)+")\n"\
                 + "print time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime()) + ': Executing " + self._fullname + "'\n"\
                 + self._fullname + '().execute()\n'\
                 + 'retcode = '+self._fullname + '().returnValidationCode('+str(PythonTestRunner.VALIDATION_FAIL_CODE)+')\n'\
                 + 'sys.exit(retcode)'
        print pycode
        # Start the new process
        self._result.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._result.addItem(['test_date',self._result.date])
        retcode, output, err = runner.start(pycode)
        if retcode == 0:
            status = 'success'
        elif retcode == 1:
            # This is most likely an algorithm failure, but it's not certain
            status = 'algorithm failure'
        elif retcode == PythonTestRunner.VALIDATION_FAIL_CODE:
            status = 'failed validation'
        elif retcode == PythonTestRunner.SEGFAULT_CODE:
            status = 'crashed'
        elif retcode < 0:
            status = 'hung'
        else:
            status = 'unknown'

        # Check return code and add result
        self._result.status = status
        self._result.addItem(['status', status])
        # Dump std out so we know what happened
        print output
        self._result.output = output
        all_lines = output.split('\n')
        # Find the test results
        for line in all_lines:
            entries = line.split(MantidStressTest.DELIMITER)
            if len(entries) == 3 and entries[0] == MantidStressTest.PREFIX:
                self._result.addItem([entries[1], entries[2]])
                
    def reportResults(self, reporters):
        for r in reporters:
            r.dispatchResults(self._result)

#########################################################################
# The main API class
#########################################################################
class TestManager(object):
    '''A manager class that is responsible for overseeing the testing process. 
    This is the main interaction point for the framework.
    '''

    def __init__(self, test_loc, runner = PythonConsoleRunner(), output = [TextResultReporter()]):
        '''Initialize a class instance'''

        # Check whether the MANTIDPATH variable is set
        mtdheader_dir = os.getenv("MANTIDPATH")
        if mtdheader_dir is None:
            sys.exit('MANTIDPATH variable not be found. Please ensure Mantid is installed correctly.')

        # Runners and reporters    
        self._runner = runner
        self._reporters = output
        
        # Init mantid
        sys.path.append(os.path.abspath(mtdheader_dir).replace('\\','/'))
        runner.setMantidDir(mtdheader_dir)

        # If given option is a directory
        if os.path.isdir(test_loc) == True:
            test_dir = os.path.abspath(test_loc).replace('\\','/')
            sys.path.append(test_dir)
            runner.setTestDir(test_dir)
            self._tests = self.loadTestsFromDir(test_dir)
        else:
            if os.path.exists(test_loc) == False:
                print 'Cannot find file ' + test_loc + '.py. Please check the path.'
                exit(2)
            test_dir = os.path.abspath(os.path.dirname(test_loc)).replace('\\','/')
            sys.path.append(test_dir)
            runner.setTestDir(test_dir)
            self._tests = self.loadTestsFromModule(os.path.basename(test_loc))
            
        if len(self._tests) == 0:
            print 'No tests defined in ' + test_dir + '. Please ensure all test classes sub class stresstesting.MantidStressTest.'
            exit(2)

        # Create a prefix to use when executing the code
        runner.createCodePrefix()

    def executeTests(self):
        # Get the defined tests
        for suite in self._tests:
            suite.execute(self._runner)
            suite.reportResults(self._reporters)
         
    def loadTestsFromDir(self, test_dir):
        ''' Load all of the tests defined in the given directory'''
        entries = os.listdir(test_dir)
        tests = []
        regex = re.compile('^.*\.py$', re.IGNORECASE)
        for file in entries:
            if regex.match(file) != None:
                tests.extend(self.loadTestsFromModule(os.path.join(test_dir,file)))
        return tests

    def loadTestsFromModule(self, filename):
        '''
        Load test classes from the given module object which has been
        imported with the __import__ statement
        '''
        tests = []
        pyfile = open(filename, 'r')
        regex = re.compile('^class\s(.*)\(.*\)')
        #regex = re.compile('^class\s(.*)\(.*MantidStressTest\)')
        modname = os.path.basename(filename)
        modname = modname.split('.py')[0]
        for line in pyfile:
          matcher = regex.match(line)
          if matcher is None: continue
          if len(matcher.groups()) != 1: continue
          test_name = matcher.groups()[0]
          tests.append(TestSuite(modname, test_name, filename))

        return tests
