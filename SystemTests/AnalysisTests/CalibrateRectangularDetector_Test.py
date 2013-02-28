import stresstesting
from mantidsimple import *
import datetime
from time import localtime, strftime
import os

def _skip_test():
    """Helper function to determine if we run the test"""
    import platform
    # Only runs on RHEL6 at the moment
    if "Linux" not in platform.platform():
        return False # Return to True if test fails on Windows
    flavour = platform.linux_distribution()[2]
    if flavour == 'Santiago': # Codename for RHEL6
        return False # Do not skip
    else:
        return False # Return to True if test fails on other Linux

class PG3Calibration(stresstesting.MantidStressTest):

    def skipTests(self):
        return _skip_test()

    def requiredFiles(self):
        files = ["PG3_2538_event.nxs"] 
        return files

    def requiredMemoryMB(self):
        """Requires 3Gb"""
        return 3000

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code
        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs = 'calibration', FilterBadPulses = True,
                          GroupDetectorsBy = 'All', DiffractionFocusWorkspace = False, Binning = '0.5, -0.0004, 2.5', 
                          MaxOffset=0.01, PeakPositions = '2.0592,1.2610,1.0754,0.7280', 
                          CrossCorrelation = False, Instrument = 'PG3', RunNumber = '2538', Extension = '_event.nxs')

        # load saved cal file
        self.saved_cal_file = savedir+"/PG3_calibrate_d2538"+strftime("_%Y_%m_%d.cal")
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName=self.saved_cal_file, WorkspaceName="PG3_2538", 
            MakeGroupingWorkspace=False)
        MaskDetectors(Workspace="PG3_2538_offsets",MaskedWorkspace="PG3_2538_mask")
        # load golden cal file
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName="PG3_golden.cal", WorkspaceName="PG3_2538_golden", 
            MakeGroupingWorkspace=False)
        MaskDetectors(Workspace="PG3_2538_golden_offsets",MaskedWorkspace="PG3_2538_golden_mask")

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        self.tolerance = 1.0e-4
        return ('PG3_2538_offsets','PG3_2538_golden_offsets')

class PG3CCCalibration(stresstesting.MantidStressTest):

    def skipTests(self):
        return _skip_test()

    def requiredFiles(self):
        files = ["PG3_2538_event.nxs"] 
        return files

    def requiredMemoryMB(self):
        """Requires 3Gb"""
        return 3000

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code

        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs = 'calibration', FilterBadPulses = True,
                          GroupDetectorsBy = 'All', DiffractionFocusWorkspace = False, Binning = '0.5, -0.0004, 2.5',
                          MaxOffset=0.01, PeakPositions = '0.7282933,1.261441',DetectorsPeaks = '17,6',
                          CrossCorrelation = True, Instrument = 'PG3', RunNumber = '2538', Extension = '_event.nxs')

        # load saved cal file
        self.saved_cal_file = savedir+"/PG3_calibrate_d2538"+strftime("_%Y_%m_%d.cal")
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName=self.saved_cal_file, WorkspaceName="PG3_2538", 
            MakeGroupingWorkspace=False)
        MaskDetectors(Workspace="PG3_2538_offsets",MaskedWorkspace="PG3_2538_mask")
        # load golden cal file
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName="PG3_goldenCC.cal", WorkspaceName="PG3_2538_golden", 
            MakeGroupingWorkspace=False)
        MaskDetectors(Workspace="PG3_2538_golden_offsets",MaskedWorkspace="PG3_2538_golden_mask")

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        self.tolerance = 1.0e-4
        return ('PG3_2538_offsets','PG3_2538_golden_offsets')
