import os
#os.environ["PATH"] = r"c:/Mantid/Code/builds/br_master/bin/Release;"+os.environ["PATH"]

""" Sample MARI reduction scrip used in testing ReductionWrapper """ 
from Direct.ReductionWrapper import *
try:
    import reduce_vars as rv
except:
    rv = None


class ReduceMARIFromFile(ReductionWrapper):
   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 
       prop = {};
       prop['sample_run'] = 11001;
       prop['wb_run'] = 11060
       prop['incident_energy'] = 12;
       prop['energy_bins'] = [-11,0.05,11]

      # Absolute units reduction properties.
       prop['monovan_run'] = 11015
       prop['sample_mass'] = 10
       prop['sample_rmm'] = 435.96
       return prop

   @AdvancedProperties
   def def_advanced_properties(self):
      """  separation between simple and advanced properties depends
           on scientist, experiment and user.
           main properties override advanced properties.      
      """
      prop = {};
      prop['map_file'] = "mari_res.map"
      prop['monovan_mapfile'] = "mari_res.map"
      prop['hard_mask_file'] ="mar11015.msk"
      prop['det_cal_file'] =11060
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
       ReductionWrapper.__init__(self,'MAR',rv)
#----------------------------------------------------------------------------------------------------------------------
class ReduceMARIFromWorkspace(ReductionWrapper):

   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 
       prop = {};
       prop['sample_run'] =  Load(Filename='MAR11001.RAW',OutputWorkspace='MAR11001.RAW')
       # WB workspace
       prop['wb_run']     = Load(Filename='MAR11060.RAW',OutputWorkspace='MAR11060.RAW')
       prop['incident_energy'] = 12;
       prop['energy_bins'] = [-11,0.05,11]

      # Absolute units reduction properties.
       prop['monovan_run'] =  Load(Filename='MAR11015.RAW',OutputWorkspace='MAR11015.RAW')
       prop['sample_mass'] = 10
       prop['sample_rmm'] = 435.96

       # Why do we need this?
       #last_alg = mono_run.getHistory().lastAlgorithm()
       #print last_alg

       #AddSampleLog(Workspace=mono_ws, LogName='Filename', 
       #             LogText=last_alg.getPropertyValue('Filename'))
       #last_alg = van_run.getHistory().lastAlgorithm()
       #van_ws = van_run
       #AddSampleLog(Workspace=van_ws, LogName='Filename', 
       #          LogText=last_alg.getPropertyValue('Filename'))

       return prop

   @AdvancedProperties
   def def_advanced_properties(self):
      """  separation between simple and advanced properties depends
           on scientist, experiment and user.
           main properties override advanced properties.      
      """
      prop = {};
      prop['map_file'] = "mari_res.map"
      prop['monovan_mapfile'] = "mari_res.map"
      prop['hard_mask_file'] ="mar11015.msk"
      # MARI calibration uses one of data files defined on instrument. Here vanadium run is used for calibration
      # TODO: Why not workspace?
      prop['det_cal_file'] ="11060"
      prop['save_format']=''
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
       ReductionWrapper.__init__(self,'MAR',rv)
#----------------------------------------------------------------------------------------------------------------------
class ReduceMARIMon2Norm(ReductionWrapper):

   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 
       prop = {};
       prop['sample_run'] =  Load(Filename='MAR11001.RAW',OutputWorkspace='MAR11001.RAW')
       # WB workspace
       prop['wb_run']     = Load(Filename='MAR11060.RAW',OutputWorkspace='MAR11060.RAW')
       prop['incident_energy'] = 12;
       prop['energy_bins'] = [-11,0.05,11]

      # Absolute units reduction properties.
       prop['monovan_run'] =  11015 #Load(Filename='MAR11015.RAW',OutputWorkspace='MAR11015.RAW')
       prop['sample_mass'] = 10
       prop['sample_rmm'] = 435.96

       return prop

   @AdvancedProperties
   def def_advanced_properties(self):
      """  separation between simple and advanced properties depends
           on scientist, experiment and user.
           main properties override advanced properties.      
      """
      prop = {};
      prop['map_file'] = "mari_res.map"
      prop['monovan_mapfile'] = "mari_res.map"
      prop['hard_mask_file'] ="mar11015.msk"
      #prop['hardmaskOnly'] ="mar11015.msk"
      prop['normalise_method']='monitor-2'
      # reduction from workspace currently needs detector_calibration file
      # MARI calibration uses one of data files defined on instrument. Here vanadium run is used for calibration
      # TODO: Why not workspace?, check it
      prop['det_cal_file'] ="11060"
      prop['save_format']=[]
      return prop;
      #
   @iliad
   def main(self,input_file=None,output_directory=None):
     # run reduction, write auxiliary script to add something here.

       red = DirectEnergyConversion()
       red.initialise(self.iliad_prop)
       outWS = red.convert_to_energy()
       #SaveNexus(ws,Filename = 'MARNewReduction.nxs')
       #SaveNXSPE(outWS,'MAR_reduction2.nxspe')


       #when run from web service, return additional path for web server to copy data to";
       return outWS
   def __init__(self):
       """ sets properties defaults for the instrument with Name"""
       ReductionWrapper.__init__(self,'MAR',rv)
#----------------------------------------------------------------------------------------------------------------------
class MARIReductionSum(ReductionWrapper):
   @MainProperties
   def def_main_properties(self):
       """ Define main properties used in reduction """ 
       prop = {}
       prop['sample_run'] = [11001,11015]
       prop['wb_run'] = 11060
       prop['incident_energy'] = 11
       prop['energy_bins'] = [-11,0.05,11]
       prop['sum_runs']    = True

      # Absolute units reduction properties.
       #prop['monovan_run'] = 11015
       #prop['sample_mass'] = 32.58
       #prop['sample_rmm'] = 50.9415# 435.96
       return prop

   @AdvancedProperties
   def def_advanced_properties(self):
      """  separation between simple and advanced properties depends
           on scientist, experiment and user.
           main properties override advanced properties.      
      """
      prop = {}
      prop['map_file'] = "mari_res.map"
      prop['monovan_mapfile'] = "mari_res.map"
      prop['hard_mask_file'] ="mar11015.msk"
      #prop['det_cal_file'] =11060
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
       ReductionWrapper.__init__(self,'MAR',rv)
#----------------------------------------------------------------------------------------------------------------------



if __name__=="__main__":

     maps_dir = 'd:/Data/MantidSystemTests/Data'
     data_dir ='d:/Data/Mantid_Testing/14_12_15'
     ref_data_dir = 'd:/Data/MantidSystemTests/SystemTests/AnalysisTests/ReferenceResults' 
     config.setDataSearchDirs('{0};{1};{2}'.format(data_dir,maps_dir,ref_data_dir))
     #config.appendDataSearchDir('d:/Data/Mantid_GIT/Test/AutoTestData')
     config['defaultsave.directory'] = data_dir # folder to save resulting spe/nxspe files. Defaults are in

     # execute stuff from Mantid
     #rd = ReduceMARIFromFile()
     rd= ReduceMARIMon2Norm()
     rd.def_advanced_properties()
     rd.def_main_properties()


     #using_web_data = False;
     #if not using_web_data:
     #   run_dir=os.path.dirname(os.path.realpath(__file__))
     #   file = os.path.join(run_dir,'reduce_vars.py');
     #   rd.export_changed_values(file);

     rd.main()

