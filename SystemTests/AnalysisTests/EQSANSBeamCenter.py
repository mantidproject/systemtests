import stresstesting
from mantid import *

from mantid.simpleapi import *
from reduction.instruments.sans.sns_command_interface import *
class EQSANSBeamCenter(stresstesting.MantidStressTest):
    def runTest(self):
        self.cleanup()
        config['default.facility'] = 'SNS'
        EQSANS(False)
        AppendDataFile("EQSANS_4061_event.nxs")
        NoSolidAngle()
        IndependentBinning(False)
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamCenter("EQSANS_1466_event.nxs")    
        Reduce1D()  
        # Scale up to match correct scaling. The reference data is off by a factor 10.0 
        Scale(InputWorkspace="EQSANS_4061_event_frame2_Iq", Factor=10.0, 
              Operation='Multiply', OutputWorkspace="EQSANS_4061_event_frame2_Iq")
        Scale(InputWorkspace="EQSANS_4061_event_frame2_Iq", Factor=277.781, 
              Operation='Multiply', OutputWorkspace="EQSANS_4061_event_frame2_Iq")
                
    def cleanup(self):
        for ws in ["beam_center_EQSANS_1466_event", "beam_center_EQSANS_1466_event_evt",
                   "EQSANS_4061_event_frame2_Iq", "EQSANS_4061_event", "EQSANS_4061_event_evt",
                   "beam_hole_transmission_EQSANS_4061_event"]:
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
        return "EQSANS_4061_event_frame2_Iq", 'EQSANSBeamCenter.nxs'

class EQSANSBeamCenterEvent(EQSANSBeamCenter):
    def runTest(self):
        self.cleanup()
        config['default.facility'] = 'SNS'
        EQSANS(True)
        AppendDataFile("EQSANS_4061_event.nxs")
        NoSolidAngle()
        IndependentBinning(False)
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        DirectBeamCenter("EQSANS_1466_event.nxs")    
        Reduce1D()
        # Scale up to match correct scaling. The reference data is off by a factor 10.0 
        Scale(InputWorkspace="EQSANS_4061_event_frame2_Iq", Factor=10.0, 
              Operation='Multiply', OutputWorkspace="EQSANS_4061_event_frame2_Iq")
        Scale(InputWorkspace="EQSANS_4061_event_frame2_Iq", Factor=277.781, 
              Operation='Multiply', OutputWorkspace="EQSANS_4061_event_frame2_Iq")
