import stresstesting

from mantid.api import MatrixWorkspace, mtd
from mantid.simpleapi import LoadILL

import unittest

DIFF_PLACES = 12

class ILLIN5Tests(unittest.TestCase):
    
    ws_name = "in5_ws"
    dataDispersionFile = "ILL/ILLIN5_Sample_096003.nxs"
    vanadiumFile = "ILL/ILLIN5_Vana_095893.nxs"


    def tearDown(self):
        if self.ws_name in mtd:
            mtd.remove(self.ws_name)

    #================== Success cases ================================
    def test_load_single_file(self):
        self._run_load(self.dataDispersionFile)
        
        # Check some data
        wsOut = mtd[self.ws_name]
        self.assertEqual(wsOut.getNumberHistograms(), 98305)
    
    def test_load_dispersion_file_and_vanadium(self):
        self._run_load(self.dataDispersionFile,self.vanadiumFile)
        
        # Check some data
        wsOut = mtd[self.ws_name]
        self.assertEqual(wsOut.getNumberHistograms(), 98305)
            
    #================== Failure cases ================================

    # TODO

    
    def _run_load(self, dataFile, vanaFile=""):
        """
        ILL Loader
        """
        LoadILL(Filename=dataFile,FilenameVanadium=vanaFile,OutputWorkspace=self.ws_name)
        self._do_ads_check(self.ws_name)

    def _do_ads_check(self, name):
        self.assertTrue(name in mtd)
        self.assertTrue(type(mtd[name]) == MatrixWorkspace)

#====================================================================================

class LoadILLIN5Test(stresstesting.MantidStressTest):

    def runTest(self):
        self._success = False
        # Custom code to create and run this single test suite
        suite = unittest.TestSuite()
        suite.addTest( unittest.makeSuite(ILLIN5Tests, "test") )
        runner = unittest.TextTestRunner()
        # Run using either runner
        res = runner.run(suite)
        if res.wasSuccessful():
            self._success = True 
        else:
            self._success = False

    def validate(self):
        return self._success
