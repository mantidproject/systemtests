import stresstesting
from mantid.simpleapi import *

class FocusTest(stresstesting.MantidStressTest):
    
    def runTest(self):
        '''A simple test of the focussing chain on our test GEM data'''
        GEM=LoadRaw(Filename='GEM38370.raw', 'GEM')
        GEM=AlignDetectors(GEM, 'offsets_2006_cycle064.cal')
        GEM=DiffractionFocussing('GEM', 'offsets_2006_cycle064.cal')
        
    def maxIterations(self):
        return 5
       

