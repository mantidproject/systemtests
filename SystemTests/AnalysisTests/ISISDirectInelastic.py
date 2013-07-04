import stresstesting
from mantid.simpleapi import *
from mantid.api import Workspace

from DirectEnergyConversion import setup_reducer
import dgreduce 

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
      #reducer = setup_reducer(self.instr_name)
      # The tests rely on MARI_Parameters.xml file valind on 31 July 2013
      dgreduce.setup(self.instr_name) 

      args={};
      args['sample_mass'] = self.sample_mass;
      args['sample_rmm']  = self.sample_rmm;
      # Disable auto save
      args['save_format'] = []
      args['hard_mask_file'] = self.hard_mask
      args['monovan_mapfile'] = self.map_file
      args['det_cal_file']=self.white_beam #"11060"


      #prepare the worksapce name expected by the framework
      if isinstance(self.sample_run, Workspace ):
        # reduction from workspace currently needs detector_calibration file
        # HACK! but MARI calibration file does not work/does  not exist. Use vanadium run for calibration
        args['det_cal_file']="11060"


      monovan_run=self.mono_van
      # Do the reduction -- when monovan run is not None, it does absolute units 
      outWS=dgreduce.arb_units(self.white_beam,self.sample_run,self.incident_energy,self.bins,self.map_file,monovan_run,**args)

      #SaveNexus(outWS,'MAR_reduction2.nxs')
      #SaveNXSPE(outWS,'MAR_reduction2.nxspe')
 

     # rename workspace to the name expected by unit test framework



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
      return isinstance(obj, Workspace)

#------------------------- MARI tests -------------------------------------------------

class MARIReductionFromFile(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)
    self.instr_name = 'MARI'
    self.sample_run = 11001 #11001
    self.incident_energy = 12
    self.bins = [-11,0.05,11]
    self.white_beam = 11060
    self.map_file = "mari_res.map"
    self.mono_van = 11015
    self.sample_mass = 10 #32.58 # 10
    self.sample_rmm =  435.96# 50.9415 # 435.96
    self.hard_mask = "mar11015.msk"

  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"   
  def get_reference_file(self):
    return "MARIReduction.nxs"
    
class MARIReductionFromWorkspace(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)

    mono_run = Load(Filename='MAR11001.RAW',OutputWorkspace='MAR11001.RAW')
    last_alg = mono_run.getHistory().lastAlgorithm()
    print last_alg
    mono_ws = mono_run
    AddSampleLog(Workspace=mono_ws, LogName='Filename', 
                 LogText=last_alg.getPropertyValue('Filename'))

    white_ws = Load(Filename='MAR11060.RAW',OutputWorkspace='MAR11060.RAW')

    van_run = Load(Filename='MAR11015.RAW',OutputWorkspace='MAR11015.RAW')
    last_alg = van_run.getHistory().lastAlgorithm()
    van_ws = van_run
    AddSampleLog(Workspace=van_ws, LogName='Filename', 
                 LogText=last_alg.getPropertyValue('Filename'))

    self.instr_name = 'MARI'
    self.sample_run = mono_ws
    self.incident_energy = 12
    self.bins = [-11,0.05,11]
    self.white_beam = white_ws
    #self.white_beam = 
    self.map_file = "mari_res.map"
    self.mono_van = van_ws
    self.sample_mass = 10
    self.sample_rmm = 435.96
    self.hard_mask = "mar11015.msk"

    
  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"

  def get_reference_file(self):
    return "MARIReduction.nxs"

class MARIReductionSum(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)

    ISISDirectInelasticReduction.__init__(self)
    self.instr_name = 'MARI'
    self.sample_run = 11001 #11001
    self.incident_energy = 11
    self.bins = [-11,0.05,11]
    self.white_beam = 11060
    self.map_file = "mari_res.map"
    self.mono_van = 11015
    self.sample_mass = 32.58 # 10
    self.sample_rmm =  50.9415 # 435.96
    self.hard_mask = "mar11015.msk"

  def runTest(self):
      """Defines the workflow for the test
      It verifies operation on summing two files on demand. No absolute units
      """

      self._validate_properties()
      # The tests rely on MARI_Parameters.xml file valind on 31 July 2013
      dgreduce.setup(self.instr_name) 

      args={};
      # Disable auto save
      args['save_format'] = []
      args['hard_mask_file'] = self.hard_mask
      args['sum_runs']    = True


      run_nums=[self.sample_run,self.mono_van]

      # Do the reduction
      outWS=dgreduce.arb_units(self.white_beam,run_nums,self.incident_energy,self.bins,self.map_file,**args)
      #SaveNexus(outWS,'MAR_reduction2.nxs')
      #SaveNXSPE(outWS,'MAR_reduction2.nxspe')
    
  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"

  def get_reference_file(self):
    return "MARIReductionSum.nxs"

