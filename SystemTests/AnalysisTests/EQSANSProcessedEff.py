import stresstesting
from mantid import *

from mantid.simpleapi import *
from reduction.instruments.sans.sns_command_interface import *
class EQSANSProcessedEff(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for sensitivity correction
        """
        self.cleanup()
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        config['default.facility'] = 'SNS'
        EQSANS(False)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        SensitivityCorrection("EQSANS_sensitivity.nxs")
        Reduce1D()  
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=277.781, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              
                
    def cleanup(self):
        for ws in ["EQSANS_1466_event_Iq", "EQSANS_1466_event", "EQSANS_1466_event_evt"]:
            if mtd.doesExist(ws):
                mtd.deleteWorkspace(ws)
                
    def validate(self):
        # Be more tolerant with the output, mainly because of the errors.
        # The following tolerance check the errors up to the third digit.   
        self.tolerance = 0.1
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_1466_event_Iq", 'EQSANSProcessedEff.nxs'

class EQSANSComputeEff(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for sensitivity correction calculation
        """
        self.cleanup()
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        config['default.facility'] = 'SNS'
        SetupEQSANSReduction(UseConfig=False, UseConfigMask=False, 
                             SensitivityFile="EQSANS_4061_event.nxs", 
                             BeamCenterMethod="Value",
                             BeamCenterX=89.675, BeamCenterY=129.693, 
                             ReductionProperties="_reduction")
        ComputeSensitivity(Filename="EQSANS_4061_event.nxs", 
                           ReductionProperties="_reduction", 
                           OutputWorkspace="sensitivity")
                
    def validate(self):
        # Be more tolerant with the output, mainly because of the errors.
        # The following tolerance check the errors up to the third digit.   
        self.tolerance = 0.001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "sensitivity", 'EQSANSComputeEff.nxs'

