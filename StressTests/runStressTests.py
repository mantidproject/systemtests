#!/usr/bin/env python
import getopt

# Define some necessary paths. The defaults are those of the repository
test_loc = './MantidScript'
stressmodule_dir = '../../Code/Tools/StressTestFramework'
mtdpy_header_dir = '../../Code/Mantid/Bin/Shared'

def usage():
    print 'Usage: runStressTests [options] [file|directory]\n\n' +\
        '[file|directory]\t\tRun either a set tests in a given file or all \n' + \
        '                \t\ttests in a given directory. The default behaviour\n'  + \
        '                \t\truns all tests in ' + test_loc + '\n'\
        'Options:\n' + \
        '\t--output=\t\tThe location to send the output. Supported options are text and db,\n' + \
        '         \t\tfor example --output=text,db will send results to the console and database\n' + \
        '\t--gui\t\tRun tests in MantidPlot script environment'


# Import the stress manager definition
import sys
sys.path.append(stressmodule_dir)
import stresstesting
import sqlresultreporter

reporters = [stresstesting.TextResultReporter()]
runner = stresstesting.PythonConsoleRunner()
# Get the command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "output=", "gui"])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '--help' or o == '-h':
        usage()
        exit(0)
    elif o == '--gui':
        runner = stresstesting.MantidPlotTestRunner(mtdpy_header_dir)
    elif o == '--output':
        reporters = []
        methods = a.split(',')
        ntext = 0
        ndb = 0
        for i in methods:
            if i == 'text':
                if ntext != 0:
                    continue
                reporters.append(stresstesting.TextResultReporter())
                ntext = 1
            elif i == 'db' or i == 'database':
                if ndb != 0:
                    continue
                reporters.append(stresstesting.SQLResultReporter())
                ndb = 1
            else:
                usage()
                exit('Error: option ' + i + ' not recognized')
    else:
        assert False

if len(args) == 0:
    pass;
elif len(args) == 1:
    test_loc = args[0]
else:
    usage()
    exit('Error: Incorrect number of arguments passed')

mgr = stresstesting.TestManager(test_loc, mtdpy_header_dir, runner = runner, output = reporters)
mgr.executeTests()
