import stresstesting
from mantidsimple import *
import datetime
from time import localtime, strftime

import sys
import os

class PG3Calibration(stresstesting.MantidStressTest):

    def skipTests(self):
        # We skip this test if the system is not Linux for the moment
        system = os.uname()
        if sys.platform.startswith('win') or sys.platform == 'darwin' or 'Ubuntu' in system[3]:
          return True
        else:
          return False


    def requiredFiles(self):
        files = ["PG3_2538_event.nxs"] 
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code
        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs = 'dspacemap and calibration', FilterBadPulses = True,
                          GroupDetectorsBy = 'All', DiffractionFocusWorkspace = False, Binning = '0.5, -0.0004, 2.5', 
                          PeakPositions = '2.0592,1.2610,1.0754,0.8916,0.8182,0.7280,0.6864,0.6305,0.6029', 
                          CrossCorrelation = False, Instrument = 'PG3', RunNumber = '2538', Extension = '_event.nxs')
        self.saved_cal_file = savedir+"/PG3_calibrate_d2538"+strftime("_%Y_%m_%d.cal")
        # delete first line with date and time
        f = open( self.saved_cal_file, 'r' )
        lines = f.readlines()
        f.close()

        f = open( self.saved_cal_file, 'w' )
        f.write( ''.join( lines[1:] ) )
        f.close()


    def validateMethod(self):
        return "ValidateASCII"

    def validate(self):
        return self.saved_cal_file, \
            os.path.join(os.path.dirname(__file__), 'ReferenceResults','PG3_golden.cal')

class PG3CCCalibration(stresstesting.MantidStressTest):

    def skipTests(self):
        # We skip this test if the system is not Linux for the moment
        if sys.platform.startswith('win') or sys.platform == 'darwin':
          return True
        else:
          return False
 

    def requiredFiles(self):
        files = ["PG3_2538_event.nxs"] 
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code

        CalibrateRectangularDetectors(OutputDirectory = savedir, SaveAs = 'dspacemap and calibration', FilterBadPulses = True,
                          GroupDetectorsBy = 'All', DiffractionFocusWorkspace = False, Binning = '0.5, -0.0004, 2.5',
                          PeakPositions = '0.7282933,1.261441',DetectorsPeaks = '17,6',
                          CrossCorrelation = True, Instrument = 'PG3', RunNumber = '2538', Extension = '_event.nxs')

        self.saved_cal_file = savedir+"/PG3_calibrate_d2538"+strftime("_%Y_%m_%d.cal")
        # delete first line with date and time
        f = open( self.saved_cal_file, 'r' )
        lines = f.readlines()
        f.close()

        f = open( self.saved_cal_file, 'w' )
        f.write( '\n'.join( lines[1:] ) )
        f.close()


    def validateMethod(self):
        return "ValidateASCII"

    def validate(self):
        return self.saved_cal_file, \
            os.path.join(os.path.dirname(__file__), 'ReferenceResults','PG3_goldenCC.cal')
