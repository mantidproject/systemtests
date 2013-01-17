import stresstesting
import mantid
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.sns_command_interface import *
from mantid.api import *

class EQSANSTransmission(stresstesting.MantidStressTest):
    def runTest(self):
        config = ConfigService.Instance()
        config["facilityName"]='SNS'
        EQSANS(False)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        CombineTransmissionFits(True)
        UseConfigMask(False)
        SetBeamCenter(96.29, 126.15)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_1466_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()  
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              
                
    def validate(self):
        # Be more tolerant with the output, mainly because of the errors.
        # The following tolerance check the errors up to the third digit.   
        self.tolerance = 0.1
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_1466_event_Iq", 'EQSANSTrans.nxs'

class EQSANSTransmissionEvent(EQSANSTransmission):    
    def runTest(self):
        config = ConfigService.Instance()
        config["facilityName"]='SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        SetBeamCenter(96.29, 126.15)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_1466_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              

class EQSANSTransmissionCompatibility(EQSANSTransmission):
    """
        Analysis Tests for EQSANS
        Check that the transmission correction can be applied if the 
        sample run and transmission runs don't have the same binning
    """
    
    def runTest(self):
        config = ConfigService.Instance()
        config["facilityName"]='SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        SetBeamCenter(96.29, 126.15)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_4061_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              

    def validate(self):
        # Be more tolerant with the output, mainly because of the errors.
        # The following tolerance check the errors up to the third digit.   
        self.tolerance = 0.1
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_1466_event_Iq", 'EQSANSTransmissionCompatibility.nxs'
