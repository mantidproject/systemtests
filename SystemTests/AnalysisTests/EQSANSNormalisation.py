import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.sns_command_interface import *
import os

class EQSANSNormalisationNoFlux(stresstesting.MantidStressTest):
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
        mtd.settings['default.facility'] = 'SNS'
        ws = "__eqsans_normalisation_test"
        
        EQSANSLoad(Filename="EQSANS_1466_event.nxs", OutputWorkspace=ws, PreserveEvents=False)
        EQSANSNormalise(InputWorkspace=ws, NormaliseToBeam=False)
        SumSpectra(InputWorkspace=ws, OutputWorkspace="eqsans_no_flux")
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "eqsans_no_flux", 'EQSANSNormalisation_NoFlux.nxs'

class EQSANSNormalisationDefault(stresstesting.MantidStressTest):
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
        mtd.settings['default.facility'] = 'SNS'
        ws = "__eqsans_normalisation_test"
        
        EQSANSLoad(Filename="EQSANS_1466_event.nxs", OutputWorkspace=ws, PreserveEvents=False)
        EQSANSNormalise(InputWorkspace=ws,NormaliseToBeam=True)
        SumSpectra(InputWorkspace=ws, OutputWorkspace="eqsans_default_flux")
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "eqsans_default_flux", 'EQSANSNormalisation_DefaultFlux.nxs'
    
class EQSANSNormalisationInputFlux(stresstesting.MantidStressTest):
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
        mtd.settings['default.facility'] = 'SNS'
        ws = "__eqsans_normalisation_test"
        
        parentDir = os.path.abspath('..')
        spectrum_file = os.path.join(parentDir, "Data", "eqsans_beam_flux.txt")
        
        EQSANSLoad(Filename="EQSANS_1466_event.nxs", OutputWorkspace=ws, PreserveEvents=False)
        EQSANSNormalise(InputWorkspace=ws,NormaliseToBeam=True,BeamSpectrumFile=spectrum_file)
        SumSpectra(InputWorkspace=ws, OutputWorkspace="eqsans_input_flux")
  
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "eqsans_input_flux", 'EQSANSNormalisation_InputFlux.nxs'
