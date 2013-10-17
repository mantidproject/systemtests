########################################################################
#
# This is the system test for workflow algorithms
# 1. ExaminePowder...
# 2. SeqRefinement...
# Both of which are based on LeBailFit to do peak profile calibration
# for powder diffractometers.
#
########################################################################
import stresstesting
from mantid.simpleapi import *

def getSaveDir():
        """determine where to save - the current working directory"""
        import os
        return os.path.abspath(os.path.curdir)

class VulcanExamineProfile(stresstesting.MantidStressTest):
    irf_file = 'xxx.irf'
    hkl_file = 'xxx.hkl'
    dat_file = 'PG3_???.dat'

    def requiredFiles(self):
        files = [self.irf_file, self.hkl_file, self.dat_file]
        return files

    def runTest(self):
        savedir = getSaveDir()

        # run the actual code
	ExaminePowderDiffProfile(
	    InputFilename	= self.dat_file,
	    ProfileFilename	= self.irf_file,
	    ReflectonFilename	= self.hkl_file,
	    OutputWorkspacd	= "PG3_???_Calculated")


        # load output gsas file and the golden one
	Load(Filename = "PG3_???_ref.nxs", OutputWorkspace = "PG3_???_golden")

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        return ('PG3_???_Calculated','PG3_???_golden')


