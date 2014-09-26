import stresstesting
import os
from abc import ABCMeta, abstractmethod

from mantid.simpleapi import *

# For debugging only.
from mantid.api import FileFinder

# Import our workflows.
from inelastic_indirect_reducer import IndirectReducer
from inelastic_indirect_reduction_steps import CreateCalibrationWorkspace
from IndirectEnergyConversion import resolution, slice
from IndirectDataAnalysis import elwin, msdfit, fury, furyfitSeq, furyfitMult, confitSeq

'''
- TOSCA only supported by "Reduction" (the Energy Transfer tab of C2E).
- OSIRIS/IRIS supported by all tabs / interfaces.
- VESUVIO is not supported by any interface as of yet.

For diagrams on the intended work flow of the IDA and Indirect parts of the
C2E interface, please see:

- http://www.mantidproject.org/IDA
- http://www.mantidproject.org/Indirect

System test class hierarchy as shown below:

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
     |   |
     |   +--IRISDiagnostics
     |   +--OSIRISDiagnostics
     |
     +--ISISIndirectInelasticMoments
     |   |
     |   +--IRISMoments
     |   +--OSIRISMoments
     |
     +--ISISIndirectInelasticElwinAndMSDFit
     |   |
     |   +--IRISElwinAndMSDFit
     |   +--OSIRISElwinAndMSDFit
     |
     +--ISISIndirectInelasticFuryAndFuryFit
     |   |
     |   +--IRISFuryAndFuryFit
     |   +--OSIRISFuryAndFuryFit
     |
     +--ISISIndirectInelasticFuryAndFuryFitMulti
     |   |
     |   +--IRISFuryAndFuryFitMulti
     |   +--OSIRISFuryAndFuryFitMulti
     |
     +--ISISIndirectInelasticConvFit
     |   |
     |   +--IRISConvFit
     |   +--OSIRISConvFit
     |
'''


class ISISIndirectInelasticBase(stresstesting.MantidStressTest):
    '''A common base class for the ISISIndirectInelastic* base classes.
    '''

    __metaclass__ = ABCMeta  # Mark as an abstract class

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

        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Axes')

        for reference_file, result in zip(self.get_reference_files(),
                                          self.result_names):
            wsName = "RefFile"
            if reference_file.endswith('.nxs'):
                LoadNexus(Filename=reference_file, OutputWorkspace=wsName)
            else:
                raise RuntimeError("Should supply a NeXus file: %s" %
                                   reference_file)

            if not self.validateWorkspaces([result, wsName]):
                print str([reference_file, result]) + " do not match."
                return False

        return True

    def get_temp_dir_path(self, filename):
        '''Given a filename, prepends the system test temporary directory
        and returns the full path.'''
        return os.path.join(config['defaultsave.directory'], filename)


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

    __metaclass__ = ABCMeta  # Mark as an abstract class
    sum_files = False

    def _run(self):
        self.tolerance = 1e-7
        '''Defines the workflow for the test'''
        reducer = IndirectReducer()
        reducer.set_instrument_name(self.instr_name)
        reducer.set_detector_range(self.detector_range[0],
                                   self.detector_range[1])
        reducer.set_sum_files(self.sum_files)
        self.parameter_file = self.instr_name + '_graphite_002_Parameters.xml'
        reducer.set_parameter_file(self.parameter_file)

        for name in self.data_files:
            reducer.append_data_file(name)

        if self.rebin_string is not None:
            reducer.set_rebin_string(self.rebin_string)

        # Do the reduction and rename the result.
        reducer.reduce()
        self.result_names = sorted(reducer.get_result_workspaces())

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        if type(self.instr_name) != str:
            raise RuntimeError("instr_name property should be a string")
        if type(self.detector_range) != list and len(self.detector_range) != 2:
            raise RuntimeError("detector_range should be a list of exactly 2 "
                               "values")
        if type(self.data_files) != list:
            raise RuntimeError("data_file property should be a string")
        if self.rebin_string is not None and type(self.rebin_string) != str:
            raise RuntimeError("rebin_string property should be a string")
        if self.sum_files is not None and type(self.sum_files) != bool:
            raise RuntimeError("sum_files property should be a bool")

#------------------------- TOSCA tests ----------------------------------------


class TOSCAReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'TOSCA'
        self.detector_range = [0, 139]
        self.data_files = ['TSC15352.raw']
        self.rebin_string = '-2.5,0.015,3,-0.005,1000'

    def get_reference_files(self):
        return ["II.TOSCAReductionFromFile.nxs"]

class TOSCAMultiFileReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'TOSCA'
        self.detector_range = [0, 139]
        self.data_files = ['TSC15352.raw', 'TSC15353.raw','TSC15354.raw']
        self.rebin_string = '-2.5,0.015,3,-0.005,1000'

    def get_reference_files(self):
        #note that the same run for single reduction is used.
        #as they should be the same
        return ['II.TOSCAReductionFromFile.nxs', 'II.TOSCAMultiFileReduction1.nxs', 'II.TOSCAMultiFileReduction2.nxs']

class TOSCAMultiFileSummedReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'TOSCA'
        self.detector_range = [0, 139]
        self.data_files = ['TSC15352.raw', 'TSC15353.raw','TSC15354.raw']
        self.rebin_string = '-2.5,0.015,3,-0.005,1000'
        self.sum_files = True

    def get_reference_files(self):
        return ['II.TOSCAMultiFileSummedReduction.nxs']


#------------------------- OSIRIS tests ---------------------------------------


class OSIRISReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'OSIRIS'
        self.detector_range = [962, 1003]
        self.data_files = ['OSIRIS00106550.raw']
        self.rebin_string = None

    def get_reference_files(self):
        return ["II.OSIRISReductionFromFile.nxs"]

class OSIRISMultiFileReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'OSIRIS'
        self.detector_range = [962, 1003]
        self.data_files = ['OSIRIS00106550.raw',' OSIRIS00106551.raw']
        self.rebin_string = None

    def get_reference_files(self):
        #note that the same run for single reduction is used.
        #as they should be the same
        return ['II.OSIRISReductionFromFile.nxs','II.OSIRISMultiFileReduction1.nxs']

class OSIRISMultiFileSummedReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'OSIRIS'
        self.detector_range = [962, 1003]
        self.data_files = ['OSIRIS00106550.raw', 'OSIRIS00106551.raw']
        self.rebin_string = None
        self.sum_files = True

    def get_reference_files(self):
        return ['II.OSIRISMultiFileSummedReduction.nxs']

#------------------------- IRIS tests -----------------------------------------

class IRISReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'IRIS'
        self.detector_range = [2, 52]
        self.data_files = ['IRS21360.raw']
        self.rebin_string = None

    def get_reference_files(self):
        return ["II.IRISReductionFromFile.nxs"]


class IRISMultiFileReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'IRIS'
        self.detector_range = [2, 52]
        self.data_files = ['IRS21360.raw', 'IRS53664.raw']
        self.rebin_string = None

    def get_reference_files(self):
        return ['II.IRISReductionFromFile.nxs', 'II.IRISMultiFileReduction1.nxs']


class IRISMultiFileSummedReduction(ISISIndirectInelasticReduction):

    def __init__(self):
        ISISIndirectInelasticReduction.__init__(self)
        self.instr_name = 'IRIS'
        self.detector_range = [2, 52]
        self.data_files = ['IRS21360.raw', 'IRS53664.raw']
        self.sum_files = True
        self.rebin_string = None

    def get_reference_files(self):
        #note that the same run for single reduction is used.
        #as they should be the same
        return ['II.IRISMultiFileSummedReduction.nxs']

#--------------------- Generic Reduction tests -----------------------------

