import stresstesting
from mantidsimple import RenameWorkspace

from inelastic_indirect_reducer import IndirectReducer
from inelastic_indirect_reduction_steps import CreateCalibrationWorkspace
from IndirectEnergyConversion import resolution

from abc import ABCMeta, abstractmethod

#==============================================================================
class ISISIndirectInelasticReduction(stresstesting.MantidStressTest):
    """A base class for the ISIS indirect inelastic reduction tests
    
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
        
        reducer = IndirectReducer()
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

#------------------------- IRIS tests -----------------------------------------

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

        
#==============================================================================
class ISISIndirectInelasticCalibration(stresstesting.MantidStressTest):
    """A base class for the ISIS indirect inelastic calibration tests
    
    The workflow is defined in the runTest() method, simply
    define an __init__ method and set the following properties
    on the object
        - self.data_file: a string giving the name of the data file
        - self.detector_range: a list of two ints, giving the lower and
                               upper bounds of the detector range
        - self.parameters: a list containing four doubles, each a parameter.
        - self.analyser: a string giving the name of the analyser to use
        - self.reflection: a string giving the reflection to use
        - self.result_name: a string containing the name of the result
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
        
        calib = CreateCalibrationWorkspace()
        calib.set_files([self.data_file])
        calib.set_detector_range(self.detector_range[0], 
                                 self.detector_range[1])
        calib.set_parameters(self.parameters[0],
                             self.parameters[1],
                             self.parameters[2],
                             self.parameters[3])
        calib.set_analyser(self.analyser)
        calib.set_reflection(self.reflection)
        calib.execute(None, None) # Does not appear to be used.
        result = calib.result_workspace()
        RenameWorkspace(result, self.result_name)

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
        
        if type(self.data_file) != str:
            raise RuntimeError("data_file property should be a string")
        if type(self.detector_range) != list and len(self.detector_range) != 2:
            raise RuntimeError("detector_range should be a list of exactly 2 "
                               "values")
        if type(self.parameters) != list and len(self.parameters) != 4:
            raise RuntimeError("parameters should be a list of exactly 4 "
                               "values")
        if type(self.analyser) != str:
            raise RuntimeError("analyser property should be a string")
        if type(self.reflection) != str:
            raise RuntimeError("reflection property should be a string")
        if type(self.result_name) != str:
            raise RuntimeError("result_name property should be a string")

#------------------------- OSIRIS tests ---------------------------------------

class OSIRISCalibration(ISISIndirectInelasticCalibration):

    def __init__(self):
        ISISIndirectInelasticCalibration.__init__(self)
        self.data_file = 'OSI97935.raw'
        self.detector_range = [963-1, 1004-1]
        self.parameters = [68000.00,70000.00,59000.00,61000.00]
        self.analyser = 'graphite'
        self.reflection = '002'
        self.result_name = 'OsirisCalibrationTest'
    
    def get_reference_file(self):
        return "II.OSIRISCalibration.nxs"

#------------------------- IRIS tests ---------------------------------------

class IRISCalibration(ISISIndirectInelasticCalibration):

    def __init__(self):
        ISISIndirectInelasticCalibration.__init__(self)
        self.data_file = 'IRS53664.raw'
        self.detector_range = [3-1, 53-1]
        self.parameters = [59000.00,61500.00,62500.00,65000.00]
        self.analyser = 'graphite'
        self.reflection = '002'
        self.result_name = 'IrisCalibrationTest'
    
    def get_reference_file(self):
        return "II.IRISCalibration.nxs"

        
#==============================================================================
class ISISIndirectInelasticResolution(stresstesting.MantidStressTest):
    """A base class for the ISIS indirect inelastic resolution tests
    
    The workflow is defined in the runTest() method, simply
    define an __init__ method and set the following properties
    on the object
        - self.icon_opt: a dictionary of icon options
        - self.instrument: a string giving the intrument name
        - self.analyser: a string giving the name of the analyser
        - self.reflection: a string giving the name of the reflection
        - self.background: a list of two doubles, giving the background params
        - rebin_params: a comma separated string containing the rebin params
        - self.files: a list of strings containing filenames
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
        
        result = resolution(self.files,
                            self.icon_opt,
                            self.rebin_params,
                            self.background,
                            self.instrument,
                            self.analyser,
                            self.reflection,
                            # Don't plot from a system test:
                            plotOpt = False)
        
        RenameWorkspace(result, self.result_name)

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
        
        if type(self.icon_opt) != dict:
            raise RuntimeError("icon_opt should be a dictionary of exactly")
        if type(self.instrument) != str:
            raise RuntimeError("instrument property should be a string")
        if type(self.analyser) != str:
            raise RuntimeError("analyser property should be a string")
        if type(self.reflection) != str:
            raise RuntimeError("reflection property should be a string")
        if type(self.background) != list and len(self.background) != 2:
            raise RuntimeError(" should be a list of exactly 2 "
                               "values")
        if type(self.rebin_params) != str:
            raise RuntimeError("rebin_params property should be a string")
        #Have this as just one file for now.
        if type(self.files) != list and len(self.files) != 1:
            raise RuntimeError("files should be a list of exactly 1 "
                               "value")

#------------------------- OSIRIS tests ---------------------------------------

class OSIRISResolution(ISISIndirectInelasticResolution):

    def __init__(self):
        ISISIndirectInelasticResolution.__init__(self)
        self.icon_opt = { 'first': 963, 'last': 1004 }
        self.instrument = 'OSIRIS'
        self.analyser = 'graphite'
        self.reflection = '002'
        self.background = [ -0.563032, 0.605636 ]
        self.rebin_params = '-0.2,0.002,0.2'
        self.files = ['OSI97935.raw']
        self.result_name = 'OsirisResolutionTest'
    
    def get_reference_file(self):
        return "II.OSIRISResolution.nxs"

#------------------------- IRIS tests -----------------------------------------

class IRISResolution(ISISIndirectInelasticResolution):

    def __init__(self):
        ISISIndirectInelasticResolution.__init__(self)
        self.icon_opt = { 'first': 3, 'last': 53 }
        self.instrument = 'IRIS'
        self.analyser = 'graphite'
        self.reflection = '002'
        self.background = [ -0.54, 0.65 ]
        self.rebin_params = '-0.2,0.002,0.2'
        self.files = ['IRS53664.raw']
        self.result_name = 'IrisResolutionTest'
    
    def get_reference_file(self):
        return "II.IRISResolution.nxs"