import stresstesting
import mantid
from mantid.simpleapi import *

class SANSBeamFluxCorrectionSimpleTest(stresstesting.MantidStressTest):
    def _setup(self):
        self.test_ws_name = "EQSANS_test_ws"
        x = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.]
        y = 491520*[0.1]    
        CreateWorkspace(OutputWorkspace=self.test_ws_name,DataX=x,DataY=y,DataE=y,NSpec='49152',UnitX='Wavelength')
        LoadInstrument(self.test_ws_name, InstrumentName="EQSANS")

        self.monitor = "EQSANS_test_monitor_ws"
        SumSpectra(InputWorkspace=self.test_ws_name, OutputWorkspace=self.monitor)

        self.expected_ws_name = "expected"
        CreateWorkspace(OutputWorkspace=self.expected_ws_name,
                        DataX=x,
                        DataY=491520*[4.139211e-09],
                        DataE=491520*[4.139296e-09],
                        NSpec='49152',
                        UnitX='Wavelength')

        self.tolerance = 0.00001

        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def runTest(self):
        self._setup()

        output = SANSBeamFluxCorrection(InputWorkspace=self.test_ws_name,
                                        InputMonitorWorkspace=self.monitor,
                                        ReferenceFluxFilename="SANSBeamFluxCorrectionMonitor.nxs")

    def validate(self):
        return ("output", self.expected_ws_name)

class SANSBeamFluxCorrectionInPlaceTest(SANSBeamFluxCorrectionSimpleTest):
    def runTest(self):
        self._setup()

        output = SANSBeamFluxCorrection(InputWorkspace=self.test_ws_name,
                                        InputMonitorWorkspace=self.monitor,
                                        ReferenceFluxFilename="SANSBeamFluxCorrectionMonitor.nxs",
                                        OutputWorkspace=self.test_ws_name)

    def validate(self):
        return (self.test_ws_name, self.expected_ws_name)