class ISISIndirectInelasticReductionOutput(stresstesting.MantidStressTest):

    def runTest(self):
        reducer = self._setup_reducer()
        reducer.reduce()
        self.result_names = sorted(reducer.get_result_workspaces())
        
    def validate(self):
        self.assertEqual(len(self.result_names), 1)
        self.result_name = self.result_names[0]

        self.output_file_names = self._get_file_names()
        self.assert_reduction_output_exists(self.output_file_names)
        self.assert_ascii_file_matches()
        self.assert_aclimax_file_matches()
        self.assert_spe_file_matches()

    def cleanup(self):
        mtd.clear()

        for file_path in self.output_file_names.itervalues():
            if os.path.isfile(file_path):
                os.remove(file_path)

    def assert_ascii_file_matches(self):
        expected_result = [
            'X , Y0 , E0 , Y1 , E1 , Y2 , E2',
            '-2.4925,0,0,0.617579,0.362534,0.270868,0.159006', 
            '-2.4775,0.375037,0.273017,0,0,0.210547,0.153272'
        ]
        self.assert_file_format_matches_expected(expected_result, self.output_file_names['ascii'],
                                                 "Output of ASCII format did not match expected result.")

    def assert_aclimax_file_matches(self):
        expected_result = [
            '# X \t Y \t E',
            '0',
            '3.0075\t0.175435\t0.115017'
        ]
        self.assert_file_format_matches_expected(expected_result, self.output_file_names['aclimax'],
                                                 "Output of aclimax format did not match expected result.")

    def assert_spe_file_matches(self):
        expected_result = [
            '       3    1532', 
            '### Phi Grid',
            ' 5.000E-01 1.500E+00 2.500E+00 3.500E+00',
            '### Energy Grid',
            '-2.500E+00-2.485E+00-2.470E+00-2.455E+00-2.440E+00-2.425E+00-2.410E+00-2.395E+00'
        ]
        self.assert_file_format_matches_expected(expected_result, self.output_file_names['spe'],
                                                 "Output of SPE format did not match expected result.")

    def assert_reduction_output_exists(self, output_file_names):
        for file_path in output_file_names.itervalues():
            self.assertTrue(os.path.exists(file_path), "File does not exist in the default save directory")
            self.assertTrue(os.path.isfile(file_path), "Output file of reduction output is not a file.")

    def assert_file_format_matches_expected(self, expected_result, file_path, msg=""):
        num_lines = len(expected_result)
        actual_result = self._read_ascii_file(file_path, num_lines)
        self.assertTrue(actual_result == expected_result, msg + " (%s != %s)" % (actual_result, expected_result))

    def _setup_reducer(self):
        self.file_formats = ['nxs', 'spe', 'nxspe', 'ascii', 'aclimax']
        self.file_extensions = ['.nxs', '.spe', '.nxspe', '.dat', '_aclimax.dat']
        self.instr_name = 'TOSCA'
        self.detector_range = [0, 139]
        self.data_files = ['TSC15352.raw']
        self.rebin_string = '-2.5,0.015,3,-0.005,1000'
        self.parameter_file = self.instr_name + '_graphite_002_Parameters.xml'

        reducer = IndirectReducer()
        reducer.set_instrument_name(self.instr_name)
        reducer.set_detector_range(self.detector_range[0],
                                   self.detector_range[1])
        reducer.set_sum_files(False)
        reducer.set_parameter_file(self.parameter_file)
        reducer.set_save_formats(self.file_formats)

        for name in self.data_files:
            reducer.append_data_file(name)

        if self.rebin_string is not None:
            reducer.set_rebin_string(self.rebin_string)

        return reducer

    def _read_ascii_file(self, path, num_lines):
        with open(path,'rb') as file_handle:
            lines = [file_handle.readline().rstrip() for _ in xrange(num_lines)]
            return lines

    def _get_file_names(self):
        working_directory = config['defaultsave.directory']
        
        output_names = {}
        for format, ext in zip(self.file_formats, self.file_extensions):
            output_file_name = self.result_name + ext
            output_file_name = os.path.join(working_directory, output_file_name)
            output_names[format] = output_file_name

        return output_names

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

    __metaclass__ = ABCMeta  # Mark as an abstract class

    def _run(self):
        '''Defines the workflow for the test'''
        self.tolerance = 1e-7

        self.result_names = ['IndirectCalibration_Output']

        CreateCalibrationWorkspace(InputFiles=self.data_file,
                                   OutputWorkspace='IndirectCalibration_Output',
                                   DetectorRange=self.detector_range,
                                   PeakRange=self.peak,
                                   BackgroundRange=self.back)

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''

        if type(self.data_file) != str:
            raise RuntimeError("data_file property should be a string")
        if type(self.detector_range) != list and len(self.detector_range) != 2:
            raise RuntimeError("detector_range should be a list of exactly 2 values")
        if type(self.peak) != list and len(self.peak) != 2:
            raise RuntimeError("peak should be a list of exactly 2 values")
        if type(self.back) != list and len(self.back) != 2:
            raise RuntimeError("back should be a list of exactly 2 values")

