import stresstesting
from mantidsimple import *

import inelastic_indirect_reducer

class TOSCAReductionTest(stresstesting.MantidStressTest):
    
  def runTest(self):
    reducer = inelastic_indirect_reducer.IndirectReducer()
    reducer.set_instrument_name('TOSCA')
    reducer.set_detector_range(0,139)
    reducer.append_data_file('TSC11453.raw')
    reducer.set_rebin_string('-2.5,0.015,3,-0.005,1000')
    reducer.reduce()
    ws = reducer.get_result_workspaces()[0]
    RenameWorkspace(ws, 'ToscaReductionTest')

  def validate(self):
    self.disableChecking.append('Instrument')
    return 'ToscaReductionTest', 'TOSCAReductionTest.nxs'
