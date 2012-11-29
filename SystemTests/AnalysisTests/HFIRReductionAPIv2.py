import stresstesting
import mantid
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.hfir_command_interface import *

class HFIRReductionAPIv2(stresstesting.MantidStressTest):
    """
        Simple reduction example
    """
    
    def runTest(self):

        config = ConfigService.Instance()
        config["facilityName"]='HFIR'
        GPSANS()
        DirectBeamCenter("BioSANS_empty_cell.xml")
        AppendDataFile("BioSANS_test_data.xml")
        SetTransmission(0.51944, 0.011078)
        SensitivityCorrection("BioSANS_flood_data.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce()
        print "------------- OUTPUT -------------"
        print ReductionSingleton().log_text

        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", "HFIRReduction.nxs"
