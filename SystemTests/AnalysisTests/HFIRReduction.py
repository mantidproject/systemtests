import stresstesting
from mantid import *

from mantid.simpleapi import *
from reduction.instruments.sans.hfir_command_interface import *

class HFIRReduction(stresstesting.MantidStressTest):
    """
        Simple reduction example
    """
    
    def runTest(self):

        config['default.facility'] = 'HFIR'
        HFIRSANS()
        DirectBeamCenter("BioSANS_empty_cell.xml")
        AppendDataFile("BioSANS_test_data.xml")
        SetTransmission(0.51944, 0.011078)
        SensitivityCorrection("BioSANS_flood_data.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", "HFIRReduction.nxs"

class HFIRAbsoluteScalingReference(stresstesting.MantidStressTest):
    """
        Test absolute scaling using a reference data set
    """
    
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        SolidAngle(detector_tubes=True)
        MonitorNormalization()
        AzimuthalAverage(binning="0.01,0.001,0.2")
        SetBeamCenter(16.39, 95.53)
        SetDirectBeamAbsoluteScale('BioSANS_empty_trans.xml')
        AppendDataFile(["BioSANS_test_data.xml"])
        Reduce()
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", "HFIRAbsoluteScalingReference.nxs"

class HFIRAbsoluteScalingReference(stresstesting.MantidStressTest):
    """
        Test absolute scaling using a reference data set
    """
    
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        SolidAngle(detector_tubes=True)
        MonitorNormalization()
        AzimuthalAverage(binning="0.01,0.001,0.2")
        SetBeamCenter(16.39, 95.53)
        SetAbsoluteScale(1.680537663117948)
        AppendDataFile(["BioSANS_test_data.xml"])
        Reduce()
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", "HFIRAbsoluteScalingReference.nxs"