#------------------------- MAPS tests -------------------------------------------------



class MAPSDgreduceReduction(ISISDirectInelasticReduction):

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 10Gb"""
      return 10000

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)



  def runTest(self):
      # The tests rely on MAPS_Parameters.xml file valind on 31 July 2013
      # All other reducer parameters are defaults taken this file
      dgreduce.setup('MAP')   
      argi = dict();
      argi['save_format'] = None; # disable saving
      argi['abs_units_van_range']=[-40,40]

      #argi['hardmaskPlus']=maskfile 
      #argi['hardmaskOnly']=maskfile 
      argi['hard_mask_file']=None
      argi['diag_remove_zero']=False
      argi['sample_mass'] = 10/(94.4/13) # -- this number allows to get approximately the same system test intensities for MAPS as the old test
      argi['sample_rmm']  = 435.96 #
      # The mass and rmm for Vanadium to get correct cross-section
      #argi['sample_mass'] =  30.1
      #argi['sample_rmm']  =  50.9415

      # this are the parameterw which were used in old MAPS_Parameters.xml test. 
      argi['wb-integr-max'] =300
      argi['bkgd-range-min']=12000
      argi['bkgd-range-max']=18000
      argi['diag_samp_hi']=1.5
      argi['diag_samp_sig']=3.3
      argi['diag_van_hi']=2.0



      # This file is the essential part of this test

      # this is for testing only as the test talks to these parameters
      self.sample_run = 17269
      #self.sample_run = 17589 # mono-run to estimate known Vanadium x-section

      # the test to get WB cross-section
      #outWS =dgreduce.arb_units(17186,self.sample_run,150,[-50,1,100],'default',17589,**argi)
      outWS = dgreduce.arb_units(17186,self.sample_run,150,[-15,3,135],'default',17589,**argi)
    # set up the reducer parameters which come from dgreduce arguments

      # rename workspace to the name expected by unit test framework
      RenameWorkspace(InputWorkspace=outWS,OutputWorkspace=str(self.sample_run)+'.spe')


  def get_reference_file(self):
    return "MAPSDgreduceReduction.nxs"

#------------------------- MERLIN tests -------------------------------------------------

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

#------------------------- LET tests -------------------------------------------------

class LETReduction(stresstesting.MantidStressTest):

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 2Gb"""
      return 2000

  def runTest(self):
      """
      Run the LET reduction with event NeXus files
      """
      import dgreduce
      dgreduce.setup('LET')
      white_run = 'LET00005545.raw'
      sample_run = 'LET00006278.nxs'
      ei = 7.0
      ebin = [-1,0.002,0.95]
      map_file = 'rings_103'
      
      white_ws = 'wb_wksp'
      LoadRaw(Filename=white_run,OutputWorkspace=white_ws)
      sample_ws = 'w1'
      monitors_ws = sample_ws + '_monitors'
      LoadEventNexus(Filename=sample_run,OutputWorkspace=sample_ws,
                     SingleBankPixelsOnly='0',LoadMonitors='1',
                     MonitorsAsEvents='1')
      ConjoinWorkspaces(InputWorkspace1=sample_ws, InputWorkspace2=monitors_ws)

      energy = ei
      emin = 0.2*energy   #minimum energy is with 80% energy loss
      lam = (81.81/energy)**0.5
      lam_max = (81.81/emin)**0.5
      tsam = 252.82*lam*25   #time at sample
      tmon2 = 252.82*lam*23.5 #time to monitor 6 on LET
      tmax = tsam+(252.82*lam_max*4.1) #maximum time to measure inelastic signal to
      t_elastic = tsam+(252.82*lam*4.1)   #maximum time of elastic signal
      tbin = [int(tmon2),1.6,int(tmax)]
      Rebin(InputWorkspace=sample_ws,OutputWorkspace=sample_ws, Params=tbin, PreserveEvents='1')
      energybin = [ebin[0]*energy,ebin[1]*energy,ebin[2]*energy]
      energybin = [ '%.4f' % elem for elem in energybin ]  
      ebinstring = str(energybin[0])+','+str(energybin[1])+','+str(energybin[2])

      reduced_ws = dgreduce.arb_units(white_ws, sample_ws, energy, ebinstring, map_file, det_cal_file='det_corrected7.dat',
                                      bleed=False, norm_method='current', 
                                      detector_van_range=[0.5,200],bkgd_range=[int(t_elastic),int(tmax)])

  def validate(self):
      self.disableChecking.append('Instrument') # Disable parameter map checking
      return "reduced_ws", "LETReduction.nxs"

