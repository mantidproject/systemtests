import stresstesting
import mantid
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.sns_command_interface import *
from mantid.api import *

class EQSANSDarkCurrent(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
        Testing that the I(Q) output of is correct 
    """
    
    def runTest(self):
        config = ConfigService.Instance()
        config["facilityName"]='SNS'
        EQSANS(True)
        SolidAngle()
        SetBeamCenter(96.29, 126.15)
        PerformFlightPathCorrection(False)
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        SetTOFTailsCutoff(low_cut=0.00, high_cut=0.00)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        SetTransmission(1.0,0.0, False)
        DarkCurrent("EQSANS_4061_event.nxs")
        AppendDataFile("EQSANS_1466_event.nxs")
        Reduce1D()           
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              

    def validate(self):
        self.tolerance = 1.0
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "EQSANS_1466_event_Iq", 'EQSANSDarkCurrent.nxs'

class EQSANSDarkCurrentWorkflow(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS using the workflow algorithms
        along with property manager
        Testing that the I(Q) output of is correct 
    """
    
    def runTest(self):
        config = ConfigService.Instance()
        config["facilityName"]='SNS'
        SetupEQSANSReduction(UseConfig=False,
                             PreserveEvents=True,
                             Normalisation="Charge",
                             BeamCenterMethod="Value",
                             BeamCenterX=96.29,
                             BeamCenterY=126.15,
                             DarkCurrentFile="EQSANS_4061_event.nxs",
                             TransmissionValue=1.0,
                             ThetaDependentTransmission=False,
                             SetupReducer=True,
                             ReductionProperties="_test_eqsans_reduce")
        
        EQSANSReduce(Filename="EQSANS_1466_event.nxs",
                     ReductionProcess=True,
                     PostProcess=True,
                     ReductionProperties="_test_eqsans_reduce",
                     OutputWorkspace="eqsans_reduce_output")
        
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              

    def validate(self):
        self.tolerance = 1.0
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "EQSANS_1466_event_Iq", 'EQSANSDarkCurrent.nxs'
