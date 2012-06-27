import stresstesting
from mantidsimple import RenameWorkspace

import inelastic_indirect_reducer

from abc import ABCMeta, abstractmethod

#----------------------------------------------------------------------
class ISISIndirectInelasticReduction(stresstesting.MantidStressTest):
    """A base class for the ISIS indirect inelastic tests
    
    The workflow is defined in the runTest() method, simply
    define an __init__ method and set the following properties
    on the object
        - instr_name: A string giving the instrument name for the test
        - detector_range: A list containing the lower and upper bounds of the 
                          range of detectors to use
        - data_file: A string giving the data file to use
        - rebin_string: A comma separated string giving the rebin params
        - result_name: A string giving the name of the resulting ws
        - save_formats: A list containing the file extensions of the formats
                        to save to.
    """
    __metaclass__ = ABCMeta # Mark as an abstract class

    @abstractmethod
    def get_reference_file(self):
        """Returns the name of the reference file to compare against"""
        raise NotImplementedError("Implmenent get_reference_file to return "
                                  "the name of the file to compare against.")
    
    def runTest(self):
        """Defines the workflow for the test"""
        self._validate_properties()
        
        reducer = inelastic_indirect_reducer.IndirectReducer()
        reducer.set_instrument_name(self.instr_name)
        reducer.set_detector_range(self.detector_range[0], 
                                   self.detector_range[1])
        reducer.append_data_file(self.data_file)
        if self.rebin_string is not None:
            reducer.set_rebin_string(self.rebin_string)
        
        # Do the reduction and rename the result.
        reducer.reduce()
        ws = reducer.get_result_workspaces()[0]
        RenameWorkspace(ws, self.result_name)

    def validate(self):
        """Returns the name of the workspace & file to compare"""
        self.tolerance = 1e-7
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Instrument')
        result = self.result_name
        reference = self.get_reference_file()
        return result, reference

    def _validate_properties(self):
        """Check the object properties are in an expected state to continue"""
        if type(self.instr_name) != str:
            raise RuntimeError("instr_name property should be a string")
        if type(self.detector_range) != list and len(self.detector_range) != 2:
            raise RuntimeError("detector_range should be a list of exactly 2 "
                               "values")
        if type(self.data_file) != str:
            raise RuntimeError("data_file property should be a string")
        if self.rebin_string is not None and type(self.rebin_string) != str:
            raise RuntimeError("rebin_string property should be a string")
        if type(self.result_name) != str:
            raise RuntimeError("result_name property should be a string")

#------------------------- TOSCA tests ----------------------------------------

class TOSCAReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'TOSCA'
        self.detector_range = [1, 139]
        self.data_file = 'TSC11453.raw'
        self.rebin_string = '-2.5,0.015,3,-0.005,1000'
        self.result_name = 'ToscaReductionTest'
    
    def get_reference_file(self):
        return "II.TOSCAReductionFromFile.nxs"

#------------------------- OSIRIS tests ---------------------------------------

class OSIRISReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'OSIRIS'
        self.detector_range = [963, 1004]
        self.data_file = 'OSI97919.raw'
        self.rebin_string = None
        self.result_name = 'OsirisReductionTest'
    
    def get_reference_file(self):
        return "II.OSIRISReductionFromFile.nxs"

#------------------------- IRIS tests ---------------------------------------

class IRISReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'IRIS'
        self.detector_range = [3, 53]
        self.data_file = 'IRS21360.raw'
        self.rebin_string = None
        self.result_name = 'IrisReductionTest'
    
    def get_reference_file(self):
        return "II.IRISReductionFromFile.nxs"
