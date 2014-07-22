import stresstesting
from mantid.simpleapi import *

class EQSANS2QD(stresstesting.MantidStressTest):

    def _setup(self):
        self.test_ws_name = "EQSANS_test_ws"
        x = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.]
        y = 491520*[0.1]
        CreateWorkspace(OutputWorkspace=self.test_ws_name,DataX=x,DataY=y,DataE=y,NSpec='49152',UnitX='Wavelength')
        LoadInstrument(Workspace=self.test_ws_name, InstrumentName="EQSANS")

        run = mtd[self.test_ws_name].mutableRun()

        run.addProperty("sample_detector_distance", 4000.0, 'mm', True)
        run.addProperty("beam_center_x", 96.0, 'pixel', True)
        run.addProperty("beam_center_y", 128.0, 'pixel', True)   
        run.addProperty("wavelength_min", 1.0, "Angstrom", True)
        run.addProperty("wavelength_max", 11.0, "Angstrom", True)
        run.addProperty("is_frame_skipping", 0, True)
        run.addProperty("wavelength_min_frame2", 5.0, "Angstrom", True)
        run.addProperty("wavelength_max_frame2", 10.0, "Angstrom", True)

        self.expected_ws_name = "expected"
        CreateWorkspace(OutputWorkspace=self.expected_ws_name,
                        DataX=[-8.579111e-01, 8.579111e-01],
                        DataY=[7.240770e+00],
                        DataE=[5.220208e-02],
                        NSpec='1',
                        UnitX='MomentumTransfer')

        self.tolerance = 0.00001
        
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
    
    def runTest(self):
        self._setup()

        EQSANSQ2D(InputWorkspace=self.test_ws_name)
        ReplaceSpecialValues(InputWorkspace=self.test_ws_name+"_Iqxy",OutputWorkspace=self.test_ws_name+"_Iqxy",NaNValue=0,NaNError=0)
        Integration(InputWorkspace=self.test_ws_name+"_Iqxy", OutputWorkspace="__tmp")
        SumSpectra(InputWorkspace="__tmp", OutputWorkspace="summed")

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        return ("summed", self.expected_ws_name)