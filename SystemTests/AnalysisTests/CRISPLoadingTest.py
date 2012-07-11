from LoadAndCheckBase import *

'''
Test File loading and basic data integrity checks of CRISP data in Mantid.
'''
class CRISPLoadingTest(LoadAndCheckBase):
    def get_raw_workspace_filename(self):
        return "CSP85423.raw"
        
    def get_nexus_workspace_filename(self):
        return "CSP85423.nxs"
        
    def get_expected_number_of_periods(self):
        return 2
    
    def get_integrated_reference_workspace_filename(self):
        return "CSP85423_1Integrated.nxs"