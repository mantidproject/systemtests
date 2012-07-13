import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
import math
from reduction.instruments.sans.sns_command_interface import *
class EQSANSIQOutput(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
        Testing that the I(Q) output of is correct 
    """
    
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        self.cleanup()
        mtd.settings['default.facility'] = 'SNS'
        EQSANS()
        AppendDataFile("EQSANS_1466_event.nxs")
        NoSolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        Reduce1D()        
        # Scale up to match correct scaling.
        Scale(InputWorkspace="EQSANS_1466_event_Iq", Factor=2777.81, 
              Operation='Multiply', OutputWorkspace="EQSANS_1466_event_Iq")              
                        
    def cleanup(self):
        for ws in ["EQSANS_1466_event_Iq", "EQSANS_1466_event", "EQSANS_1466_event_evt", "beam_hole_transmission_EQSANS_1466_event"]:
            if mtd.workspaceExists(ws):
                mtd.deleteWorkspace(ws)
                
    def validate(self):
        self.tolerance = 0.2
        mtd["EQSANS_1466_event_Iq"].dataY(0)[0] = 269.687
        mtd["EQSANS_1466_event_Iq"].dataE(0)[0] = 16.4977
        mtd["EQSANS_1466_event_Iq"].dataE(0)[1] = 6.78
        mtd["EQSANS_1466_event_Iq"].dataY(0)[2] = 11.3157
        mtd["EQSANS_1466_event_Iq"].dataE(0)[2] = 1.23419
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_1466_event_Iq", 'EQSANSIQOutput.nxs'

class EQSANSDQPositiveOutput(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
        Testing that the Q resolution output of is correct 
    """
    
    def runTest(self):
        """
            Check that the Q resolution calculation returns positive values
            even when background is larger than signal and I(q) is negative.
            (Non-physical value that's an experimental edge case)
        """
        mtd.settings['default.facility'] = 'SNS'
        EQSANS()
        AppendDataFile("EQSANS_1466_event.nxs")
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        SetTransmission(1.0,0.0, False)
        Background("EQSANS_4061_event.nxs")
        Resolution()
        Reduce1D()           
                        
    def validate(self):
        dq = mtd['EQSANS_1466_event_Iq'].dataDx(0)
        return min(dq)>=0
    
class EQSANSDQOutput(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
        Testing that the Q resolution output of is correct 
    """
    
    def runTest(self):
        """
            Check that the Q resolution calculation returns positive values
            even when background is larger than signal and I(q) is negative.
            (Non-physical value that's an experimental edge case)
        """
        mtd.settings['default.facility'] = 'SNS'
        EQSANS()
        AppendDataFile("EQSANS_1466_event.nxs")
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        SetTransmission(1.0,0.0, False)
        Background("EQSANS_4061_event.nxs")
        Resolution()
        Reduce1D()           
                        
    def validate(self):
        """
            Reference values were generate using the event-by-event method
            and are slightly different than the ones generated using
            the histogram method.
            The event-by-event method processes each event one-by-one,
            computes dQ for each of them, and averages those dQ for each
            Q bin of the I(Q) distribution.
        """
        dq_ref = [0.00178823,0.0014458,0.00144805,0.00155836,0.00150908,
                  0.00163262,0.00158216,0.00160879,0.00165932,0.00164304,
                  0.00165549,0.00163676,0.00167581,0.0016957,0.00167898,
                  0.00172297,0.00169375,0.00174938,0.00173394,0.00180498,
                  0.00188825,0.00184747,0.00181396,0.00185052,0.00191187,
                  0.00192331,0.00196536,0.00196182,0.00202844,0.00205516,
                  0.00208013,0.00210195,0.00212621,0.00217228,0.00217713,
                  0.002243,0.00225329,0.00229956,0.00234733,0.00234773,
                  0.00239551,0.00243152,0.0024392,0.00248026,0.00249286,
                  0.00252012,0.00253674,0.00257043,0.00257755,0.00261695,
                  0.00263961,0.00268499,0.0026836,0.00273043,0.00272828,
                  0.00279073,0.00279924,0.00284322,0.00283794,0.00288332,
                  0.00289423,0.00291934,0.00294244,0.00295239,0.00297587,
                  0.00300671,0.00299071,0.00307836,0.00304013,0.00307726,
                  0.00312929,0.00314636,0.00315895,0.00312642,0.00322729,
                  0.00325368,0.00326916,0.00328936,0.00331894,0.00328319,
                  0.00337098,0.00335638,0.00335586,0.00340926,0.00343972,
                  0.00349148,0.003528,0.00352863,0.0035665,0.0036791,
                  0.00360243,0.00364245,0.003671,0,0,0,0.00375495,0,0,0,0]
        dq = mtd['EQSANS_1466_event_Iq'].readDx(0)
        diff = [math.fabs(dq_ref[i]-dq[i])<0.0001 for i in range(7,100)]
        output = reduce(lambda x,y:x and y, diff)
        if not output:
            for i in range(len(dq)):
                print i, dq[i], dq_ref[i], math.fabs(dq_ref[i]-dq[i])<0.0001
        return output