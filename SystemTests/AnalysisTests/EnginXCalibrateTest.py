import stresstesting
from mantid.simpleapi import *

class EnginXCalibrateTest(stresstesting.MantidStressTest):
  
    def runTest(self):
      positions = EnginXCalibrateFull(CalibrationRun = 'ENGINX00193749.nxs',
                                      Bank = 1,
                                      ExpectedPeaks = '1.3529, 1.6316, 1.9132')

      (self.difc, self.zero) = EnginXCalibrate(CalibrationRun = 'ENGINX00193749.nxs',
                                               Bank = 1,
                                               ExpectedPeaks = '2.7057,1.9132,1.6316,1.5621,1.3528,0.9566',
                                               DetectorPositions = positions)

    def validate(self):
      self.assertDelta(self.difc, 18404.522, 0.001)
      self.assertDelta(self.zero, 4.426, 0.001)

    def cleanup(self):
      mtd.remove('positions')
