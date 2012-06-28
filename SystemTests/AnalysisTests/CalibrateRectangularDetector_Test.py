import stresstesting
from mantidsimple import *
import datetime
from time import localtime, strftime
import os

class PG3Calibration(stresstesting.MantidStressTest):

    def requiredFiles(self):
        files = ["PG3_2538_event.nxs"] 
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code
        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs = 'calibration', FilterBadPulses = True,
                          GroupDetectorsBy = 'All', DiffractionFocusWorkspace = False, Binning = '0.5, -0.0008, 2.5', 
                          PeakPositions = '2.0592,1.2610,1.0754,0.8916,0.8182,0.7280,0.6864,0.6305,0.6029', 
                          CrossCorrelation = False, Instrument = 'PG3', RunNumber = '2538', Extension = '_event.nxs')

        # load saved cal file
        self.saved_cal_file = savedir+"/PG3_calibrate_d2538"+strftime("_%Y_%m_%d.cal")
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName=self.saved_cal_file, WorkspaceName="PG3_2538", 
            MakeGroupingWorkspace=False, MakeMaskWorkspace=False)
        # load golden cal file
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName="PG3_golden.cal", WorkspaceName="PG3_2538_golden", 
            MakeGroupingWorkspace=False, MakeMaskWorkspace=False)

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        self.tolerance = 1.0e-4
        return ('PG3_2538_offsets','PG3_2538_golden_offsets')

class PG3CCCalibration(stresstesting.MantidStressTest):

    def requiredFiles(self):
        files = ["PG3_2538_event.nxs"] 
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code

        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs = 'calibration', FilterBadPulses = True,
                          GroupDetectorsBy = 'All', DiffractionFocusWorkspace = False, Binning = '0.5, -0.0008, 2.5',
                          PeakPositions = '0.7282933,1.261441',DetectorsPeaks = '17,6',
                          CrossCorrelation = True, Instrument = 'PG3', RunNumber = '2538', Extension = '_event.nxs')

        # load saved cal file
        self.saved_cal_file = savedir+"/PG3_calibrate_d2538"+strftime("_%Y_%m_%d.cal")
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName=self.saved_cal_file, WorkspaceName="PG3_2538", 
            MakeGroupingWorkspace=False, MakeMaskWorkspace=False)
        # load golden cal file
        LoadCalFile(InputWorkspace="PG3_2538_calibrated", CalFileName="PG3_goldenCC.cal", WorkspaceName="PG3_2538_golden", 
            MakeGroupingWorkspace=False, MakeMaskWorkspace=False)

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        self.tolerance = 1.0e-4
        return ('PG3_2538_offsets','PG3_2538_golden_offsets')
