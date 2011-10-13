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

def locateSourceDir():
    loc = os.path.abspath(__file__)
    return os.path.split(loc)[0] # get the directory

def locateStressTestFramework():
    loc = locateSourceDir()
    (parent, curdir) = os.path.split(loc)
    if curdir == "SystemTests":
        loc = os.path.join(loc, "../../Code/Tools/StressTestFramework")
    else:
        raise RuntimeError("Failed to find scripts directory from '%s'" % loc)
    loc = os.path.abspath(loc)
    return loc

def setDataDirs(mtd):
    # get the file of the python script
    sourceDir = locateSourceDir()
    testDir = os.path.split(sourceDir)[0]

    # add things to the data search path
    mtd.settings.appendDataSearchDir(os.path.join(testDir, "Data"))
    mtd.settings.appendDataSearchDir(os.path.join(testDir,
                             "SystemTests/AnalysisTests/ReferenceResults"))
    mtd.settings.appendDataSearchDir(os.path.join(testDir, "Data/LOQ"))
    mtd.settings.appendDataSearchDir(os.path.join(testDir, "Data/SANS2D"))
    mtd.settings.appendDataSearchDir(os.path.join(testDir, "Data/Polref Scan"))
    mtd.settings.appendDataSearchDir(os.path.abspath(os.getenv("MANTIDPATH")))
