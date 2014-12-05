""" Sample LET reduction scrip """ 

from ReductionWrapper import *
try:
    import reduce_vars as rv
except:
    rv = None

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


class ReduceLET_OneRep(ReductionWrapper):
   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 


       prop = {};
       ei = 7.0
       ebin = [-1,0.002,0.95]
 
       prop['sample_run'] = 'LET00006278.nxs'
       prop['wb_run'] = 'LET00005545.raw'
       prop['incident_energy'] = ei;
       prop['energy_bins'] = ebin

       
      # Absolute units reduction properties.
       #prop['monovan_run'] = 17589
       #prop['sample_mass'] = 10/(94.4/13) # -- this number allows to get approximately the same system test intensities for MAPS as the old test
       #prop['sample_rmm'] = 435.96 #
       return prop

   @AdvancedProperties
   def def_advanced_properties(self):
      """  separation between simple and advanced properties depends
           on scientist, experiment and user.
           main properties override advanced properties.      
      """

      prop = {};
      prop['map_file'] = 'rings_103'
      prop['hard_mask_file'] ='LET_hard.msk'
      prop['det_cal_file'] = 'det_corrected7.dat'
      prop['save_format']=''
      prop['bleed'] = False
      prop['norm_method']='current'
      prop['detector_van_range']=[0.5,200]
      #TODO: this has to be loaded from the workspace and work without this 
      prop['ei-mon1-spec']=40966
     
      
      return prop;
      #
   @iliad
   def main(self,input_file=None,output_directory=None):
     # run reduction, write auxiliary script to add something here.

      prop = self.iliad_prop;
      # 
      sample_run    = prop.sample_run
      white_run     = prop.wb_run
      white_ws = 'wb_wksp'
      LoadRaw(Filename=white_run,OutputWorkspace=white_ws)
      #prop.wb_run = mtd[white_ws]

      sample_ws = 'w1'
      monitors_ws = sample_ws + '_monitors'
      LoadEventNexus(Filename=sample_run,OutputWorkspace=sample_ws,
                     SingleBankPixelsOnly='0',LoadMonitors='1',
                     MonitorsAsEvents='1')
      ConjoinWorkspaces(InputWorkspace1=sample_ws, InputWorkspace2=monitors_ws)


      ebin = prop.energy_bins
      ei   = prop.incident_energy;

      (energybin,tbin,t_elastic) = find_binning_range(ei,ebin);
      Rebin(InputWorkspace=sample_ws,OutputWorkspace=sample_ws, Params=tbin, PreserveEvents='1')

      prop.bkgd_range=[int(t_elastic),int(tbin[2])]

      ebinstring = str(energybin[0])+','+str(energybin[1])+','+str(energybin[2])
      self.iliad_prop.energy_bins = ebinstring;

      red = DirectEnergyConversion();

      red.initialise(prop);
      outWS = red.convert_to_energy_transfer(white_ws,sample_ws);
      #SaveNexus(ws,Filename = 'MARNewReduction.nxs')

      #when run from web service, return additional path for web server to copy data to";
      return outWS

   def __init__(self):
       """ sets properties defaults for the instrument with Name"""
       ReductionWrapper.__init__(self,'LET',rv)
#----------------------------------------------------------------------------------------------------------------------



if __name__=="__main__":
     maps_dir = 'd:/Data/MantidSystemTests/Data'
     data_dir ='d:/Data/Mantid_Testing/14_11_27'
     ref_data_dir = 'd:/Data/MantidSystemTests/SystemTests/AnalysisTests/ReferenceResults' 
     config.setDataSearchDirs('{0};{1};{2}'.format(data_dir,maps_dir,ref_data_dir))
     #config.appendDataSearchDir('d:/Data/Mantid_GIT/Test/AutoTestData')
     config['defaultsave.directory'] = data_dir # folder to save resulting spe/nxspe files. Defaults are in

     # execute stuff from Mantid
     rd = ReduceLET_OneRep();
     rd.def_advanced_properties();
     rd.def_main_properties();


     using_web_data = False;
     if not using_web_data:
        run_dir=os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(run_dir,'reduce_vars.py');
        rd.export_changed_values(file);

     rd.main(); 
