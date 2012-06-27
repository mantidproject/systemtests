import stresstesting
from mantidsimple import Load, AddSampleLog, WorkspaceProxy

from DirectEnergyConversion import setup_reducer

from abc import ABCMeta, abstractmethod

#----------------------------------------------------------------------
class ISISDirectInelasticReduction(stresstesting.MantidStressTest):
    """A base class for the ISIS direct inelastic tests
    
    The workflow is defined in the runTest() method, simply
    define an __init__ method and set the following properties
    on the object
        - instr_name: A string giving the instrument name for the test
        - sample_run: An integer run number of the sample or a a workspace
        - incident_energy: A float value for the Ei guess
        - bins: A list of rebin parameters
        - white_beam: An integer giving a white_beam_file or a workspace
        - mono_van: An integer giving a mono-vanadium run or a workspace or None
        - map_file: An optional string pointing to a map file 
        - sample_mass: A float value for the sample mass or None
        - sample_rmm: A float value for the sample rmm or None
        - hard_mask: An hard mask file or None
    """
    __metaclass__ = ABCMeta # Mark as an abstract class

    @abstractmethod
    def get_reference_file(self):
      """Returns the name of the reference file to compare against"""
      raise NotImplementedError("Implmenent get_reference_file to return "
                                "the name of the file to compare against.")

    def get_result_workspace(self):
        """Returns the result workspace to be checked"""
        return str(self.sample_run) + ".spe"
  
    def runTest(self):
      """Defines the workflow for the test"""

      self._validate_properties()

      reducer = setup_reducer(self.instr_name)
      ei = self.incident_energy
      reducer.energy_bins = self.bins
      # Disable auto save
      reducer.save_formats = []
      reducer.map_file = self.map_file
      reducer.abs_map_file = reducer.map_file
      if self.sample_mass is not None:
        reducer.sample_mass = self.sample_mass
      if self.sample_rmm is not None:
        reducer.sample_rmm = self.sample_rmm
      hard_mask = self.hard_mask

      # Do the reduction
      reducer.diagnose(self.white_beam, sample=self.sample_run, hard_mask=self.hard_mask)
      reducer.convert_to_energy(mono_run=self.sample_run, ei=self.incident_energy, 
                                white_run=self.white_beam,mono_van=self.mono_van, 
                                abs_white_run=self.white_beam)

    def validate(self):
      """Returns the name of the workspace & file to compare"""
      self.tolerance = 1e-7
      self.disableChecking.append('SpectraMap')
      self.disableChecking.append('Instrument')
      result = self.get_result_workspace()
      reference = self.get_reference_file()
      return result, reference

    def _validate_properties(self):
      """Check the object properties are
      in an expected state to continue
      """
      if type(self.instr_name) != str:
        raise RuntimeError("instr_name property should be a string")
      if type(self.sample_run) != int and not self._is_workspace(self.sample_run):
        raise RuntimeError("sample_run property should be an integer or a workspace.")
      if not self._is_numeric(self.incident_energy):
        raise RuntimeError("incident_energy property should be a numerical quantity")
      if type(self.bins) != list and len(self.bins) < 3:
        raise RuntimeError("bins property should be a list of atleast 3 values")
      if type(self.white_beam) != int and not self._is_workspace(self.white_beam):
        raise RuntimeError("white_beam property should be an integer or a workspace")
      if self.mono_van is not None and type(self.mono_van) != int and \
              not self._is_workspace(self.mono_van) :
        raise RuntimeError("mono_van property should be an integer or a workspace")
      if self.map_file is not None and type(self.map_file) != str:
        raise RuntimeError("map_file property should be a string")
      if self.sample_mass is not None and not self._is_numeric(self.sample_mass):
        raise RuntimeError("sample_mass property should be a numerical quantity")
      if self.sample_rmm is not None and not self._is_numeric(self.sample_rmm):
        raise RuntimeError("sample_rmm property should be a numerical quantity")
      if self.hard_mask is not None and type(self.hard_mask) != str:
        raise RuntimeError("hard_mask property should be a string")
      
    def _is_numeric(self, obj):
      """Returns true if the object is an int or float, false otherwise"""
      if type(obj) != float or type(obj) != int:
        return True
      else:
        return False
      
    def _is_workspace(self, obj):
      """ Returns True if the object is a workspace"""
      return type(obj) == WorkspaceProxy

#------------------------- MARI tests -------------------------------------------------

class MARIReductionFromFile(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)
    self.instr_name = 'MARI'
    self.sample_run = 11015
    self.incident_energy = 11
    self.bins = [-11,0.05,11]
    self.white_beam = 11060
    self.map_file = "mari_res.map"
    self.mono_van = 11001
    self.sample_mass = 10
    self.sample_rmm = 435.96
    self.hard_mask = "mar11015.msk"
    
  def get_reference_file(self):
    return "MARIReduction.nxs"
    
class MARIReductionFromWorkspace(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)

    mono_run = Load(Filename='MAR11015.RAW',OutputWorkspace='MAR11015.RAW')
    mono_ws = mono_run.workspace()
    AddSampleLog(Workspace=mono_ws, LogName='Filename', 
                 LogText=mono_run['Filename'].value)

    white_ws = Load(Filename='MAR11060.RAW',OutputWorkspace='MAR11060.RAW').workspace()

    van_run = Load(Filename='MAR11001.RAW',OutputWorkspace='MAR11001.RAW')
    van_ws = van_run.workspace()
    AddSampleLog(Workspace=van_ws, LogName='Filename', 
                 LogText=van_run['Filename'].value)

    self.instr_name = 'MARI'
    self.sample_run = mono_ws
    self.incident_energy = 11
    self.bins = [-11,0.05,11]
    self.white_beam = 11060
    self.map_file = "mari_res.map"
    self.mono_van = van_ws
    self.sample_mass = 10
    self.sample_rmm = 435.96
    self.hard_mask = "mar11015.msk"
    
  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "11015.spe"

  def get_reference_file(self):
    return "MARIReduction.nxs"

#------------------------- MAPS tests -------------------------------------------------

class MAPSReduction(ISISDirectInelasticReduction):

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 10Gb"""
      return 10000

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)
    self.instr_name = 'MAPS'
    self.sample_run = 17269
    self.incident_energy = 150
    self.bins = [-15,3,135]
    self.white_beam = 17186
    self.map_file = "4to1.map"
    self.mono_van = 17589
    # We care about deviations from expected so the absolute numbers are not vital
    # Using same as above
    self.sample_mass = 10
    self.sample_rmm = 435.96
    self.hard_mask = None
    
  def get_reference_file(self):
    return "MAPSReduction.nxs"

#------------------------- MAPS tests -------------------------------------------------

class MERLINReduction(ISISDirectInelasticReduction):

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 16Gb"""
      return 16000

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)
    self.instr_name = 'MERLIN'
    self.sample_run = 6398
    self.incident_energy = 18
    self.bins = [-10, 0.2, 15]
    self.white_beam = 6399
    self.map_file = "rings_113.map"
    self.mono_van = None
    self.sample_mass = None
    self.sample_rmm = None
    self.hard_mask = None
    
  def get_reference_file(self):
    return "MERLINReduction.nxs"
