import stresstesting
from mantidsimple import *

import osiris_diffraction_reducer as odr

class OsirisDiffractionTest(stresstesting.MantidStressTest):
    
  def runTest(self):
    # View the ASCII file in Test\Data\ReferenceData\Osiris\ to see how this
    # looks from Arial.
    reducer = odr.OsirisDiffractionReducer()
    reducer.append_data_file('OSI89813.raw') # d1
    reducer.append_data_file('OSI89814.raw') # d2
    reducer.append_data_file('OSI89815.raw') # d3
    reducer.append_data_file('OSI89816.raw') # d4
    reducer.append_data_file('OSI89817.raw') # d5

    # Set cal file
    reducer.set_cal_file('osiris_041_RES10.cal')

    # Add Vanadium files
    reducer.append_vanadium_file('OSI89757')
    reducer.append_vanadium_file('OSI89758')
    reducer.append_vanadium_file('OSI89759')
    reducer.append_vanadium_file('OSI89760')
    reducer.append_vanadium_file('OSI89761')
    reducer.reduce()
    
    ws = reducer.result_workspace()
    
    RenameWorkspace(ws, 'OsirisDiffractionTest')

  def validate(self):
    self.disableChecking.append('Instrument')
    return 'OsirisDiffractionTest', 'OsirisDiffractionTest.nxs'
