import stresstesting
from mantidsimple import *
import sys

class PG3Calibration(stresstesting.MantidStressTest):

    def skipTests(self):
        # We skip this test if the system is not Linux for the moment
        if sys.platform.startswith('win') or sys.platform == 'darwin':
          return True
        else:
          return False


    def requiredFiles(self):
        files = ["PG3_2538_event.nxs","PG3_golden.cal"] 
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code
        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs='dspacemap and calibration', FilterBadPulses=True,
                          GroupDetectorsBy='All', DiffractionFocusWorkspace=False, Binning='0.5, -0.0015, 2.5', 
                          PeakPositions = '2.0592,1.2610,1.0754,0.8916,0.8182,0.7280,0.6864,0.6305,0.6029', 
                         CrossCorrelation =False, Instrument='PG3', RunNumber='2538', Extension='_event.nxs')
        Rebin(InputWorkspace='PG3_2538_calibrated', OutputWorkspace='PG3_2538_calibrated', Params='0.5, -0.0015, 2.5', PreserveEvents=False)

        # load the golden one
        LoadEventNexus(Filename='PG3_2538_event.nxs',OutputWorkspace='PG3_2538',Precount=True)
        LoadCalFile(InputWorkspace='PG3_2538', CalFileName='PG3_golden.cal', WorkspaceName='PG3_2538')
        FilterBadPulses(InputWorkspace='PG3_2538', OutputWorkspace='PG3_2538')
        CompressEvents(InputWorkspace='PG3_2538', OutputWorkspace='PG3_2538', Tolerance=0.01)
        MaskDetectors(Workspace='PG3_2538', MaskedWorkspace='PG3_2538_mask')
        AlignDetectors(InputWorkspace='PG3_2538', OutputWorkspace='PG3_2538', OffsetsWorkspace='PG3_2538_offsets')
        Rebin(InputWorkspace='PG3_2538', OutputWorkspace='PG3_2538', Params='0.5, -0.0015, 2.5', PreserveEvents=False)


    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        return ('PG3_2538_calibrated','PG3_2538')
