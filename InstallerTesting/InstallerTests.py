import os
import sys
import platform
import shutil
import subprocess
import glob
from getopt import getopt

'''

This script copies Mantid installer for the system it is running on from the build server,
installs it, runs system tests and produces an xml report file SystemTestsReport.xml

'''

try:
    opt,argv = getopt(sys.argv[1:],'noh')
except:
    opt = [('-h','')]

if ('-h','') in opt:
    print "Usage: %s [OPTIONS]" % os.path.basename(sys.argv[0])
    print
    print "Valid options are:"
    print "       -n Run tests without installing Mantid (it must be already installed)"
    print "       -o Output to the screen instead of log files"
    print "       -h Display the usage"
    sys.exit(0)

doInstall = True
if ('-n','') in opt:
    doInstall = False
out2stdout = False
if ('-o','') in opt:
    out2stdout = True

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
scriptLog = open(parentDir + '/logs/TestScript.log','w')
testRunLogPath = parentDir + '/logs/testsRun.log'
testRunErrPath = parentDir + '/logs/testsRun.err'

# Define useful functions

def stop():
    ''' Save the log, exit with error code 0 '''
    scriptLog.close()
    sys.exit(0)

def log(txt):
    ''' Write text to the script log file '''
    if txt and len(txt) > 0:
        scriptLog.write(txt)
        if not txt.endswith('\n'):
            scriptLog.write('\n')
        print txt

def failure():
    ''' Report failure of test(s), exit with code 1 '''
    log('Tests failed')
    print 'Tests failed'
    sys.exit(1)

def scriptfailure(txt):
    '''Report failure of this script, exit with code 1 '''
    if txt:
        log(txt)
    os.chdir(currentDir)
    scriptLog.close()
    sys.exit(1)

def run(cmd):
    ''' Run a command '''
    try:
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        out = p.communicate()[0]
        if p.returncode != 0:
            raise Exception('Returned with code '+str(p.returncode)+'\n'+out)
    except Exception,err:
        log('Error in subprocess '+cmd+':\n'+str(err))
        raise
    log(out)
    return out

def update(dir):
    '''Update a directory '''
    try:
        log("Updating "+dir)
        log(run('svn update ' + dir))
    except Exception, err:
        scriptfailure("Update failed: "+str(err))

class MantidInstaller:
    '''
    Class for copying and installing Mantid installer. 

    mantidInstaller :: name of the installer file
    mantidPlotPath :: path to installed MantidPlot executable
    '''
    def __init__(self):
        system = platform.system()
        arch = platform.architecture()
        dist = platform.dist()
        if system == 'Windows':
            self.mantidPlotPath = 'C:/MantidInstall/bin/MantidPlot.exe'
            pattern = 'mantid-*.msi'
            self.install = self.installWindows
        elif system == 'Linux':
            if dist[0] == 'Ubuntu':
                pattern = 'mantid_[0-9]*.deb'
                self.install = self.installUbuntu
            elif dist[0] == 'redhat' and (dist[1].startswith('5.') or dist[1].startswith('6.')):
                pattern = 'mantid-*.rpm'
                self.install = self.installRHEL
            else:
                raise RuntimeError('Unknown Linux flavour: %s' % str(dist))
            self.mantidPlotPath = '/opt/Mantid/bin/MantidPlot'
        elif system == 'Darwin':
            pattern = 'mantid-*.dmg'
            self.mantidPlotPath = '/Applications/MantidPlot.app/Contents/MacOS/MantidPlot'
            self.install = self.installDarwin
        else:
            scriptfailure('Unsupported platform ' + platform.system())
        # Glob for packages
        matches = glob.glob(os.path.abspath(pattern))
        if len(matches) > 0: # Take the last one as it should have the highest version number
            self.mantidInstaller = matches[-1]
        else:
            scriptfailure('Unable to find installer package in "%s"' % os.getcwd())

    '''
    Implementations of install() method for different systems
    '''

    def installWindows(self):
        # ADDLOCAL=ALL installs any optional features as well
        run('msiexec /quiet /i '+ self.mantidInstaller + ' ADDLOCAL=ALL')

    def installUbuntu(self):
        run('sudo gdebi -n ' + self.mantidInstaller)

    def installRHEL(self):
        try:
            run('sudo rpm --upgrade ' + self.mantidInstaller)
        except Exception, exc:
            # This reports an error if the same package is already installed
            if 'is already installed' in str(exc):
                log("Current version is up-to-date, continuing.\n")
                pass
            else:
                raise

    def installDarwin(self):
        run('hdiutil attach '+ self.mantidInstaller)
        mantidInstallerName = os.path.basename(self.mantidInstaller)
        mantidInstallerName = mantidInstallerName.replace('.dmg','')
        run('sudo installer -pkg /Volumes/'+ mantidInstallerName+'/'+ mantidInstallerName+'.pkg -target "/"')
        run('hdiutil detach /Volumes/'+ mantidInstallerName+'/')

log('Starting system tests')
installer = MantidInstaller()
log("Using installer '%s'" % os.path.join(os.getcwd(), installer.mantidInstaller))

# Install the found package
if doInstall:
    log("Installing package '%s'" % installer.mantidInstaller)
    try:
        installer.install()
    except Exception,err:
        scriptfailure("Installing failed. "+str(err))

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
        scriptfailure('Directory ' + dir + ' was not found.')
    search_dir = dir.replace('\\','/')
    if not search_dir.endswith('/'):
        search_dir += '/'
	data_path += search_dir + ';'
mtd.settings['datasearch.directories'] = data_path
# Save path
mtd.settings['defaultsave.directory'] = saveDir
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
    scriptfailure('Version test failed: '+str(err))

log("Running system tests. Log files are: logs/testsRun.log and logs/testsRun.err")
try:
    if out2stdout:
        p = subprocess.Popen('python runSystemTests.py --disablepropmake',shell=True) # no PIPE: print on screen for debugging
        p.wait()
    else:
        p = subprocess.Popen('python runSystemTests.py',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out,err = p.communicate() # waits for p to finish
        testsRunLog = open(testRunLogPath,'w')
        if out:
            testsRunLog.write(out)
        testsRunLog.close()
        testsRunErr = open(testRunErrPath,'w')
        if err:
            testsRunErr.write(err)
        testsRunErr.close()
    if p.returncode != 0:
        failure()
except:
    failure()

# Test run completed successfully
stop()
