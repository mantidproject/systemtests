"""
   Extends the basic test of the Load algorithm done by the LoadLotsOfFiles
   test to encompass the complex multi-file loading that the Load
   algorithm is capable of.
"""
import stresstesting

from mantid.api import AnalysisDataService, IEventWorkspace, MatrixWorkspace, WorkspaceGroup
from mantid.simpleapi import Load

import unittest

DIFF_PLACES = 12

class LoadTest(stresstesting.MantidStressTest):

    def runTest(self):
        self._success = False

        # Custom code to create and run this single test suite
        # and then mark as success or failure
        suite = unittest.TestSuite()
        suite.addTest( unittest.makeSuite(LoadTests, "test") )
        runner = unittest.TextTestRunner()
        # Run using either runner
        res = runner.run(suite)
        if res.wasSuccessful():
            self._success = True 
        else:
            self._success = False

    def validate(self):
        return self._success

#------------------------------------------------------------------------------
# work horse
class LoadTests(unittest.TestCase):

    wsname = "__LoadTest"
    cleanup_names = []

    def tearDown(self):
        self.cleanup_names.append(self.wsname)
        for name in self.cleanup_names:
            try:
                AnalysisDataService.remove(name)
            except KeyError:
                pass
        self.cleanup_names = []

    def test_csv_list_with_same_instrument_produces_single_group(self):
        data = Load("OFFSPEC10791,10792,10793.raw", OutputWorkspace = self.wsname)

        self.assertTrue(isinstance(data, WorkspaceGroup))
        self.assertEquals(6, data.getNumberOfEntries())
        ads_names = ["OFFSPEC00010791_1", "OFFSPEC00010791_2",
                     "OFFSPEC00010792_1", "OFFSPEC00010792_2",
                     "OFFSPEC00010793_1", "OFFSPEC00010793_2"]
        for name in ads_names:
            self.assertTrue(name in AnalysisDataService)

        deleted_names = ["OFFSPEC10791", "OFFSPEC10792", "OFFSPEC10793"]
        for name in deleted_names:
            self.assertTrue(name not in AnalysisDataService)

        self.cleanup_names = ads_names

    def test_csv_list_with_different_instrument_produces_single_group(self):
        # Combine test of different instruments with giving the output name
        # the same name as one of the members of the group
        self.wsname = "LOQ99631"
        data = Load("LOQ99631.RAW, CSP85423.raw", OutputWorkspace = self.wsname)

        self.assertTrue(isinstance(data, WorkspaceGroup))
        self.assertEquals(3, data.getNumberOfEntries())
        ads_names = ["LOQ99631", "CSP85423_1", "CSP85423_2"]
        for name in ads_names:
            self.assertTrue(name in AnalysisDataService)

        deleted_names = ["CSP85423"]
        for name in deleted_names:
            self.assertTrue(name not in AnalysisDataService)

        self.cleanup_names = ads_names
        self.wsname = "__LoadTest"

    def test_extra_properties_passed_to_loader(self):
        data = Load("CNCS_7860_event.nxs", OutputWorkspace = self.wsname,
                    BankName = "bank1", SingleBankPixelsOnly = False)

        self.assertTrue(isinstance(data, IEventWorkspace))
        self.assertEquals(1740, data.getNumberEvents())

    def test_extra_properties_passed_to_loader_for_multiple_files(self):
        data = Load("EQSANS_1466_event.nxs,EQSANS_3293_event.nxs", OutputWorkspace = self.wsname,
                    BankName = "bank1", SingleBankPixelsOnly = False)

        self.assertTrue(isinstance(data, WorkspaceGroup))
        self.assertEquals(2, data.getNumberOfEntries())
        # Test number of events in each
        self.assertEquals(740, data[0].getNumberEvents())
        self.assertEquals(105666, data[1].getNumberEvents())


#====================================================================================
