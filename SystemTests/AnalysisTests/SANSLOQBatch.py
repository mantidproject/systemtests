import stresstesting
from mantidsimple import *
from ISISCommandInterface import *
from SANSBatchMode import *
import os.path

class SANSLOQBatch(stresstesting.MantidStressTest):
    
  def runTest(self):
    #DataPath("../Data/LOQ/")
    #UserPath("../Data/LOQ/")

    #here we are testing the LOQ setup
    LOQ()
    #rear detector
    Detector("main-detector-bank")
    #test batch mode, although only the analysis from the last line is checked
    # Find the file , this should really be in the BatchReduce reduction step
    csv_file = FileFinder.getFullPath('batch_input.csv')
    
    Set1D()
    MaskFile('MASK.094AA')
    Gravity(True)
    
    BatchReduce(csv_file, 'raw', plotresults=False, saveAlgs={'SaveCanSAS1D':'xml','SaveNexus':'nxs'})
        
    LoadNexus('54433sans.nxs', 'result')
    Plus('result', '99630sanotrans', 'result')

    os.remove(mtd.getConfigProperty('defaultsave.directory')+'54433sans.nxs')
    os.remove(mtd.getConfigProperty('defaultsave.directory')+'99630sanotrans.nxs')
    os.remove(mtd.getConfigProperty('defaultsave.directory')+'54433sans.xml')
    os.remove(mtd.getConfigProperty('defaultsave.directory')+'99630sanotrans.xml')
    
  def validate(self):
    # Need to disable checking of the Spectra-Detector map because it isn't
    # fully saved out to the nexus file (it's limited to the spectra that
    # are actually present in the saved workspace).
    self.disableChecking.append('SpectraMap')
    self.disableChecking.append('Axes')
    self.disableChecking.append('Instrument')
    
    return 'result','SANSLOQBatch.nxs'
