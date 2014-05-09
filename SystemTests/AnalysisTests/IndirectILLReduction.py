import stresstesting
import os
from abc import ABCMeta, abstractmethod

from mantid.simpleapi import *


class IndirectILLReductionBase(stresstesting.MantidStressTest):
    '''A common base class for the IndirectILLReduction tests
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


class IndirectILLReductionMinimalTest(IndirectILLReductionBase):
    ''' Test a simple reduction from IN16B.
    '''
    def __init__(self):
        IndirectILLReductionBase.__init__(self)

        run_name = 'ILLIN16B_034745'
        self.kwargs = {}
        self.kwargs['Run'] = run_name + '.nxs'
        self.kwargs['Analyser'] = 'silicon'
        self.kwargs['Reflection'] = '111'
        self.kwargs['RawWorkspace'] = run_name + '_' + self.kwargs['Analyser'] + self.kwargs['Reflection'] + '_raw'
        self.kwargs['ReducedWorkspace'] = run_name + '_' + self.kwargs['Analyser'] + self.kwargs['Reflection'] + '_red'
        self.kwargs['Verbose'] = True

    def _run(self):
        self.tolerance = 1e-7
        IndirectILLReduction(**self.kwargs)
        self.result_names = [self.kwargs['ReducedWorkspace']]

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        pass

    def get_reference_files(self):
        return ["II.IN16BReduction.nxs"]


class IndirectILLReductionMirrorModeTest(IndirectILLReductionBase):
    ''' Test reduction from IN16B using mirror mode.
    '''
    def __init__(self):
        IndirectILLReductionBase.__init__(self)

        run_name = 'ILLIN16B_034745'
        self.kwargs = {}
        self.kwargs['Run'] = run_name + '.nxs'
        self.kwargs['Analyser'] = 'silicon'
        self.kwargs['Reflection'] = '111'
        self.kwargs['RawWorkspace'] = run_name + '_' + self.kwargs['Analyser'] + self.kwargs['Reflection'] + '_raw'
        self.kwargs['ReducedWorkspace'] = run_name + '_' + self.kwargs['Analyser'] + self.kwargs['Reflection'] + '_red'
        self.kwargs['Verbose'] = True

        # additional options for mirror mode
        self.kwargs['MirrorMode'] = True
        self.kwargs['LeftWorkspace'] = self.kwargs['ReducedWorkspace'] + '_left'
        self.kwargs['RightWorkspace'] = self.kwargs['ReducedWorkspace'] + '_right'

    def _run(self):
        self.tolerance = 1e-7
        IndirectILLReduction(**self.kwargs)
        self.result_names = [self.kwargs['ReducedWorkspace'], self.kwargs['LeftWorkspace'], self.kwargs['RightWorkspace']]

    def _validate_properties(self):
        '''Check the object properties are in an expected state to continue'''
        pass

    def get_reference_files(self):
        return ["II.IN16BReductionMirrorModeSum.nxs", "II.IN16BReductionMirrorModeLeft.nxs", "II.IN16BReductionMirrorModeRight.nxs"]
