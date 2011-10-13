import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.sns_command_interface import *
class EQSANSTransmission(stresstesting.MantidStressTest):
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        self.cleanup()
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        mtd.settings['default.facility'] = 'SNS'
        EQSANS(False)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_1466_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()  
        # Scale up to match correct scaling. The reference data is off by a factor 10.0 
        Scale("EQSANS_1466_event_Iq", "EQSANS_1466_event_Iq", 10.0)                
                
    def cleanup(self):
        for ws in ["EQSANS_1466_event_Iq", "EQSANS_1466_event", "EQSANS_1466_event_evt"]:
            if mtd.workspaceExists(ws):
                mtd.deleteWorkspace(ws)
                
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
    """
        Analysis Tests for EQSANS
        Testing that the I(Q) output of is correct 
    """
    
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        self.cleanup()
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        mtd.settings['default.facility'] = 'SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_1466_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()
        # Scale up to match correct scaling. The reference data is off by a factor 10.0 
        Scale("EQSANS_1466_event_Iq", "EQSANS_1466_event_Iq", 10.0)                

