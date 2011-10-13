import stresstesting
from mantidsimple import *
from ISISCommandInterface import *

# Test is giving odd results on Linux, but only this 2D one.

xclass SANSLOQCan2D(stresstesting.MantidStressTest):
    
  def runTest(self):
  	  
    LOQ()
    Set2D()
    Detector("main-detector-bank")
    MaskFile('MASK.094AA')
    Gravity(True)

    AssignSample('99630.RAW')
    AssignCan('99631.RAW')
    
    WavRangeReduction(None, None, False)

    
  def validate(self):
    # Need to disable checking of the Spectra-Detector map because it isn't
    # fully saved out to the nexus file (it's limited to the spectra that
    # are actually present in the saved workspace).
    self.disableChecking.append('SpectraMap')
    self.disableChecking.append('Instrument')
    #when comparing LOQ files you seem to need the following
    self.disableChecking.append('Axes')

    return '99630main_2D_2.2_10.0','SANSLOQCan2D.nxs'
