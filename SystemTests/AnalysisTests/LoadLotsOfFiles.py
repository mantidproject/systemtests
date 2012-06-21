from mantid.simpleapi import *
import os
import re
import stresstesting

BANNED_FILES = ['992 Descriptions.txt',
                'BioSANS_dark_current.xml',
                'BioSANS_empty_cell.xml',
                'BioSANS_empty_trans.xml',
                'BioSANS_exp61_scan0004_0001.xml',
                'BioSANS_flood_data.xml',
                'BioSANS_sample_trans.xml',
                'BioSANS_test_data.xml',
                'eqsans_configuration.1463',
                'FLAT_CELL.061',
                'batch_input.csv',
                'mar11015.msk',
                'mari_res.map',
                'MASK.094AA',
                'MASKSANS2D_094i_RKH.txt',
                'MASKSANS2D.091A',
                'MASKSANS2Doptions.091A',
                'PG3_characterization_2011_08_31-HR.txt',
                'REF_M_9684_event.nxs',
                'REF_M_9709_event.nxs',
                'SANS2D_periodTests.csv',
                'SANS2D_992_91A.csv',
                'testCansas1DMultiEntry.xml',
                'Wish_Diffuse_Scattering_ISAW_UB.mat']

EXPECTED_EXT = '.expected'

BANNED_REGEXP = [r'SANS2D\d+.log$',
                 r'SANS2D00000808_.+.txt$']

def useDir(direc):
    """Only allow directories that aren't test output or 
    reference results."""
    if "ReferenceResults" in direc:
        return False
    if "logs" in direc:
        return False
    return ("Data" in direc)

def useFile(direc, filename):
    """Returns (useFile, abspath)"""
    # list of explicitly banned files at the top of this script
    if filename in BANNED_FILES:
        return (False, filename)

    # is an 'expected' file
    if filename.endswith(EXPECTED_EXT):
        return (False, filename)

    # list of banned files by regexp
    for regexp in BANNED_REGEXP:
        if re.match(regexp, filename) is not None:
            return (False, filename)

    filename = os.path.join(direc, filename)
    if os.path.isdir(filename):
        return (False, filename)
    return (True, filename)

class LoadLotsOfFiles(stresstesting.MantidStressTest):
    def __getDataFileList__(self):
        # get a list of directories to look in
        dirs = config['datasearch.directories'].split(';')
        dirs = [item for item in dirs if useDir(item)]
        print "Looking for data files in:", ', '.join(dirs)

        # get the list of files
        files = []
        for direc in dirs:
            myFiles = os.listdir(direc)
            for filename in myFiles:
                (good, filename) = useFile(direc, filename)
                print "***", good, filename
                if good:
                    files.append(filename)
        files.sort()
        return files

    def __runExtraTests__(self, wksp, filename):
        """Runs extra tests that are specified in '.expected' files
        next to the data files"""
        expected = filename + EXPECTED_EXT
        if not os.path.exists(expected): #file exists
            return True
        if os.path.getsize(expected) <= 0: #non-zero length
            return True

        # TODO Everything else
        return False

    def __loadAndTest__(self, filename):
        """Do all of the real work of loading and testing the file"""
        print "----------------------------------------"
        print "Loading '%s'" % filename
        wksp = Load(filename)
        if wksp is None:
            return False

        # generic checks
        if wksp.getName() is None or len(wksp.getName()) <= 0:
            print "Workspace does not have a name"
            del wksp
            return False

        id = wksp.id()
        print id, "***", dir(wksp) # REMOVE?
        if id is None or len(id) <= 0:
            print "Workspace does not have an id"
            del wksp
            return False

        # rest switches based on workspace type
        if id == "WorkspaceGroup":
            # groups have no histograms
            #    and take no memory
            pass
        else:
            if wksp.getNumberHistograms() <= 0:
                print "Workspace has zero histograms"
                del wksp
                return False
            if wksp.getMemorySize() <= 0:
                print "Workspace takes no memory"
                del wksp
                return False

        # checks for EventWorkspace
        if id == "EventWorkspace":
            if wksp.getNumberEvents() <= 0:
                print "EventWorkspace does not have events"
                del wksp
                return False

        # do the extra checks
        result = self.__runExtraTests__(wksp, filename)

        # cleanup
        del wksp
        return result

    def runTest(self):
        """Main entry point for the test suite"""
        files = self.__getDataFileList__()

        # run the tests
        failed = []
        for filename in files:
            try:
                if not self.__loadAndTest__(filename):
                    print "FAILED TO LOAD '%s'" % filename
                    failed.append(filename)
            except Exception, e:
                print "FAILED TO LOAD '%s' WITH ERROR:" % filename
                print e
                failed.append(filename)

        # final say on whether or not it 'worked'
        print "----------------------------------------"
        if len(failed) != 0:
            print "SUMMARY OF FAILED FILES"
            for filename in failed:
                print filename
            raise RuntimeError("Failed to load %d of %d files" \
                                   % (len(failed), len(files)))
        else:
            print "Succesfully loaded %d files" % len(files)
