import stresstesting
from mantidsimple import RenameWorkspace, LoadNexus
import os

from inelastic_indirect_reducer import IndirectReducer
from inelastic_indirect_reduction_steps import CreateCalibrationWorkspace
from IndirectEnergyConversion import resolution
from IndirectEnergyConversion import slice

from abc import ABCMeta, abstractmethod

'''
stresstesting.MantidStressTest
 |
 +--ISISIndirectInelasticBase
     |
     +--ISISIndirectInelasticReduction
     |   |
     |   +--TOSCAReduction
     |   +--IRISReduction
     |   +--OSIRISReduction
     |
     +--ISISIndirectInelasticCalibratrion
     |   |
     |   +--IRISCalibratrion
     |   +--OSIRISCalibratrion
     |
     +--ISISIndirectInelasticResolution
     |   |
     |   +--IRISResolution
     |   +--OSIRISResolution
     |
     +--ISISIndirectInelasticDiagnostics
         |
         +--IRISDiagnostics
         +--OSIRISDiagnostics
'''

class ISISIndirectInelasticBase(stresstesting.MantidStressTest):
    '''A common base class for the ISISIndirectInelastic* base classes.
    '''
    __metaclass__ = ABCMeta # Mark as an abstract class

    @abstractmethod
    def get_reference_files(self):
        '''Returns the name of the reference files to compare against.'''
        raise NotImplementedError("Implmenent get_reference_files to return "
                                  "the names of the files to compare against.")

    @abstractmethod
    def _run(self):
        raise NotImplementedError("Implement _run.")
    
    def validate_results_and_references(self):
        if type(self.get_reference_files()) != list:
            raise RuntimeError("The reference file(s) should be in a list")
        if type(self.result_names) != list:
            raise RuntimeError("The result workspace(s) should be in a list")
        if len(self.get_reference_files()) !=\
           len(self.result_names):
            raise RuntimeError("The number of result workspaces does not match"
                               " the number of reference files.")
        if len(self.get_reference_files()) < 1:
            raise RuntimeError("There needs to be a least one result and "
                               "reference.")
    
    @abstractmethod
    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        raise NotImplementedError("Implmenent _validate_properties.")
    
    def runTest(self):
        self._validate_properties()
        self._run()
        self.validate_results_and_references()

    def validate(self):
        '''Performs the validation for the generalised case of multiple results
        and multiple reference files.
        '''
        self.tolerance = 1e-7
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Axes')
        
        for reference_file, result in zip(self.get_reference_files(),
                                          self.result_names):
            wsName = "RefFile"
            if reference_file.endswith('.nxs'):
                LoadNexus(Filename=reference_file,OutputWorkspace=wsName)
            else:
                raise RuntimeError("Should supply a NeXus file: %s" % 
                                   reference_file)
            
            if not self.validateWorkspaces([wsName, result]):
                print str([reference_file, result]) + " do not match."
                return False
        
        return True


