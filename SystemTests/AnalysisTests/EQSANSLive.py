import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *

class EQSANSLive(stresstesting.MantidStressTest):
    def runTest(self):
        """
            System test for live and mpi reduction
        """
        self.cleanup()
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        mtd.settings['default.facility'] = 'SNS'

        SetupEQSANSReduction(UseConfigTOFCuts=True, 
                             UseConfigMask=True, 
                             BeamCenterX=89.675, 
                             BeamCenterY=129.693,
                             PreserveEvents=False,
                             NormaliseToBeam=True,
                             NormaliseToMonitor=False,
                             SensitivityFile="EQSANS_sensitivity.nxs",
                             CorrectForFlightPath=False,
                             SetupReducer=True,
                             SolidAngleCorrection=False,
                             TransmissionValue="1.0",
                             ReductionProperties="_reduction")
        EQSANSReduce(Filename="EQSANS_1466_event.nxs", 
                     ReductionProcess=True, 
                     PostProcess=True,
                     ReductionProperties="_reduction", 
                     OutputWorkspace="EQSANS_1466_event_Iq")  
                
    def cleanup(self):
        for ws in ["EQSANS_1466_event_Iq", "EQSANS_1466_event", "EQSANS_1466_event_evt"]:
            if mtd.workspaceExists(ws):
                mtd.deleteWorkspace(ws)
                
    def validate(self):
        # Be more tolerant with the output, mainly because of the errors.
        # The following tolerance check the errors up to the third digit.   
        self.tolerance = 0.001
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_1466_event_Iq", 'EQSANSLive.nxs'
