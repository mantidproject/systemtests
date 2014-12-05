import stresstesting
from mantid.simpleapi import *
from mantid.api import Workspace

from DirectEnergyConversion import setup_reducer
import dgreduce
import CommonFunctions as common

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
      raise NotImplementedError("Implement get_reference_file to return "
                                "the name of the file to compare against.")

    @abstractmethod
    def get_result_workspace(self):
        """Returns the result workspace to be checked"""

    @abstractmethod
    def runTest(self):
      """Defines the workflow for the test"""
     # rename workspace to the name expected by unit test framework



    def validate(self):
      """Returns the name of the workspace & file to compare"""
      self.tolerance = 1e-6
      self.tolerance_is_reller=True
      self.disableChecking.append('SpectraMap')
      self.disableChecking.append('Instrument')
      self.disableChecking.append('Sample')
      result = self.get_result_workspace()
      reference = self.get_reference_file()
      return result, reference

    def _is_numeric(self, obj):
      """Returns true if the object is an int or float, false otherwise"""
      if type(obj) != float or type(obj) != int:
        return True
      else:
        return False
      
    def _is_workspace(self, obj):
      """ Returns True if the object is a workspace"""
      return isinstance(obj, Workspace)
    def __init__(self):
        stresstesting.MantidStressTest.__init__(self);
        # this is temporary parameter 
        self.scale_to_fix_abf=1;

#------------------------- MARI tests -------------------------------------------------

class MARIReductionFromFile(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)

    from ISIS_MariReduction import ReduceMARIFromFile

    self.red = ReduceMARIFromFile()
    self.red.def_advanced_properties();
    self.red.def_main_properties();
    # temporary fix to account for different monovan integral
    self.scale_to_fix_abf = 0.0245159026452/0.024519711695583177

  def runTest(self):
       outWS = self.red.main();
       outWS*=self.scale_to_fix_abf;



  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"   
  def get_reference_file(self):
    return "MARIReduction.nxs"
    
class MARIReductionFromWorkspace(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)

    from ISIS_MariReduction import ReduceMARIFromWorkspace

    self.red = ReduceMARIFromWorkspace()
    self.red.def_advanced_properties();
    self.red.def_main_properties();

    self.scale_to_fix_abf = 0.0245159026452/0.024519711695583177


  def runTest(self):
      """Defines the workflow for the test"""

      outWS=self.red.main();
      # temporary fix to account for different monovan integral
      outWS*=self.scale_to_fix_abf

    
  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"

  def get_reference_file(self):
    return "MARIReduction.nxs"

class MARIReductionMon2Norm(ISISDirectInelasticReduction):

  def __init__(self):
    ISISDirectInelasticReduction.__init__(self)

    from ISIS_MariReduction import ReduceMARIMon2Norm

    self.red = ReduceMARIMon2Norm()
    self.red.def_advanced_properties();
    self.red.def_main_properties();

  def runTest(self):
      """Defines the workflow for the test"""

      outWS=self.red.main();
      # temporary fix to account for different monovan integral
      outWS*=2.11507984881/2.11563628862


  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"

  def get_reference_file(self):
    return "MARIReductionMon2Norm.nxs"

class MARIReductionSum(ISISDirectInelasticReduction):

  def __init__(self):

    ISISDirectInelasticReduction.__init__(self)
    from ISIS_MariReduction import MARIReductionSum

    self.red = MARIReductionSum()
    self.red.def_advanced_properties();
    self.red.def_main_properties();

  def runTest(self):
      """Defines the workflow for the test
      It verifies operation on summing two files on demand. No absolute units
      """
      outWS=self.red.main();
    
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

    from ISIS_MAPS_DGSReduction import ReduceMAPS

    self.red = ReduceMAPS()
    self.red.def_advanced_properties();
    self.red.def_main_properties();

  def runTest(self):

      outWS=self.red.main();
      #New WBI value 0.027546078402873958
      #Old WBI Value 0.027209867107187088
      # fix old system test. 
      outWS*=0.027546078402873958/0.027209867107187088

      # rename workspace to the name expected by unit test framework
      wsName = common.create_resultname(self.red.iliad_prop.sample_run,self.red.iliad_prop.instr_name);
      RenameWorkspace(InputWorkspace=outWS,OutputWorkspace=wsName)
      self.ws_name = wsName;


  def get_reference_file(self):
    return "MAPSDgreduceReduction.nxs"
  def get_result_workspace(self):
        """Returns the result workspace to be checked"""
        return self.ws_name 