#==============================================================================
class ISISIndirectInelasticReduction(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic reduction tests
    
    The workflow is defined in the _run() method, simply
    define an __init__ method and set the following properties
    on the object
        - instr_name: A string giving the instrument name for the test
        - detector_range: A list containing the lower and upper bounds of the 
                          range of detectors to use
        - data_file: A string giving the data file to use
        - rebin_string: A comma separated string giving the rebin params
        - save_formats: A list containing the file extensions of the formats
                        to save to.
    '''
    __metaclass__ = ABCMeta # Mark as an abstract class
    
    def _run(self):
        '''Defines the workflow for the test'''
        reducer = IndirectReducer()
        reducer.set_instrument_name(self.instr_name)
        reducer.set_detector_range(self.detector_range[0], 
                                   self.detector_range[1])
        reducer.append_data_file(self.data_file)
        if self.rebin_string is not None:
            reducer.set_rebin_string(self.rebin_string)
        
        # Do the reduction and rename the result.
        reducer.reduce()
        self.result_names = reducer.get_result_workspaces()

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        if type(self.instr_name) != str:
            raise RuntimeError("instr_name property should be a string")
        if type(self.detector_range) != list and len(self.detector_range) != 2:
            raise RuntimeError("detector_range should be a list of exactly 2 "
                               "values")
        if type(self.data_file) != str:
            raise RuntimeError("data_file property should be a string")
        if self.rebin_string is not None and type(self.rebin_string) != str:
            raise RuntimeError("rebin_string property should be a string")

#------------------------- TOSCA tests ----------------------------------------

class TOSCAReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'TOSCA'
        self.detector_range = [1, 139]
        self.data_file = 'TSC11453.raw'
        self.rebin_string = '-2.5,0.015,3,-0.005,1000'
    
    def get_reference_files(self):
        return ["II.TOSCAReductionFromFile.nxs"]

#------------------------- OSIRIS tests ---------------------------------------

class OSIRISReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'OSIRIS'
        self.detector_range = [963, 1004]
        self.data_file = 'OSI97919.raw'
        self.rebin_string = None
    
    def get_reference_files(self):
        return ["II.OSIRISReductionFromFile.nxs"]

#------------------------- IRIS tests -----------------------------------------

class IRISReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'IRIS'
        self.detector_range = [3, 53]
        self.data_file = 'IRS21360.raw'
        self.rebin_string = None
    
    def get_reference_files(self):
        return ["II.IRISReductionFromFile.nxs"]


#==============================================================================
class ISISIndirectInelasticCalibration(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic calibration tests
    
    The workflow is defined in the _run() method, simply
    define an __init__ method and set the following properties
    on the object
        - self.data_file: a string giving the name of the data file
        - self.detector_range: a list of two ints, giving the lower and
                               upper bounds of the detector range
        - self.parameters: a list containing four doubles, each a parameter.
        - self.analyser: a string giving the name of the analyser to use
        - self.reflection: a string giving the reflection to use
    '''
    __metaclass__ = ABCMeta # Mark as an abstract class
    
    def _run(self):
        '''Defines the workflow for the test'''
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
        self.result_names = [calib.result_workspace()]

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        
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

#------------------------- OSIRIS tests ---------------------------------------

class OSIRISCalibration(ISISIndirectInelasticCalibration):

    def __init__(self):
        ISISIndirectInelasticCalibration.__init__(self)
        self.data_file = 'OSI97935.raw'
        self.detector_range = [963-1, 1004-1]
        self.parameters = [68000.00,70000.00,59000.00,61000.00]
        self.analyser = 'graphite'
        self.reflection = '002'
    
    def get_reference_files(self):
        return ["II.OSIRISCalibration.nxs"]

#------------------------- IRIS tests ---------------------------------------

class IRISCalibration(ISISIndirectInelasticCalibration):

    def __init__(self):
        ISISIndirectInelasticCalibration.__init__(self)
        self.data_file = 'IRS53664.raw'
        self.detector_range = [3-1, 53-1]
        self.parameters = [59000.00,61500.00,62500.00,65000.00]
        self.analyser = 'graphite'
        self.reflection = '002'
    
    def get_reference_files(self):
        return ["II.IRISCalibration.nxs"]


#==============================================================================
class ISISIndirectInelasticResolution(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic resolution tests
    
    The workflow is defined in the _run() method, simply
    define an __init__ method and set the following properties
    on the object
        - self.icon_opt: a dictionary of icon options
        - self.instrument: a string giving the intrument name
        - self.analyser: a string giving the name of the analyser
        - self.reflection: a string giving the name of the reflection
        - self.background: a list of two doubles, giving the background params
        - rebin_params: a comma separated string containing the rebin params
        - self.files: a list of strings containing filenames
    '''
    __metaclass__ = ABCMeta # Mark as an abstract class
    
    def _run(self):
        '''Defines the workflow for the test'''
        self.result_names = [resolution(self.files,
                                        self.icon_opt,
                                        self.rebin_params,
                                        self.background,
                                        self.instrument,
                                        self.analyser,
                                        self.reflection,
                                        # Don't plot from a system test:
                                        plotOpt = False)]

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        
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
    
    def get_reference_files(self):
        return ["II.OSIRISResolution.nxs"]

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
    
    def get_reference_files(self):
        return ["II.IRISResolution.nxs"]


#==============================================================================
class ISISIndirectInelasticDiagnostics(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic diagnostic tests
    
    The workflow is defined in the _run() method, simply
    define an __init__ method and set the following properties
    on the object
    '''
    __metaclass__ = ABCMeta # Mark as an abstract class
    
    def _run(self):
        '''Defines the workflow for the test'''
        slice(self.rawfiles,
              '',# No calib file.
              self.tofRange,
              self.spectra,
              self.suffix,
              Save=False, 
              Verbose=False, 
              Plot=False)
        
        # Construct the result ws name.
        file = self.rawfiles[0]
        self.result_names = [os.path.splitext(file)[0] + "_" + 
                            self.suffix + "_slice"]

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        
        if type(self.rawfiles) != list and len(self.rawfiles) != 2:
            raise RuntimeError("rawfiles should be a list of exactly 2 "
                               "values")
        if type(self.tofRange) != list and len(self.tofRange) != 1:
            raise RuntimeError("tofRange should be a list of exactly 1 "
                               "value")
        if type(self.spectra) != list and len(self.spectra) != 2:
            raise RuntimeError("spectra should be a list of exactly 2 "
                               "values")
        if type(self.suffix) != str:
            raise RuntimeError("suffix property should be a string")

#------------------------- OSIRIS tests ---------------------------------------

class OSIRISDiagnostics(ISISIndirectInelasticDiagnostics):

    def __init__(self):
        ISISIndirectInelasticDiagnostics.__init__(self)
        self.tofRange = [62500,65000]
        self.rawfiles = ['IRS53664.raw']
        self.spectra = [3,53]
        self.suffix = 'graphite002'
    
    def get_reference_files(self):
        return ["II.OSIRISDiagnostics.nxs"]

#------------------------- IRIS tests -----------------------------------------

class IRISDiagnostics(ISISIndirectInelasticDiagnostics):

    def __init__(self):
        ISISIndirectInelasticDiagnostics.__init__(self)
        self.tofRange = [59000,61000]
        self.rawfiles = ['OSI97935.raw']
        self.spectra = [963,1004]
        self.suffix = 'graphite002'
    
    def get_reference_files(self):
        return ["II.IRISDiagnostics.nxs"]