import stresstesting
from mantidsimple import *
import inelastic_indirect_reducer

class IndirectEnergyConversionTest(stresstesting.MantidStressTest):    
    def runTest(self):
        reducer = inelastic_indirect_reducer.IndirectReducer()
        reducer.set_instrument_name('IRIS')
        reducer.set_detector_range(2, 52)
        reducer.append_data_file('irs21360.raw')
        reducer.set_parameter_file('IRIS_graphite_002_Parameters.xml')
        reducer.set_grouping_policy('Individual')
        reducer.set_rebin_string('-0.5,0.005,0.5')
        reducer.reduce()
        ws = reducer.get_result_workspaces()
        RenameWorkspace(ws[0], 'IndirectEnergyConversionTest')

    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('SpectraMap')
        return 'IndirectEnergyConversionTest', 'IndirectEnergyConversionTest.nxs'