#------------------------- MERLIN tests -------------------------------------------------

class MERLINReduction(ISISDirectInelasticReduction):

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 16Gb"""
      return 16000

  def __init__(self):
    ''' Test relies on MERLIN_Parameters.xml file introduced in July 2014
    ''' 
    ISISDirectInelasticReduction.__init__(self)

    from ISIS_MERLINReduction import ReduceMERLIN

    self.red = ReduceMERLIN()
    self.red.def_advanced_properties();
    self.red.def_main_properties();

  def runTest(self):
       outWS = self.red.main();
    
  def get_reference_file(self):
    return "MERLINReduction.nxs"
  def get_result_workspace(self):
      """Returns the result workspace to be checked"""
      return "outWS"

  def validate(self):
      self.tolerance = 1e-6
      self.tolerance_is_reller=True
      self.disableChecking.append('SpectraMap')
      self.disableChecking.append('Instrument')
      result = self.get_result_workspace()
      reference = self.get_reference_file()
      return result, reference

#------------------------- LET tests -------------------------------------------------
#
def find_binning_range(energy,ebin):
    """ function finds the binning range used in multirep mode 
        for merlin ls=11.8,lm2=10. mult=2.8868 dt_DAE=1;
        for LET    ls=25,lm2=23.5 mult=4.1     dt_DAE=1.6;
        all these values have to be already present in IDF and should be taken from there

        # THIS FUNCTION SHOULD BE MADE GENERIG AND MOVED OUT OF HERE
    """

    InstrName =  config['default.instrument'][0:3];
    if InstrName.find('LET')>-1:
        ls  =25;
        lm2 =23.5;
        mult=4.1;
        dt_DAE = 1.6
    elif InstrName.find('MER')>-1:
        ls =11.8;
        lm2=10;
        mult=2.8868;
        dt_DAE = 1
    else:
       raise RuntimeError("Find_binning_range: unsupported/unknown instrument found")

    energy=float(energy)

    emin=(1.0-ebin[2])*energy   #minimum energy is with 80% energy loss
    lam=(81.81/energy)**0.5
    lam_max=(81.81/emin)**0.5
    tsam=252.82*lam*ls   #time at sample
    tmon2=252.82*lam*lm2 #time to monitor 6 on LET
    tmax=tsam+(252.82*lam_max*mult) #maximum time to measure inelastic signal to
    t_elastic=tsam+(252.82*lam*mult)   #maximum time of elastic signal
    tbin=[int(tmon2),dt_DAE,int(tmax)]				
    energybin=[float("{0: 6.4f}".format(elem*energy)) for elem in ebin]

    return (energybin,tbin,t_elastic);
#--------------------------------------------------------------------------------------------------------
def find_background(ws_name,bg_range):
    """ Function to find background from multirep event workspace
     dt_DAE = 1 for MERLIN and 1.6 for LET
     should be precalculated or taken from IDF

        # THIS FUNCTION SHOULD BE MADE GENERIC AND MOVED OUT OF HERE
    """
    InstrName =  config['default.instrument'][0:3];
    if InstrName.find('LET')>-1:
        dt_DAE = 1.6
    elif InstrName.find('MER')>-1:
        dt_DAE = 1
    else:
       raise RuntimeError("Find_binning_range: unsupported/unknown instrument found")

    bg_ws_name = 'bg';
    delta=bg_range[1]-bg_range[0]
    Rebin(InputWorkspace='w1',OutputWorkspace=bg_ws_name,Params=[bg_range[0],delta,bg_range[1]],PreserveEvents=False)	
    v=(delta)/dt_DAE
    CreateSingleValuedWorkspace(OutputWorkspace='d',DataValue=v)
    Divide(LHSWorkspace=bg_ws_name,RHSWorkspace='d',OutputWorkspace=bg_ws_name)
    return bg_ws_name;


class LETReduction(stresstesting.MantidStressTest):

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 2Gb"""
      return 2000

  def runTest(self):
      """
      Run the LET reduction with event NeXus files
      
      Relies on LET_Parameters.xml file from June 2013
      """

      dgreduce.setup('LET',True)
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

      (energybin,tbin,t_elastic) = find_binning_range(ei,ebin);

      Rebin(InputWorkspace=sample_ws,OutputWorkspace=sample_ws, Params=tbin, PreserveEvents='1')
      #energybin = [ebin[0]*energy,ebin[1]*energy,ebin[2]*energy]
      #energybin = [ '%.4f' % elem for elem in energybin ]  
      ebinstring = str(energybin[0])+','+str(energybin[1])+','+str(energybin[2])
      argi={}
      argi['det_cal_file']='det_corrected7.dat'
      argi['bleed'] = False
      argi['norm_method']='current'
      argi['detector_van_range']=[0.5,200]
      argi['bkgd_range']=[int(t_elastic),int(tbin[2])]
      argi['hard_mask_file']='LET_hard.msk'
      #TODO: this has to be loaded from the workspace and work without this settings
      argi['ei-mon1-spec']=40966

      reduced_ws = dgreduce.arb_units(white_ws, sample_ws, ei, ebinstring, map_file,**argi)
      pass

  def validate(self):
      self.tolerance = 1e-6
      self.tolerance_is_reller=True
      self.disableChecking.append('SpectraMap')
      self.disableChecking.append('Instrument')

      return "reduced_ws", "LETReduction.nxs"

