import stresstesting

from mantid.api import MatrixWorkspace, mtd
from mantid.simpleapi import LoadVesuvio

import unittest

DIFF_PLACES = 12

class VesuvioTests(unittest.TestCase):
    
    ws_name = "evs_raw"


    def tearDown(self):
        if self.ws_name in mtd:
            mtd.remove(self.ws_name)

    #================== Success cases ================================
    def test_load_with_back_scattering_spectra_produces_correct_workspace(self):
        self._run_load("14188", "3-134", "DoubleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(0.10578008404756822, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.012473899398724836, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.019430710038363164, evs_raw.readY(131)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0089329377485360718, evs_raw.readE(131)[1188], places=DIFF_PLACES)

    def test_consecutive_runs_with_back_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188-14190", "3-134", "DoubleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(0.16459533916997771, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0054835169773849151, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.04106419502927916, evs_raw.readY(131)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0039458033851850569, evs_raw.readE(131)[1188], places=DIFF_PLACES)

    def test_non_consecutive_runs_with_back_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188,14190", "3-134", "DoubleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(0.2228557076076223, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0074247283506022844, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(-0.02965284101745258, evs_raw.readY(131)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.005338637434321317, evs_raw.readE(131)[1188], places=DIFF_PLACES)

    def test_load_with_forward_scattering_spectra_produces_correct_workspace(self):
        self._run_load("14188", "135-198", "SingleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(-0.98848024168979975, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.020413830523102618, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(-0.030630421989159107, evs_raw.readY(63)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.020413830523102618, evs_raw.readE(0)[1], places=DIFF_PLACES)

    def test_consecutive_runs_with_forward_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188-14190", "135-198", "SingleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(-0.79635325645330823, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0090021341424403132, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(-0.00058496015876685625, evs_raw.readY(63)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0036140732253384837, evs_raw.readE(63)[1188], places=DIFF_PLACES)

    def test_non_consecutive_runs_with_forward_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188,14190", "135-198", "SingleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(-0.81024153418200484, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.012181357261799183, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0013864599556558943, evs_raw.readY(63)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.012181357261799183, evs_raw.readE(0)[1], places=DIFF_PLACES)

    def test_load_with_spectra_mixed_from_forward_backward_gives_expected_numbers(self):
        self._run_load("14188", "134,135", "DoubleDifference")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(1.0911906622104048, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.01712867623423316, evs_raw.readE(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(0.013801041649942475, evs_raw.readY(1)[1188], places=DIFF_PLACES)
        self.assertAlmostEqual(0.0069224310040054467, evs_raw.readE(1)[1188], places=DIFF_PLACES)

    def test_foilout_mode_gives_expected_numbers(self):
        self._run_load("14188", "3", "FoilOut")

        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(18753.00, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(136.94159338929865, evs_raw.readE(0)[1], places=DIFF_PLACES)

    def test_foilin_mode_gives_expected_numbers(self):
        self._run_load("14188", "3", "FoilIn")

        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(37594.0, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(193.89172236070317, evs_raw.readE(0)[1], places=DIFF_PLACES)
        
    def test_using_ip_file_adjusts_instrument_and_attaches_parameters(self):
        self._run_load("14188", "3", "SingleDifference","IP0005.dat")
        
        # Check some data
        evs_raw = mtd[self.ws_name]
        det0 = evs_raw.getDetector(0)
        param = det0.getNumberParameter("t0")
        self.assertEqual(1, len(param))
        self.assertAlmostEqual(-0.4157, param[0],places=4)

    def _run_load(self, runs, spectra, diff_opt, ip_file=""):
        LoadVesuvio(Filename=runs,OutputWorkspace=self.ws_name,
            SpectrumList=spectra,Mode=diff_opt,InstrumentParFile=ip_file)

        self._do_ads_check(self.ws_name)

        def expected_size(str_param):
            if "-" in str_param:
                elements = str_param.split("-")
                min,max=(int(elements[0]), int(elements[1]))
                return max - min + 1
            elif "," in str_param:
                elements = str_param.strip().split(",")
                return len(elements)
            else:
                return 1

        self._do_size_check(self.ws_name, expected_size(spectra))

    def _do_ads_check(self, name):
        self.assertTrue(name in mtd)
        self.assertTrue(type(mtd[name]) == MatrixWorkspace)

    def _do_size_check(self,name, expected_nhist):
        loaded_data = mtd[name]
        self.assertEquals(expected_nhist, loaded_data.getNumberHistograms())
        
    #================== Failure cases ================================

    def test_missing_spectra_property_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, Filename="14188",
                          OutputWorkspace=self.ws_name)
        
    def test_load_with_invalid_spectra_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, Filename="14188",
                          OutputWorkspace=self.ws_name, SpectrumList="200")
        
    def test_load_with_spectra_that_are_just_monitors_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, Filename="14188",
          OutputWorkspace=self.ws_name, SpectrumList="1")
        self.assertRaises(RuntimeError, LoadVesuvio, Filename="14188",
                          OutputWorkspace=self.ws_name, SpectrumList="1-2")
        
    def test_load_with_invalid_difference_option_raises_error(self):
        self.assertRaises(ValueError, LoadVesuvio, Filename="14188",
          OutputWorkspace=self.ws_name, Mode="Unknown",SpectrumList="3-134")

    def test_load_with_difference_option_not_applicable_to_current_spectra_raises_error(self):
        self.assertRaises(ValueError, LoadVesuvio, Filename="14188",
          OutputWorkspace=self.ws_name, Mode="",SpectrumList="3-134")

    def test_raising_error_removes_temporary_raw_workspaces(self):
        self.assertRaises(RuntimeError, LoadVesuvio, Filename="14188,14199", # Second run is invalid
          OutputWorkspace=self.ws_name, Mode="SingleDifference",SpectrumList="3-134")

        self._do_test_temp_raw_workspaces_not_left_around()

    def _do_test_temp_raw_workspaces_not_left_around(self):
        self.assertTrue("__loadraw_evs" not in mtd) 
        self.assertTrue("__loadraw_evs_monitors" not in mtd)


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
