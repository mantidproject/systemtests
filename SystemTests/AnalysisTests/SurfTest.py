import stresstesting
from mantidsimple import *

'''
Test File loading and basic data integrity checks of SURF data in Mantid.
'''
class SurfTest(stresstesting.MantidStressTest):    
    def runTest(self):
        Load(Filename='SRF92132.nxs', OutputWorkspace='Surf_nexus')
        Load(Filename='SRF92132.raw', OutputWorkspace='Surf_raw')
        
        a = mtd['Surf_nexus']
        b = mtd['Surf_raw']
        
        self.assertTrue(a.size() == b.size())
        self.assertTrue(a.size() == 22)
        for i in range(0, a.size()):
            self.assertTrue(a[i].getNumberHistograms(), a[i].getNumberHistograms())
            self.assertTrue(len(a[i].readX(0)) == len(b[i].readX(0)))
       
        # Integrate accross the bins in preparation to compare against the benchmark. Only do this for the first workspace in the multi-period group.
        Integration(InputWorkspace=a[0], OutputWorkspace='a_integrated')
        
    def validate(self):
        return 'a_integrated', 'SRF92132_1Integrated.nxs'