class LETReductionEvent2014Multirep(stresstesting.MantidStressTest):
  """
  written in a hope that most of the stuff find here will eventually find its way into main reduction routines
  """

  def requiredMemoryMB(self):
      """Far too slow for managed workspaces. They're tested in other places. Requires 20Gb"""
      return 20000

  def runTest(self):
      """
      Run the LET reduction with event NeXus files
      
      Relies on LET_Parameters.xml file from June 2013
      """

      dgreduce.setup('LET',True)
      wb=5545 #11869   # enter whitebeam run number here
        
      run_no=[14305] 
      ei=[3.4,8.] # multiple energies provided in the data file
      ebin=[-4,0.002,0.8]    #binning of the energy for the spe file. The numbers are as a fraction of ei [from ,step, to ]
      mapping='rings_103.map'  # rings mapping file for powders, liquout=iliad("wb_wksp","w1reb",energy,ebinstring,mapping,bleed=False,norm_method='current',det_cal_file='det_corrected7.dat',detector_van_range=[0.5,200],bkgd_range=[int(t_elastic),int(tmax)])
      mask_file = 'LET_hard.msk'
      # currently done here on-
      remove_background = True  #if true then will subtract a flat background in time from the time range given below otherwise put False
      bg_range=[92000,98000] # range of times to take background in



    # loads the whitebeam (or rather the long monovan ). Does it as a raw file to save time as the event mode is very large
      if 'wb_wksp' in mtd:
            wb_wksp=mtd['wb_wksp']
      else:  #only load whitebeam if not already there
          LoadRaw(Filename='LET0000'+str(wb)+'.raw',OutputWorkspace='wb_wksp')
        #dgreduce.getReducer().det_cal_file = 'det_corrected7.nxs'
        #wb_wksp = dgreduce.getReducer().load_data('LET0000'+str(wb)+'.raw','wb_wksp')
        #dgreduce.getReducer().det_cal_file = wb_wksp;

######################################################################

############################################
# Vanadium labelled Dec 2011 - flat plate of dimensions: 40.5x41x2.0# volume = 3404.025 mm**3 mass= 20.79
      sampleMass=20.79 # 17.25  # mass of your sample (PrAl3)
      sampleRMM= 50.9415 # 221.854  # molecular weight of your sample
      MonoVanRun=14319 # vanadium run in the same configuration as your sample
      monovan_mapfile='rings_103.map'  #

