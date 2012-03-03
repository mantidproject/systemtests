import stresstesting
from mantidsimple import *

class OsirisDiffractionTest(stresstesting.MantidStressTest):
    
  def runTest(self):
    OSIRISDiffractionReduction(
	OutputWorkspace="OsirisDiffractionTest",
	Sample="OSI89813.raw, OSI89814.raw, OSI89815.raw, OSI89816.raw, OSI89817.raw",
	CalFile="osiris_041_RES10.cal",
	Vanadium="OSI89757, OSI89758, OSI89759, OSI89760, OSI89761")

  def validate(self):
    self.disableChecking.append('Instrument')
    return 'OsirisDiffractionTest', 'OsirisDiffractionTest.nxs'
