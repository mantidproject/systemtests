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
        ConvertToDiffractionMDWorkspace(InputWorkspace='SXD23767',OutputWorkspace='QLab',LorentzCorrection='1',SplitInto='2',SplitThreshold='50')
        
        FindPeaksMD(InputWorkspace='QLab',PeakDistanceThreshold='1',MaxPeaks='60',DensityThresholdFactor=300,OutputWorkspace='peaks')
        
        # A basic check that peak finding was possible. We don't do much more than this with SXD in mantid at this point.
        peaks = mtd['peaks']
        self.assertEqual(60, peaks.rowCount())
        
    def doValidation(self):
        # If we reach here, no validation failed
        return True
