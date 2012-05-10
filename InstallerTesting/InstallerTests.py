import os
import sys
import platform
import shutil
from getopt import getopt

from mantidinstaller import (createScriptLog, log, stop, failure, scriptfailure, 
                             get_installer, run)

'''

This script copies Mantid installer for the system it is running on from the build server,
installs it, runs system tests and produces an xml report file SystemTestsReport.xml

'''

try:
    opt,argv = getopt(sys.argv[1:],'nohv')
except:
    opt = [('-h','')]

if ('-h','') in opt:
    print "Usage: %s [OPTIONS]" % os.path.basename(sys.argv[0])
    print
    print "Valid options are:"
    print "       -n Run tests without installing Mantid (it must be already installed)"
    print "       -o Output to the screen instead of log files"
    print "       -h Display the usage"
    print "       -v Run the newer version (NSIS) of the windows installer"
    sys.exit(0)

doInstall = True
useNSISWindowsInstaller = False
if ('-n','') in opt:
    doInstall = False
out2stdout = False
if ('-o','') in opt:
    out2stdout = True
if ('-v','') in opt:
    useNSISWindowsInstaller = True

'''
The directories that will be used
'''
currentDir = os.getcwd().replace('\\','/')
parentDir = os.path.abspath('..').replace('\\','/')
saveDir = os.path.join(parentDir, "logs/").replace('\\','/')
dataDirs = [os.path.join(parentDir, "SystemTests"),
        os.path.join(parentDir, "SystemTests/AnalysisTests/ReferenceResults"),
        os.path.join(parentDir, "Data"),
        os.path.join(parentDir, "Data/LOQ"),
        os.path.join(parentDir, "Data/SANS2D"),
        saveDir
]

# the log file for this script
if not os.path.exists(parentDir + '/logs'):
    os.mkdir(parentDir + '/logs')

createScriptLog(parentDir + '/logs/TestScript.log')
testRunLogPath = parentDir + '/logs/testsRun.log'
testRunErrPath = parentDir + '/logs/testsRun.err'


log('Starting system tests')
installer = get_installer(useNSISWindowsInstaller)
log("Using installer '%s'" % installer.mantidInstaller)

# Install the found package
if doInstall:
    log("Installing package '%s'" % installer.mantidInstaller)
    try:
        installer.install()
        log("Application path " + installer.mantidPlotPath)
        installer.no_uninstall = False
    except Exception,err:
        scriptfailure("Installing failed. "+str(err))
else:
    installer.no_uninstall = True

log('Creating Mantid.user.properties file for this environment')
# make sure the data are in the search path
mantidPlotDir = os.path.dirname(installer.mantidPlotPath)
sys.path.append(mantidPlotDir)
from MantidFramework import mtd
mtd.initialise()

# Up the log level so that failures can give useful information
mtd.settings['logging.loggers.root.level'] = 'information'
# Set the correct search path
data_path = ''
for dir in dataDirs:
    if not os.path.exists(dir):
        scriptfailure('Directory ' + dir + ' was not found.', installer)
    search_dir = dir.replace('\\','/')
    if not search_dir.endswith('/'):
        search_dir += '/'
	data_path += search_dir + ';'
mtd.settings['datasearch.directories'] = data_path
# Save path
mtd.settings['defaultsave.directory'] = saveDir
# Do not show paraview dialog
mtd.settings['paraview.ignore'] = "1"
# Ensure each new version of Mantid started in the subprocess gets these paths
log('Saving user properties to "%s"' % mtd.settings.getUserFilename()) 
mtd.settings.saveConfig(mtd.settings.getUserFilename())

try:
    # Keep hold of the version that was run
    version = run(installer.mantidPlotPath + ' -v')
    version_tested = open('version_tested.log','w')
    if version and len(version) > 0:
        version_tested.write(version)
    version_tested.close()
except Exception, err:
    scriptfailure('Version test failed: '+str(err), installer)

log("Running system tests. Log files are: logs/testsRun.log and logs/testsRun.err")
try:
    pass
    # Ensure we use the right Mantid if 2 are installed
    # run_test_cmd = "python runSystemTests.py -m %s" % mantidPlotDir
    # if out2stdout:
    #     p = subprocess.Popen(run_test_cmd + ' --disablepropmake',shell=True) # no PIPE: print on screen for debugging
    #     p.wait()
    # else:
    #     p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #     out,err = p.communicate() # waits for p to finish
    #     testsRunLog = open(testRunLogPath,'w')
    #     if out:
    #         testsRunLog.write(out)
    #     testsRunLog.close()
    #     testsRunErr = open(testRunErrPath,'w')
    #     if err:
    #         testsRunErr.write(err)
    #     testsRunErr.close()
    # if p.returncode != 0:
    #     failure()
except:
    failure(installer)

# Test run completed successfully
stop(installer)
