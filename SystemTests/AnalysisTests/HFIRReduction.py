import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.hfir_command_interface import *
import math

TEST_DIR = "../Data/SANS2D/"

class HFIRReduction(stresstesting.MantidStressTest):
    """
        Simple reduction example
    """
    
    def runTest(self):

        mtd.settings['default.facility'] = 'HFIR'
        HFIRSANS()
        #DataPath(TEST_DIR)
        DirectBeamCenter("BioSANS_empty_cell.xml")
        AppendDataFile("BioSANS_test_data.xml")
        SetTransmission(0.51944, 0.011078)
        SensitivityCorrection("BioSANS_flood_data.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
        
        #SaveAscii(Filename="tmp.txt", InputWorkspace="BioSANS_test_data_Iq")
        #LoadAscii('tmp.txt', "output")
        #LoadAscii('AnalysisTests/ReferenceResults/BioSANS_test_data_Iq.txt', "ref")

    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", "HFIRReduction.nxs"
