import stresstesting
from mantid.simpleapi import *

class SANSSolidAngleCorrectionTest(stresstesting.MantidStressTest):

    def runTest(self):
        LoadSpice2D(Filename="BioSANS_exp61_scan0004_0001.xml", OutputWorkspace="wav")
        MoveInstrumentComponent(Workspace="wav", ComponentName="detector1", X=0.412, Y=0.00515)

        SANSSolidAngleCorrection(InputWorkspace="wav", OutputWorkspace="result")

        result = mtd["result"]
        self.assertTrue(result.getAxis(0).getUnit().unitID() == "Wavelength")

        self.tolerance = 1e-03
        self.disableChecking.append('Instrument')

    def validate(self):
        return ("result", "SANSSolidAngleCorrection.nxs")