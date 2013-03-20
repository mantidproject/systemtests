import stresstesting

#-------------------------------------------------------------------------------
class IRISDiffspecDiffractionTest(stresstesting.MantidStressTest):
  
  def runTest(self):
    """
    Runs the reduction
    """
    inst_name = "IRIS"
    param_file = "%s_diffraction_diffspec_Parameters.xml" % (inst_name)
    from IndirectDiffractionReduction import MSGDiffractionReducer
    reducer = MSGDiffractionReducer()
    reducer.set_instrument_name(inst_name)
    reducer.set_detector_range(104, 111) # Note these are one less than what you enter in the GUI
    reducer.set_parameter_file(param_file)
    reducer.append_data_file("IRS21360.raw")
    reducer.set_rebin_string("3.0,0.001,4.0")
    reducer.reduce()

  def validate(self):
    self.disableChecking.append('Instrument')
    return 'IRS21360', 'IRISDiffspecDiffractionTest.nxs'

#-------------------------------------------------------------------------------

class ToscaDiffractionTest(stresstesting.MantidStressTest):
  
  def runTest(self):
    """
    Runs the reduction
    """
    inst_name = "TOSCA"
    param_file = "%s_diffraction__Parameters.xml" % (inst_name)
    from IndirectDiffractionReduction import MSGDiffractionReducer
    reducer = MSGDiffractionReducer()
    reducer.set_instrument_name(inst_name)
    reducer.set_detector_range(145, 148) # Note these are one less than what you enter in the GUI
    reducer.set_parameter_file(param_file)
    reducer.append_data_file("TSC11453.raw")
    reducer.set_rebin_string("0.5,0.001,2.1")
    reducer.reduce()

  def validate(self):
    self.disableChecking.append('Instrument')
    return 'TSC11453', 'TOSCADiffractionTest.nxs'

#-------------------------------------------------------------------------------

class OsirisDiffractionTest(stresstesting.MantidStressTest):
    
  def runTest(self):
    from mantidsimple import OSIRISDiffractionReduction
    OSIRISDiffractionReduction(
	OutputWorkspace="OsirisDiffractionTest",
	Sample="OSI89813.raw, OSI89814.raw, OSI89815.raw, OSI89816.raw, OSI89817.raw",
	CalFile="osiris_041_RES10.cal",
	Vanadium="OSI89757, OSI89758, OSI89759, OSI89760, OSI89761")

  def validate(self):
    self.disableChecking.append('Instrument')
    return 'OsirisDiffractionTest', 'OsirisDiffractionTest.nxs'
