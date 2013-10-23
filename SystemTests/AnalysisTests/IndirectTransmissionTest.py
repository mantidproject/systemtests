import stresstesting
from mantid.simpleapi import *

class IndirectTransmissionTest(stresstesting.MantidStressTest):
    
    def runTest(self):
    	pass

    def validate(self):
        return 'IRIS_graphite_002_Transmission','IndirectTransmissionTest.nxs'
        