######################################################################

      MonoVanWB="wb_wksp"
      for run in run_no:     #loop around runs
          fname='LET0000'+str(run)+'.nxs'
          print ' processing file ', fname
          #w1 = dgreduce.getReducer().load_data(run,'w1')
          Load(Filename=fname,OutputWorkspace='w1',LoadMonitors='1');

    
          if remove_background:
                find_background('w1',bg_range);

        #############################################################################################
        # this section finds all the transmitted incident energies if you have not provided them
        #if len(ei) == 0:  -- not tested here -- should be unit test for that. 
           #ei = find_chopper_peaks('w1_monitors');       
          print 'Energies transmitted are:'
          print (ei)

          RenameWorkspace(InputWorkspace = 'w1',OutputWorkspace='w1_storage');
          RenameWorkspace(InputWorkspace = 'w1_monitors',OutputWorkspace='w1_mon_storage');
                    
         #now loop around all energies for the run
          result =[];
          mults =[41.032811389179471/41.178300987983413,71.28127860058153/72.231475173892022];
          for ind,energy in enumerate(ei):
                print float(energy)
                (energybin,tbin,t_elastic) = find_binning_range(energy,ebin);
                print " Rebinning will be performed in the range: ",energybin
                # if we calculate more then one energy, initial workspace will be used more then once
                if ind <len(ei)-1:
                    CloneWorkspace(InputWorkspace = 'w1_storage',OutputWorkspace='w1')
                    CloneWorkspace(InputWorkspace = 'w1_mon_storage',OutputWorkspace='w1_monitors')
                else:
                    RenameWorkspace(InputWorkspace = 'w1_storage',OutputWorkspace='w1');
                    RenameWorkspace(InputWorkspace = 'w1_mon_storage',OutputWorkspace='w1_monitors');

                if remove_background:
                    w1=Rebin(InputWorkspace='w1',OutputWorkspace='w1',Params=tbin,PreserveEvents=False)            
                    Minus(LHSWorkspace='w1',RHSWorkspace='bg',OutputWorkspace='w1')
               

                ######################################################################
                argi={};
                argi['norm_method']='current'
                argi['det_cal_file']='det_corrected7.nxs'
                argi['detector_van_range']=[2,7]
                argi['bkgd_range']=[bg_range[0],bg_range[1]]
                argi['hardmaskOnly']=mask_file   # diag does not work well on LET. At present only use a hard mask RIB has created
                argi['check_background']=False;

                # abs units
                argi['sample_mass']=sampleMass;
                argi['sample_rmm'] =sampleRMM;
                argi['monovan_mapfile']=monovan_mapfile;
                # ensure correct round-off procedure
                argi['monovan_integr_range']=[round(ebin[0]*energy,4),round(ebin[2]*energy,4)]; # integration range of the vanadium 
                #MonoVanWSName = None;
                #TODO: The same issue again. ei-monitor spectra is taken from recent IDF and old files have it wrong! 
                argi['ei-mon1-spec']=40966


                # absolute unit reduction -- if you provided MonoVan run or relative units if monoVan is not present
                out=dgreduce.arb_units("wb_wksp","w1",energy,energybin,mapping,MonoVanRun,**argi)
                #New normalization for 3.4 meV: 41.032811389179471
                #Old normalization for 3.4 meV: 41.178300987983413
                #New normalization for 8 meV: 71.28127860058153
                #Old normalization for 8 meV: 72.231475173892022
                out *=mults[ind];
                ws_name = 'LETreducedEi{0:2.1f}'.format(energy);
                RenameWorkspace(InputWorkspace=out,OutputWorkspace=ws_name);
    
                #SaveNXSPE(InputWorkspace=ws_name,Filename=ws_name+'.nxspe');



  def validate(self):
      self.tolerance = 1e-6
      self.tolerance_is_reller=False
      self.disableChecking.append('SpectraMap')
      self.disableChecking.append('Instrument')

      return "LETreducedEi3.4","LET14305_3_4mev.nxs","LETreducedEi8.0", "LET14305_8_0mev.nxs"

