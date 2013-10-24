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
    irf_file = 'arg_powder.irf'
    dat_file = 'arg_si.dat'
    bkgd_file = 'arg_si_bkgd_polynomial.nxs'

    def requiredFiles(self):
        files = [self.irf_file, self.dat_file, self.bkgd_file]
        return files

    def runTest(self):
        savedir = getSaveDir()

        LoadAscii(Filename=self.dat_file, OutputWorkspace='arg_si',Unit='TOF')

        LoadNexusProcessed(Filename=self.bkgd_file, OutputWorkspace='Arg_Si_Bkgd_Parameter')

        CreateLeBailFitInput(FullprofParameterFile=self.irf_file,
                GenerateBraggReflections='1',LatticeConstant='5.4313640',
                InstrumentParameterWorkspace='Arg_Bank1', BraggPeakParameterWorkspace='ReflectionTable')

        # run the actual code
	ExaminePowderDiffProfile(
	    InputWorkspace      = 'arg_si',
            StartX              = 1990.,
            EndX                = 29100.,
            ProfileType         = 'Back-to-back exponential convoluted with PseudoVoigt',
            ProfileWorkspace    = 'Arg_Bank1',
            BraggPeakWorkspace  = 'ReflectionTable',
            BackgroundParameterWorkspace = 'Arg_Si_Bkgd_Parameter',
            BackgroundType      = 'Polynomial',
            BackgroundWorkspace = 'Arg_Si_Background',
            OutputWorkspace     = 'Arg_Si_Calculated')


        # load output gsas file and the golden one
	Load(Filename = "Arg_Si_ref.nxs", OutputWorkspace = "Arg_Si_golden")

    def validateMethod(self):
        self.tolerance=1.0e-6
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        self.tolerance=1.0e-6
        return ('Arg_Si_Calculated','Arg_Si_golden')


