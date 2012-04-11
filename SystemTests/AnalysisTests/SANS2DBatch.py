import stresstesting
from mantidsimple import *
from ISISCommandInterface import *
from SANSBatchMode import *
import os.path

# test batch mode with sans2d and selecting a period in batch mode
class SANS2DBatch(stresstesting.MantidStressTest):
    
  def runTest(self):

    SANS2D()
    Set1D()
    Detector("rear-detector")
    MaskFile('MASKSANS2Doptions.091A')
    Gravity(True)
    
    csv_file = FileFinder.getFullPath('SANS2D_periodTests.csv')
    
    BatchReduce(csv_file, 'nxs', plotresults=False, saveAlgs={'SaveCanSAS1D':'xml','SaveNexus':'nxs'})
        
    os.remove(os.path.join(mtd.getConfigProperty('defaultsave.directory'),'5512p7_SANS2DBatch.xml'))
    
  def validate(self):
    # Need to disable checking of the Spectra-Detector map because it isn't
    # fully saved out to the nexus file (it's limited to the spectra that
    # are actually present in the saved workspace).
    self.disableChecking.append('SpectraMap')
    self.disableChecking.append('Axes')
    self.disableChecking.append('Instrument')
    
    return '5512p7_SANS2DBatch','SANS2DBatch.nxs'
