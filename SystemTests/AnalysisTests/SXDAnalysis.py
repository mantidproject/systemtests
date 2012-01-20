import stresstesting
from mantidsimple import *

class SXDAnalysis(stresstesting.MantidStressTest):
    """
    Start of a system test for SXD data analyiss
    """
    
    def runTest(self):
        # Limit mem usage as it kills our 32 bit machine when running
        #ConvertToDiffractionMDWorkspace and we have no file backend
        LoadRaw(Filename=r'SXD23767.raw',OutputWorkspace='SXD23767',Cache='Always',
                LoadLogFiles='0',LoadMonitors='Exclude', SpectrumMax=20564) 
        # Ticket #4527: This step would fail occasionally.
        ConvertToDiffractionMDWorkspace(InputWorkspace='SXD23767',OutputWorkspace='QLab',LorentzCorrection='1',SplitInto='2',SplitThreshold='150')
        FindPeaksMD(InputWorkspace='QLab',PeakDistanceThreshold='0.9',MaxPeaks='100',OutputWorkspace='peaks')
        # TODO: Add more validation. For now, the peaks that are found do not form a nice lattice. 
        
    def doValidation(self):
        # If we reach here, no validation failed
        return True