#------------------------- OSIRIS tests ---------------------------------------


class OSIRISCalibration(ISISIndirectInelasticCalibration):

    def __init__(self):
        ISISIndirectInelasticCalibration.__init__(self)
        self.data_file = 'OSI97935.raw'
        self.detector_range = [963, 1004]
        self.back = [68000.00, 70000.00]
        self.peak = [59000.00, 61000.00]

    def get_reference_files(self):
        return ["II.OSIRISCalibration.nxs"]

#------------------------- IRIS tests ---------------------------------------


class IRISCalibration(ISISIndirectInelasticCalibration):

    def __init__(self):
        ISISIndirectInelasticCalibration.__init__(self)
        self.data_file = 'IRS53664.raw'
        self.detector_range = [3, 53]
        self.back = [59000.00, 61500.00]
        self.peak = [62500.00, 65000.00]

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

    __metaclass__ = ABCMeta  # Mark as an abstract class

    def _run(self):
        self.tolerance = 1e-7
        '''Defines the workflow for the test'''
        self.result_names = [resolution(self.files,
                                        self.icon_opt,
                                        self.rebin_params,
                                        self.background,
                                        self.instrument,
                                        self.analyser,
                                        self.reflection,
                                        # Don't plot from a system test:
                                        Plot=False)]

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
        self.icon_opt = {'first': 963, 'last': 1004}
        self.instrument = 'OSIRIS'
        self.analyser = 'graphite'
        self.reflection = '002'
        self.background = [-0.563032, 0.605636]
        self.rebin_params = '-0.2,0.002,0.2'
        self.files = ['OSI97935.raw']

    def get_reference_files(self):
        return ["II.OSIRISResolution.nxs"]

#------------------------- IRIS tests -----------------------------------------


