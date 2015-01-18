""" Sample MERLIN reduction scrip """ 
import os
os.environ["PATH"] = r"c:/Mantid/Code/builds/br_10803/bin/Release;"+os.environ["PATH"]

from Direct.ReductionWrapper import *
try:
    import reduce_vars as rv
except:
    rv = None


class ReduceMERLIN(ReductionWrapper):
   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 


       prop = {};
       prop['sample_run'] = 6398;
       prop['wb_run'] = 6399
       prop['incident_energy'] = 18;
       prop['energy_bins'] = [-10, 0.2, 15]

       
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
      prop['map_file'] = 'rings_113.map'
      #prop['monovan_mapfile'] = 'default' #'4to1_mid_lowang.map' # default
      prop['hard_mask_file'] =None
      prop['det_cal_file'] = 6399 #? default?
      prop['save_format']=''
      
      return prop;
      #
   @iliad
   def main(self,input_file=None,output_directory=None):
     # run reduction, write auxiliary script to add something here.

       red = DirectEnergyConversion()
       red.initialise(self.iliad_prop)
       outWS = red.convert_to_energy()
       #SaveNexus(ws,Filename = 'MARNewReduction.nxs')

       #when run from web service, return additional path for web server to copy data to";
       return outWS

   def __init__(self):
       """ sets properties defaults for the instrument with Name"""
       ReductionWrapper.__init__(self,'MER',rv)
#----------------------------------------------------------------------------------------------------------------------



if __name__=="__main__":
     maps_dir = 'd:/Data/MantidSystemTests/Data'
     data_dir ='d:/Data/Mantid_Testing/14_11_27'
     ref_data_dir = 'd:/Data/MantidSystemTests/SystemTests/AnalysisTests/ReferenceResults' 
     config.setDataSearchDirs('{0};{1};{2}'.format(data_dir,maps_dir,ref_data_dir))
     #config.appendDataSearchDir('d:/Data/Mantid_GIT/Test/AutoTestData')
     config['defaultsave.directory'] = data_dir # folder to save resulting spe/nxspe files. Defaults are in

     # execute stuff from Mantid
     rd = ReduceMERLIN()
     rd.def_advanced_properties()
     rd.def_main_properties()


     #using_web_data = False
     #if not using_web_data:
     #   run_dir=os.path.dirname(os.path.realpath(__file__))
     #   file = os.path.join(run_dir,'reduce_vars.py')
     #   rd.export_changed_values(file)

     rd.main()
