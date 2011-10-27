import os
import sys

def setMantidPath(directory = None):
    # force the environment variable
    if directory is not None:
        os.environ['MANTIDPATH'] = directory
    # add it to the python path
    directory = os.getenv("MANTIDPATH")
    if directory is None:
        raise RuntimeError("MANTIDPATH not found.")
    else:
        sys.path.append(directory)

    # add location of stress tests
    stressmodule_dir = locateStressTestFramework()
    sys.path.append(stressmodule_dir)

    # add location of the analysis tests
    tests_dir = locateTestsDir()
    sys.path.insert(0,tests_dir)

def locateSourceDir():
    loc = os.path.abspath(__file__)
    return os.path.split(loc)[0] # get the directory

def locateStressTestFramework():
    loc = locateSourceDir()
    (parent, curdir) = os.path.split(loc)
    if curdir == "SystemTests":
        loc = os.path.join(loc, "../StressTestFramework")
    else:
        raise RuntimeError("Failed to find scripts directory from '%s'" % loc)
    loc = os.path.abspath(loc)
    if os.path.isdir(loc):
        return loc
    else:
        raise RuntimeError("'%s' is not a directory (StressTestFramework)" \
                               % loc)

def locateTestsDir():
    loc = os.path.join(locateSourceDir(), 'AnalysisTests')
    loc = os.path.abspath(loc)
    if os.path.isdir(loc):
        return loc
    else:
        raise RuntimeError("'%s' is not a directory (AnalysisTests)" % loc)


def setDataDirs(mtd):
    for direc in getDataDirs():
        mtd.settings.appendDataSearchDir(direc)

def getDataDirs():
    # get the file of the python script
    sourceDir = locateSourceDir()
    testDir = os.path.split(sourceDir)[0]

    # add things to the data search path
    dirs =[]
    dirs.append(os.path.join(testDir, "Data"))
    dirs.append(os.path.join(testDir, "Data/LOQ"))
    dirs.append(os.path.join(testDir, "Data/SANS2D"))
    dirs.append(os.path.join(testDir, "SystemTests"))
    dirs.append(os.path.join(testDir,
                             "SystemTests/AnalysisTests/ReferenceResults"))
    dirs.append(os.path.abspath(os.getenv("MANTIDPATH")))

    dirs = [os.path.normpath(item) for item in dirs]

    return dirs