class IRISResolution(ISISIndirectInelasticResolution):

    def __init__(self):
        ISISIndirectInelasticResolution.__init__(self)
        self.icon_opt = {'first': 3, 'last': 53}
        self.instrument = 'IRIS'
        self.analyser = 'graphite'
        self.reflection = '002'
        self.background = [-0.54, 0.65]
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

    __metaclass__ = ABCMeta  # Mark as an abstract class

    def _run(self):
        '''Defines the workflow for the test'''

        self.tolerance = 1e-7
        slice(self.rawfiles,
              '',  # No calib file.
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


class IRISDiagnostics(ISISIndirectInelasticDiagnostics):

    def __init__(self):
        ISISIndirectInelasticDiagnostics.__init__(self)
        self.tofRange = [62500, 65000]
        self.rawfiles = ['IRS53664.raw']
        self.spectra = [3, 53]
        self.suffix = 'graphite002'

    def get_reference_files(self):
        return ["II.IRISDiagnostics.nxs"]

#------------------------- IRIS tests -----------------------------------------


class OSIRISDiagnostics(ISISIndirectInelasticDiagnostics):

    def __init__(self):
        ISISIndirectInelasticDiagnostics.__init__(self)
        self.tofRange = [59000, 61000]
        self.rawfiles = ['OSI97935.raw']
        self.spectra = [963, 1004]
        self.suffix = 'graphite002'

    def get_reference_files(self):
        return ["II.OSIRISDiagnostics.nxs"]


#==============================================================================
class ISISIndirectInelasticMoments(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic Fury/FuryFit tests

    The output of Elwin is usually used with MSDFit and so we plug one into
    the other in this test.
    '''
    # Mark as an abstract class
    __metaclass__ = ABCMeta

    def _run(self):
        '''Defines the workflow for the test'''

        LoadNexus(self.input_workspace,
                  OutputWorkspace=self.input_workspace)

        SofQWMoments(Sample=self.input_workspace, EnergyMin=self.e_min,
                     EnergyMax=self.e_max, Scale=self.scale,
                     Verbose=False, Plot=False, Save=False, OutputWorkspace=self.input_workspace + '_Moments')

        self.result_names = [self.input_workspace + '_Moments']

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''

        if type(self.input_workspace) != str:
            raise RuntimeError("Input workspace should be a string.")
        if type(self.e_min) != float:
            raise RuntimeError("Energy min should be a float")
        if type(self.e_max) != float:
            raise RuntimeError("Energy max should be a float")
        if type(self.scale) != float:
            raise RuntimeError("Scale should be a float")


#------------------------- OSIRIS tests ---------------------------------------
class OSIRISMoments(ISISIndirectInelasticMoments):

    def __init__(self):
        ISISIndirectInelasticMoments.__init__(self)
        self.input_workspace = 'osi97935_graphite002_sqw.nxs'
        self.e_min = -0.4
        self.e_max = 0.4
        self.scale = 1.0

    def get_reference_files(self):
        return ['II.OSIRISMoments.nxs']


#------------------------- IRIS tests -----------------------------------------
class IRISMoments(ISISIndirectInelasticMoments):

    def __init__(self):
        ISISIndirectInelasticMoments.__init__(self)
        self.input_workspace = 'irs53664_graphite002_sqw.nxs'
        self.e_min = -0.4
        self.e_max = 0.4
        self.scale = 1.0

    def get_reference_files(self):
        return ['II.IRISMoments.nxs']


#==============================================================================
class ISISIndirectInelasticElwinAndMSDFit(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic Elwin/MSD Fit tests

    The output of Elwin is usually used with MSDFit and so we plug one into
    the other in this test.
    '''

    __metaclass__ = ABCMeta  # Mark as an abstract class

    def _run(self):
        '''Defines the workflow for the test'''
        self.tolerance = 1e-7
        elwin_results = elwin(self.files,
                              self.eRange,
                              Save=False,
                              Verbose=False,
                              Plot=False)

        #Manually set the Elf file label
        elf_ws = elwin_results[0][:-3] + "elf"
        units = mtd[elf_ws].getAxis(0).setUnit("Label")
        units.setLabel("Temperature", "K")

        #Append Elf file for saving
        elwin_results = elwin_results + (elf_ws,)

        int_files = [self.get_temp_dir_path(filename) + ".nxs"
                     for filename in elwin_results]

        # Save the EQ1 & EQ2 results from Elwin to put into MSDFit.
        for ws, filename in zip(elwin_results, int_files):
            SaveNexusProcessed(Filename=filename,
                               InputWorkspace=ws)

        eq2_file = elwin_results[1]
        msdfit_result = msdfit(eq2_file,
                               startX=self.startX,
                               endX=self.endX,
                               Save=False,
                               Verbose=True,
                               Plot=False)

        # @TODO: MSDFit has some other, as yet unfinalised, workspaces as its
        #        output.  We need to test these too, eventually.

        # Annoyingly, MSDFit eats the EQ2 workspaces we feed it, so let's
        # reload them for checking against the reference files later.
        for ws, filename in zip(elwin_results, int_files):
            LoadNexusProcessed(Filename=filename,
                               OutputWorkspace=ws)

            # check label properties were saved correctly
            if(ws[-3:] == "elf"):
                units = mtd[ws].getAxis(0).getUnit()
                self.assertTrue(units.caption() == "Temperature")
                self.assertTrue(units.label() == "K")

        # Clean up the intermediate files.
        for filename in int_files:
            os.remove(filename)

        # We're interested in the intermediate Elwin results as well as the
        # final MSDFit result.
        self.result_names = [elwin_results[0],  # EQ1
                             elwin_results[1],  # EQ2
                             msdfit_result]

    def _validate_properties(self):
        """Check the object properties are in an expected state to continue"""

        if type(self.files) != list or len(self.files) != 2:
            raise RuntimeError("files should be a list of exactly 2 "
                               "strings")
        if type(self.eRange) != list or len(self.eRange) != 2:
            raise RuntimeError("eRange should be a list of exactly 2 "
                               "values")
        if type(self.startX) != float:
            raise RuntimeError("startX should be a float")
        if type(self.endX) != float:
            raise RuntimeError("endX should be a float")

#------------------------- OSIRIS tests ---------------------------------------


class OSIRISElwinAndMSDFit(ISISIndirectInelasticElwinAndMSDFit):

    def __init__(self):
        ISISIndirectInelasticElwinAndMSDFit.__init__(self)
        self.files = ['osi97935_graphite002_red.nxs',
                      'osi97936_graphite002_red.nxs']
        self.eRange = [-0.02, 0.02]
        self.startX = 0.195082
        self.endX = 3.202128

    def get_reference_files(self):
        return ['II.OSIRISElwinEQ1.nxs',
                'II.OSIRISElwinEQ2.nxs',
                'II.OSIRISMSDFit.nxs']

#------------------------- IRIS tests -----------------------------------------


class IRISElwinAndMSDFit(ISISIndirectInelasticElwinAndMSDFit):

    def __init__(self):
        ISISIndirectInelasticElwinAndMSDFit.__init__(self)
        self.files = ['irs53664_graphite002_red.nxs',
                      'irs53665_graphite002_red.nxs']
        self.eRange = [-0.02, 0.02]
        self.startX = 0.313679
        self.endX = 3.285377

    def get_reference_files(self):
        return ['II.IRISElwinEQ1.nxs',
                'II.IRISElwinEQ2.nxs',
                'II.IRISMSDFit.nxs']


#==============================================================================
class ISISIndirectInelasticFuryAndFuryFit(ISISIndirectInelasticBase):
    '''
    A base class for the ISIS indirect inelastic Fury/FuryFit tests

    The output of Fury is usually used with FuryFit and so we plug one into
    the other in this test.
    '''

    __metaclass__ = ABCMeta  # Mark as an abstract class

    def _run(self):
        '''Defines the workflow for the test'''
        self.tolerance = 1e-7
        self.samples = [sample[:-4] for sample in self.samples]

        #load files into mantid
        for sample in self.samples:
            LoadNexus(sample, OutputWorkspace=sample)
        LoadNexus(self.resolution, OutputWorkspace=self.resolution)

        fury_ws = fury(self.samples,
                       self.resolution,
                       self.rebin,
                       Save=False,
                       Verbose=False,
                       Plot=False)

        """TODO: Move Fury code to Python so that we can call it here."""

        # Test FuryFit Sequential
        furyfitSeq_ws = furyfitSeq(fury_ws[0],
                                   self.func,
                                   self.ftype,
                                   self.startx,
                                   self.endx,
                                   Save=False,
                                   Plot='None',
                                   Verbose=False)

        self.result_names = [fury_ws[0],
                             furyfitSeq_ws]

        #remove workspaces from mantid
        for sample in self.samples:
            DeleteWorkspace(sample)

        DeleteWorkspace(self.resolution)

    def _validate_properties(self):
        """Check the object properties are in an expected state to continue"""

        if type(self.samples) != list:
            raise RuntimeError("Samples should be a list of strings.")
        if type(self.resolution) != str:
            raise RuntimeError("Resolution should be a string.")
        if type(self.rebin) != str:
            raise RuntimeError("Rebin should be a string.")
        if type(self.func) != str:
            raise RuntimeError("Function should be a string.")
        if type(self.ftype) != str:
            raise RuntimeError("Function type should be a string.")
        if type(self.startx) != float:
            raise RuntimeError("startx should be a float")
        if type(self.endx) != float:
            raise RuntimeError("endx should be a float")

#------------------------- OSIRIS tests ---------------------------------------


class OSIRISFuryAndFuryFit(ISISIndirectInelasticFuryAndFuryFit):

    def __init__(self):
        ISISIndirectInelasticFuryAndFuryFit.__init__(self)
        # Fury
        self.samples = ['osi97935_graphite002_red.nxs']
        self.resolution = 'osi97935_graphite002_res.nxs'
        self.rebin = '-0.400000,0.002000,0.400000'
        # Fury Seq Fit
        self.func = r'name=LinearBackground,A0=0,A1=0,ties=(A1=0);name=UserFunction,Formula=Intensity*exp(-(x/Tau)),Intensity=0.304185,Tau=100;ties=(f1.Intensity=1-f0.A0)'
        self.ftype = '1E_s'
        self.startx = 0.022861
        self.endx = 0.118877

    def get_reference_files(self):
        return ['II.OSIRISFury.nxs',
                'II.OSIRISFuryFitSeq.nxs']

#------------------------- IRIS tests -----------------------------------------


class IRISFuryAndFuryFit(ISISIndirectInelasticFuryAndFuryFit):

    def __init__(self):
        ISISIndirectInelasticFuryAndFuryFit.__init__(self)
        # Fury
        self.samples = ['irs53664_graphite002_red.nxs']
        self.resolution = 'irs53664_graphite002_res.nxs'
        self.rebin = '-0.400000,0.002000,0.400000'
        # Fury Seq Fit
        self.func = r'name=LinearBackground,A0=0,A1=0,ties=(A1=0);name=UserFunction,Formula=Intensity*exp(-(x/Tau)),Intensity=0.355286,Tau=100;ties=(f1.Intensity=1-f0.A0)'
        self.ftype = '1E_s'
        self.startx = 0.013717
        self.endx = 0.169171

    def get_reference_files(self):
        return ['II.IRISFury.nxs',
                'II.IRISFuryFitSeq.nxs']

#==============================================================================


class ISISIndirectInelasticFuryAndFuryFitMulti(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic Fury/FuryFit tests

    The output of Elwin is usually used with MSDFit and so we plug one into
    the other in this test.
    '''

    __metaclass__ = ABCMeta  # Mark as an abstract class

    def _run(self):
        '''Defines the workflow for the test'''
        self.tolerance = 1e-6
        self.samples = [sample[:-4] for sample in self.samples]

        #load files into mantid
        for sample in self.samples:
            LoadNexus(sample, OutputWorkspace=sample)
        LoadNexus(self.resolution, OutputWorkspace=self.resolution)

        fury_ws = fury(self.samples,
                       self.resolution,
                       self.rebin,
                       Save=False,
                       Verbose=False,
                       Plot=False)

        """TODO: Move Fury code to Python so that we can call it here."""

        # Test FuryFit Sequential
        furyfitSeq_ws = furyfitMult(fury_ws[0],
                                    self.func,
                                    self.ftype,
                                    self.startx,
                                    self.endx,
                                    Save=False,
                                    Plot='None',
                                    Verbose=False)

        self.result_names = [fury_ws[0],
                             furyfitSeq_ws]

        #remove workspaces from mantid
        for sample in self.samples:
            DeleteWorkspace(sample)
        DeleteWorkspace(self.resolution)

    def _validate_properties(self):
        """Check the object properties are in an expected state to continue"""

        if type(self.samples) != list:
            raise RuntimeError("Samples should be a list of strings.")
        if type(self.resolution) != str:
            raise RuntimeError("Resolution should be a string.")
        if type(self.rebin) != str:
            raise RuntimeError("Rebin should be a string.")
        if type(self.func) != str:
            raise RuntimeError("Function should be a string.")
        if type(self.ftype) != str:
            raise RuntimeError("Function type should be a string.")
        if type(self.startx) != float:
            raise RuntimeError("startx should be a float")
        if type(self.endx) != float:
            raise RuntimeError("endx should be a float")

#------------------------- OSIRIS tests ---------------------------------------


class OSIRISFuryAndFuryFitMulti(ISISIndirectInelasticFuryAndFuryFitMulti):

    def __init__(self):
        ISISIndirectInelasticFuryAndFuryFitMulti.__init__(self)
        # Fury
        self.samples = ['osi97935_graphite002_red.nxs']
        self.resolution = 'osi97935_graphite002_res.nxs'
        self.rebin = '-0.400000,0.002000,0.400000'
        # Fury Seq Fit
        self.func = r'name=LinearBackground,A0=0.510595,A1=0,ties=(A1=0);name=UserFunction,Formula=Intensity*exp( -(x/Tau)^Beta),Intensity=0.489405,Tau=0.105559,Beta=1.61112e-14;ties=(f1.Intensity=1-f0.A0)'
        self.ftype = '1E_s'
        self.startx = 0.0
        self.endx = 0.119681

    def get_reference_files(self):
        return ['II.OSIRISFury.nxs',
                'II.OSIRISFuryFitMulti.nxs']

#------------------------- IRIS tests -----------------------------------------


class IRISFuryAndFuryFitMulti(ISISIndirectInelasticFuryAndFuryFitMulti):

    def __init__(self):
        ISISIndirectInelasticFuryAndFuryFitMulti.__init__(self)
        # Fury
        self.samples = ['irs53664_graphite002_red.nxs']
        self.resolution = 'irs53664_graphite002_res.nxs'
        self.rebin = '-0.400000,0.002000,0.400000'
        # Fury Seq Fit
        self.func = r'name=LinearBackground,A0=0.584488,A1=0,ties=(A1=0);name=UserFunction,Formula=Intensity*exp( -(x/Tau)^Beta),Intensity=0.415512,Tau=4.848013e-14,Beta=0.022653;ties=(f1.Intensity=1-f0.A0)'
        self.ftype = '1S_s'
        self.startx = 0.0
        self.endx = 0.156250

    def get_reference_files(self):
        return ['II.IRISFury.nxs',
                'II.IRISFuryFitMulti.nxs']

#==============================================================================


class ISISIndirectInelasticConvFit(ISISIndirectInelasticBase):
    '''A base class for the ISIS indirect inelastic ConvFit tests

    The workflow is defined in the _run() method, simply
    define an __init__ method and set the following properties
    on the object
    '''
    # Mark as an abstract class
    __metaclass__ = ABCMeta

    def _run(self):
        '''Defines the workflow for the test'''
        self.tolerance = 1e-4
        LoadNexus(self.sample, OutputWorkspace=self.sample)

        confitSeq(
            self.sample,
            self.func,
            self.startx,
            self.endx,
            self.ftype,
            self.bg,
            specMin=self.spectra_min,
            specMax=self.spectra_max,
            Verbose=False,
            Plot='None',
            Save=False)

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''

        if type(self.sample) != str:
            raise RuntimeError("Sample should be a string.")
        if type(self.resolution) != str:
            raise RuntimeError("Resolution should be a string.")
        if not os.path.isfile(self.resolution):
            raise RuntimeError("Resolution must be a file that exists.")
        if type(self.func) != str:
            raise RuntimeError("Function should be a string.")
        if type(self.bg) != str:
            raise RuntimeError("Background type should be a string.")
        if type(self.ftype) != str:
            raise RuntimeError("Function type should be a string.")
        if type(self.startx) != float:
            raise RuntimeError("startx should be a float")
        if type(self.endx) != float:
            raise RuntimeError("endx should be a float")
        if type(self.spectra_min) != int:
            raise RuntimeError("Min spectrum should be a int")
        if type(self.spectra_max) != int:
            raise RuntimeError("Max spectrum should be a int")
        if type(self.ties) != bool:
            raise RuntimeError("ties should be a boolean.")

#------------------------- OSIRIS tests ---------------------------------------


class OSIRISConvFit(ISISIndirectInelasticConvFit):

    def __init__(self):
        ISISIndirectInelasticConvFit.__init__(self)
        self.sample = 'osi97935_graphite002_red.nxs'
        self.resolution = FileFinder.getFullPath('osi97935_graphite002_res.nxs')
        #ConvFit fit function
        self.func = 'name=LinearBackground,A0=0,A1=0;(composite=Convolution,FixResolution=true,NumDeriv=true;name=Resolution,FileName=\"%s\";name=Lorentzian,Amplitude=2,PeakCentre=0,FWHM=0.05)' % self.resolution
        self.ftype = '1L'
        self.startx = -0.2
        self.endx = 0.2
        self.bg = 'FitL_s'
        self.spectra_min = 0
        self.spectra_max = 41
        self.ties = False

        self.result_names = ['osi97935_graphite002_conv_1LFitL_0_to_41_Result']

    def get_reference_files(self):
        return ['II.OSIRISConvFitSeq.nxs']


#------------------------- IRIS tests -----------------------------------------
class IRISConvFit(ISISIndirectInelasticConvFit):

    def __init__(self):
        ISISIndirectInelasticConvFit.__init__(self)
        self.sample = 'irs53664_graphite002_red.nxs'
        self.resolution = FileFinder.getFullPath('irs53664_graphite002_res.nxs')
        #ConvFit fit function
        self.func = 'name=LinearBackground,A0=0.060623,A1=0.001343;(composite=Convolution,FixResolution=true,NumDeriv=true;name=Resolution,FileName=\"%s\";name=Lorentzian,Amplitude=1.033150,PeakCentre=-0.000841,FWHM=0.001576)' % self.resolution
        self.ftype = '1L'
        self.startx = -0.2
        self.endx = 0.2
        self.bg = 'FitL_s'
        self.spectra_min = 0
        self.spectra_max = 50
        self.ties = False

        self.result_names = ['irs53664_graphite002_conv_1LFitL_0_to_50_Result']

    def get_reference_files(self):
        return ['II.IRISConvFitSeq.nxs']
