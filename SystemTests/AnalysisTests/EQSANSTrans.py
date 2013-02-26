import stresstesting
from mantid import *

from mantid.simpleapi import *
from reduction.instruments.sans.sns_command_interface import *
class EQSANSTransmission(stresstesting.MantidStressTest):
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
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
        DirectBeamTransmission("EQSANS_1466_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()  
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
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
        return "EQSANS_1466_event_Iq", 'EQSANSTrans.nxs'

class EQSANSTransmissionDC(stresstesting.MantidStressTest):
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
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
        DarkCurrent("EQSANS_4061_event.nxs")
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_1466_event.nxs", "EQSANS_1466_event.nxs", beam_radius=3)
        ThetaDependentTransmission(True)
        Reduce1D()  
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
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
        return "EQSANS_1466_event_Iq", 'EQSANSTransmissionDC.nxs'

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
        config['default.facility'] = 'SNS'
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
        """
            Check that transmission correction returns the correct workspace
        """
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        config['default.facility'] = 'SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_1466_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
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

class EQSANSTransmissionFS(stresstesting.MantidStressTest):
    
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        self.cleanup()
        config['default.facility'] = 'SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_4061_event.nxs")
        SolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        SetTransmission(0.5, 0.1)
        ThetaDependentTransmission(False)
        Reduce1D()
        
    def validate(self):
        self.tolerance = 0.000001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_4061_event_frame1_Iq", 'EQSANSTransmissionFS.nxs' 
    
class EQSANSDirectTransFS(stresstesting.MantidStressTest):
    
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        self.cleanup()
        config['default.facility'] = 'SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_4061_event.nxs")
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamTransmission("EQSANS_4061_event.nxs", "EQSANS_4061_event.nxs", beam_radius=3)
        ThetaDependentTransmission(False)
        Reduce1D()
        Scale(InputWorkspace="EQSANS_4061_event_frame1_Iq", Factor=2.0, 
              Operation='Multiply', OutputWorkspace="EQSANS_4061_event_frame1_Iq")              
       
    def validate(self):
        # Relax the tolerance since the reference data is not for that exact
        # scenario but for one that's very close to it.
        self.tolerance = 0.00001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_4061_event_frame1_Iq", 'EQSANSTransmissionFS.nxs' 
    
    