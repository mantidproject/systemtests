import stresstesting
import MantidFramework
MantidFramework.mtd.initialize()
from mantidsimple import *

class REFLReduction(stresstesting.MantidStressTest):
    def runTest(self):
        RefLReduction(RunNumbers=[int(70977)],
                     NormalizationRunNumber=70964,
                     SignalPeakPixelRange=[125, 135],
                     SubtractSignalBackground=True,
                     SignalBackgroundPixelRange=[122, 138],
                     NormFlag=True,
                     NormPeakPixelRange=[125, 135],
                     NormBackgroundPixelRange=[122, 138],
                     SubtractNormBackground=True,
                     LowResDataAxisPixelRangeFlag=True,
                     LowResDataAxisPixelRange=[115, 210],
                     LowResNormAxisPixelRangeFlag=True,
                     LowResNormAxisPixelRange=[115, 210],
                     TOFRange=[50343.0, 62140.0],
                     IncidentMediumSelected='H2O',
                     QMin=0.001,
                     QStep=-0.001,
                     AngleOffset=0.009,
                     AngleOffsetError=0.001,
                     OutputWorkspace='reflectivity_70977')
                
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "reflectivity_70977", 'REFLReduction.nxs'

