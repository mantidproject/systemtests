import stresstesting

from mantid.api import MatrixWorkspace, mtd
from mantid.simpleapi import LoadVesuvio

import unittest

class VesuvioTests(unittest.TestCase):
    
    ws_name = "evs_raw"

    def tearDown(self):
        if self.ws_name in mtd:
            mtd.remove(self.ws_name)

    #================== Success cases ================================
    def test_load_with_back_scattering_spectra_produces_correct_Workspace(self):
        self._run_load("14188", "3-134", "Double")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(1088575.7438282669, evs_raw.readY(0)[1], delta=1e-12)
        self.assertAlmostEqual(450536.04689897969, evs_raw.readY(131)[1188], delta=1e-12)

    def test_consecutive_runs_with_back_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188-14190", "3-134", "Double")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(14518389.539437652, evs_raw.readY(0)[1], delta=1e-12)
        self.assertAlmostEqual(3777267.858574003, evs_raw.readY(131)[1188], delta=1e-12)

    def test_non_consecutive_runs_with_back_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188,14190", "3-134", "Double")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(8312081.5967741609, evs_raw.readY(0)[1], delta=1e-12)
        self.assertAlmostEqual(-561548.15057308972, evs_raw.readY(131)[1188], delta=1e-12)

    def test_load_with_forward_scattering_spectra_produces_correct_Workspace(self):
        self._run_load("14188", "135-198", "Single")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(10175012.618748903, evs_raw.readY(0)[1], delta=1e-12)
        self.assertAlmostEqual(278560.72293964587, evs_raw.readY(63)[1188], delta=1e-12)

    def test_consecutive_runs_with_forward_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188-14190", "135-198", "Single")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(71968266.925433159, evs_raw.readY(0)[1], delta=1e-12)
        self.assertAlmostEqual(664080.94680766761, evs_raw.readY(63)[1188], delta=1e-12)

    def test_non_consecutive_runs_with_forward_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188,14190", "135-198", "Single")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(33382423.256690979, evs_raw.readY(0)[1], delta=1e-12)
        self.assertAlmostEqual(89769.348181426525, evs_raw.readY(63)[1188], delta=1e-12)

    def _run_load(self, runs, spectra, diff_opt):
        LoadVesuvio(RunNumbers=runs,OutputWorkspace=self.ws_name,
            SpectrumList=spectra,DifferenceType=diff_opt)

        self._do_ads_check(self.ws_name)
        if spectra == "3-134":
            self._do_size_check(self.ws_name, 132)
        elif spectra == "135-198":
            self._do_size_check(self.ws_name, 64)
        else:
            raise ValueError("Unknown spectra set given %s" % str(spectra))

    def _do_ads_check(self, name):
        self.assertTrue(name in mtd)
        self.assertTrue(type(mtd[name]) == MatrixWorkspace)

    def _do_size_check(self,name, expected_nhist):
        loaded_data = mtd[name]
        self.assertEquals(expected_nhist, loaded_data.getNumberHistograms())
        
    #================== Failure cases ================================

    def test_missing_spectra_property_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                          OutputWorkspace=self.ws_name)
        
    def test_load_with_invalid_spectra_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                          OutputWorkspace=self.ws_name, SpectrumList="200")

    def test_load_with_spectra_mixed_from_forward_backward_raises_error(self):
        # Everything
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                  OutputWorkspace=self.ws_name, SpectrumList="3-198")
        # Smaller range
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                  OutputWorkspace=self.ws_name, SpectrumList="125-180")
        
        # Just two
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                  OutputWorkspace=self.ws_name, SpectrumList="134,135")
        
    def test_load_with_spectra_that_are_just_monitors_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
          OutputWorkspace=self.ws_name, SpectrumList="1")
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                          OutputWorkspace=self.ws_name, SpectrumList="1-2")
        
    def test_load_with_invalid_difference_option_raises_error(self):
        self.assertRaises(ValueError, LoadVesuvio, RunNumbers="14188",
          OutputWorkspace=self.ws_name, DifferenceType="Unknown",SpectrumList="3-134")

    def test_load_with_difference_option_not_applicable_to_current_spectra_raises_error(self):
        self.assertRaises(ValueError, LoadVesuvio, RunNumbers="14188",
          OutputWorkspace=self.ws_name, DifferenceType="",SpectrumList="3-134")
    

#====================================================================================

class LoadVesuvioTest(stresstesting.MantidStressTest):

    def runTest(self):
        self._success = False
        # Custom code to create and run this single test suite
        suite = unittest.TestSuite()
        suite.addTest( unittest.makeSuite(VesuvioTests, "test") )
        runner = unittest.TextTestRunner()
        # Run using either runner
        res = runner.run(suite)
        if res.wasSuccessful():
            self._success = True 
        else:
            self._success = False

    def validate(self):
        return self._success
