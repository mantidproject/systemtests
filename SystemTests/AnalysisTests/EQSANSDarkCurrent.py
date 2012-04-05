import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.sns_command_interface import *
class EQSANSDarkCurrent(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
        Testing that the I(Q) output of is correct 
    """
    
    def runTest(self):
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
        SetTransmission(1.0,0.0, False)
        DarkCurrent("EQSANS_4061_event.nxs")
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
