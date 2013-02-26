import stresstesting
from mantid import *

from mantid.simpleapi import *
from reduction.instruments.sans.hfir_command_interface import *
class HFIREff(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for sensitivity correction
        """
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        DirectBeamCenter("BioSANS_empty_cell.xml")
        AppendDataFile("BioSANS_test_data.xml")
        SetTransmission(0.51944, 0.011078)
        SensitivityCorrection("BioSANS_flood_data.xml",
                              dark_current="BioSANS_dark_current.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIREff.nxs'

class HFIRSensitivityDirectBeamCenter(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for sensitivity correction
        """
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        DirectBeamCenter("BioSANS_empty_cell.xml")
        AppendDataFile("BioSANS_test_data.xml")
        SetTransmission(0.51944, 0.011078)
        SensitivityCorrection("BioSANS_flood_data.xml", 
                              dark_current="BioSANS_dark_current.xml")
        SensitivityDirectBeamCenter("BioSANS_empty_trans.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRSensitivityDirectBeamCenter.nxs'

class HFIRSensitivityScatteringBeamCenter(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for sensitivity correction
        """
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        DirectBeamCenter("BioSANS_empty_cell.xml")
        AppendDataFile("BioSANS_test_data.xml")
        SetTransmission(0.51944, 0.011078)
        SensitivityCorrection("BioSANS_flood_data.xml", 
                              dark_current="BioSANS_dark_current.xml")
        SensitivityScatteringBeamCenter("BioSANS_test_data.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRSensitivityScatteringBeamCenter.nxs'

