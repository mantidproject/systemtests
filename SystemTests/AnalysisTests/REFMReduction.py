import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *

class REFMReduction(stresstesting.MantidStressTest):
    def runTest(self):
          RefMReduction(RunNumbers=9709,
          NormalizationRunNumber=9684,
          SignalPeakPixelRange=[216, 224],
          SubtractSignalBackground=True,
          SignalBackgroundPixelRange=[172, 197],
          PerformNormalization=True,
          NormPeakPixelRange=[226, 238],
          NormBackgroundPixelRange=[130, 183],
          SubtractNormBackground=False,
          CropLowResDataAxis=True,
          LowResDataAxisPixelRange=[86, 159],
          CropLowResNormAxis=False,
          NBins=40,
          Theta=0.086,
          OutputWorkspace='reflectivity_Off_Off_9709')
                
    def validate(self):
        # Be more tolerant with the output, mainly because of the errors.
        # The following tolerance check the errors up to the third digit.   
        self.tolerance = 0.1
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "reflectivity_Off_Off_9709", 'REFMReduction_off_off.nxs'

