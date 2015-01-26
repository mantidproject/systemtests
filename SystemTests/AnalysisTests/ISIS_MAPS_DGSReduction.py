""" Sample MAPS reduction scrip """ 

from Direct.ReductionWrapper import *
try:
    import reduce_vars as rv
except:
    rv = None


class ReduceMAPS(ReductionWrapper):
   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 
       prop = {};
       prop['sample_run'] = 17269;
       prop['wb_run'] = 17186
       prop['incident_energy'] = 150;
       prop['energy_bins'] = [-15,3,135]

       
      # Absolute units reduction properties.
       prop['monovan_run'] = 17589
       prop['sample_mass'] = 10/(94.4/13) # -- this number allows to get approximately the same system test intensities for MAPS as the old test
       prop['sample_rmm'] = 435.96 #
       return prop

   @AdvancedProperties
   def def_advanced_properties(self):
      """  separation between simple and advanced properties depends
           on scientist, experiment and user.
           main properties override advanced properties.      
      """
      prop = {};
      prop['map_file'] = 'default'
      #prop['monovan_mapfile'] = 'default' #'4to1_mid_lowang.map' # default
      prop['hard_mask_file'] =None
      #prop['det_cal_file'] = ? default?
      prop['save_format']=''
      
      prop['diag_remove_zero']=False

      # this are the parameters which were used in old MAPS_Parameters.xml test. 
      prop['wb-integr-max'] =300
      #prop['wb_integr_range']=[20,300]
      prop['bkgd-range-min']=12000
      prop['bkgd-range-max']=18000
      #prop['bkgd_range']=[12000,18000]

      prop['diag_samp_hi']=1.5
      prop['diag_samp_sig']=3.3
      prop['diag_van_hi']=2.0
      
      prop['abs_units_van_range']=[-40,40]    
      
      return prop;
      #
   @iliad
   def main(self,input_file=None,output_directory=None):
     # run reduction, write auxiliary script to add something here.

       red = DirectEnergyConversion();
       red.initialise(self.iliad_prop);
       outWS = red.convert_to_energy();
       #SaveNexus(ws,Filename = 'MARNewReduction.nxs')

       #when run from web service, return additional path for web server to copy data to";
       return outWS

   def __init__(self):
       """ sets properties defaults for the instrument with Name"""
       ReductionWrapper.__init__(self,'MAP',rv)
#----------------------------------------------------------------------------------------------------------------------



if __name__=="__main__":
     maps_dir = 'd:/Data/MantidSystemTests/Data'
     data_dir ='d:/Data/Mantid_Testing/14_11_27'
     ref_data_dir = 'd:/Data/MantidSystemTests/SystemTests/AnalysisTests/ReferenceResults' 
     config.setDataSearchDirs('{0};{1};{2}'.format(data_dir,maps_dir,ref_data_dir))
     #config.appendDataSearchDir('d:/Data/Mantid_GIT/Test/AutoTestData')
     config['defaultsave.directory'] = data_dir # folder to save resulting spe/nxspe files. Defaults are in

     # execute stuff from Mantid
     rd = ReduceMAPS();
     rd.def_advanced_properties();
     rd.def_main_properties();


     using_web_data = False;
     if not using_web_data:
        run_dir=os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(run_dir,'reduce_vars.py');
        rd.export_changed_values(file);

     rd.main(); 
