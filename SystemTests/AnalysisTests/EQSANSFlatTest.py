import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.sns_command_interface import *

# If true, this test will be skipped
SKIP_ME = True

class EQSANSFlatTest(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for EQSANS.
            This test is meant to be run at SNS and takes a long time.
            It is used to verify that the complete reduction chain works
            and reproduces reference results.
        """
        if SKIP_ME: return
        
        EQSANS()
        DataPath(os.path.expanduser("~")+"/data/eqsans")
        SolidAngle()
        DarkCurrent("5704")
        MonitorNormalization()
        AzimuthalAverage(n_bins=100, n_subpix=1, log_binning=False)
        IQxQy(nbins=100)
        OutputPath(os.path.expanduser("~")+"/data/output")
        UseConfigTOFTailsCutoff(True)
        PerformFlightPathCorrection(True)
        UseConfigMask(True)
        SetBeamCenter(89.6749, 129.693)
        SensitivityCorrection('5703', min_sensitivity=0.5, max_sensitivity=1.5, use_sample_dc=True)
        DivideByThickness(1)
        DirectBeamTransmission("5734", "5738", beam_radius=3)
        ThetaDependentTransmission(False)
        #Note: Data path was not found at script generation, will try at run time.
        AppendDataFile(["5729"])
        CombineTransmissionFits(True)
        
        Background("5732")
        BckDirectBeamTransmission("5737", "5738", beam_radius=3)
        BckThetaDependentTransmission(False)
        BckCombineTransmissionFits(True)
        SaveIqAscii(process='None')
        Reduce1D()
                
    def validate(self):
        if SKIP_ME: return None
        
        self.tolerance = 0.05
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "5729_frame1_Iq", 'EQSANSFlatTest.nxs'

