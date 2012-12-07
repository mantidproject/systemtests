import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.hfir_command_interface import *

class HFIRBackground(stresstesting.MantidStressTest):
    def runTest(self):
        mtd.settings['default.facility'] = 'HFIR'
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
        mtd.settings['default.facility'] = 'HFIR'
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
        mtd.settings['default.facility'] = 'HFIR'
        HFIRSANS()
        AppendDataFile("BioSANS_test_data.xml")
        Background("BioSANS_test_data.xml")
        BckDirectBeamTransmission(sample_file="BioSANS_sample_trans.xml",
                                  empty_file="BioSANS_empty_trans.xml",
                                  beam_radius=10.0)
        AzimuthalAverage(binning="0.01,0.001,0.11", error_weighting=True)
        Reduce1D()
        print ReductionSingleton().log_text
                
    def validate(self):
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "BioSANS_test_data_Iq", 'HFIRBackgroundDirectBeamTrans.nxs'

