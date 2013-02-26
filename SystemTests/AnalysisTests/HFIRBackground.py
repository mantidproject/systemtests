import stresstesting
from mantid import *

from mantid.simpleapi import *
from reduction.instruments.sans.hfir_command_interface import *

class HFIRBackground(stresstesting.MantidStressTest):
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        SetBeamCenter(16, 95)
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackground.nxs'

class HFIRBackgroundTransmission(stresstesting.MantidStressTest):
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        SetBckTransmission(0.55, 0.1)
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackgroundTransmission.nxs'

class HFIRBackgroundDirectBeamTrans(stresstesting.MantidStressTest):
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        BckDirectBeamTransmission(sample_file="BioSANS_sample_trans.xml",
                                  empty_file="BioSANS_empty_trans.xml",
                                  beam_radius=10.0)
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackgroundDirectBeamTrans.nxs'

class HFIRBackgroundBeamSpreaderTrans(stresstesting.MantidStressTest):
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        BckBeamSpreaderTransmission(sample_spreader="BioSANS_test_data.xml", 
                                 direct_spreader="BioSANS_empty_cell.xml",
                                 sample_scattering="BioSANS_test_data.xml", 
                                 direct_scattering="BioSANS_empty_cell.xml",
                                 spreader_transmission=0.5, 
                                 spreader_transmission_err=0.1)
        AzimuthalAverage(binning="0.01,0.001,0.11")
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackgroundBeamSpreaderTrans.nxs'

class HFIRBackgroundTransDarkCurrent(stresstesting.MantidStressTest):
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        BckDirectBeamTransmission(sample_file="BioSANS_sample_trans.xml",
                                  empty_file="BioSANS_empty_trans.xml",
                                  beam_radius=10.0)
        BckTransmissionDarkCurrent("BioSANS_dark_current.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()

    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackgroundTransDarkCurrent.nxs'
    
class HFIRBackgroundDirectBeamTransDC(stresstesting.MantidStressTest):
    def runTest(self):
        config['default.facility'] = 'HFIR'
        HFIRSANS()
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        BckDirectBeamTransmission(sample_file="BioSANS_sample_trans.xml",
                                  empty_file="BioSANS_empty_trans.xml",
                                  beam_radius=10.0)
        BckTransmissionDarkCurrent("BioSANS_dark_current.xml")
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackgroundDirectBeamTransDC.nxs'
    
