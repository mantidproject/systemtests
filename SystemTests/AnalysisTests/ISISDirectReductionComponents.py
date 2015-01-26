import os,sys
import stresstesting
from mantid.simpleapi import *
from mantid.api import Workspace,IEventWorkspace

from Direct.PropertyManager import PropertyManager
from Direct.RunDescriptor   import RunDescriptor
import ISIS_MariReduction as mr

#----------------------------------------------------------------------
class ISIS_ReductionWebLike(stresstesting.MantidStressTest):
    def __init__(self):
       stresstesting.MantidStressTest.__init__(self)

       self.rd = mr.ReduceMARIFromFile()
       self.rd.def_main_properties()
       self.rd.def_advanced_properties()

       save_folder = config['defaultsave.directory']

       self.rd.save_web_variables(os.path.join(save_folder,'reduce_vars.py'))
       

    def runTest(self):
        web_var_folder = config['defaultsave.directory']
        sys.path.insert(0,web_var_folder)

        #import reduce_vars as web_vars
        reload(mr)


        mr.web_var.advanced_vars['save_format']='nxs'
        # web services currently need input file to be defined
        input_file = 'MAR11001.RAW'
        rez = mr.main(input_file,web_var_folder)

        self.rd.reducer.sample_run = input_file 
        saveFileName = self.rd.reducer.save_file_name
        oputputFile = os.path.join(web_var_folder,saveFileName+'.nxs')

        self.assertTrue(os.path.exists(oputputFile))
        
        web_var_file = os.path.join(web_var_folder,'reduce_vars')
        if os.path.exists(web_var_file+'.py'):
            os.remove(web_var_file+'.py')
        if os.path.exists(web_var_file+'.pyc'):
            os.remove(web_var_file+'.pyc')


    def get_result_workspace(self):
       """Returns the result workspace to be checked"""
       saveFileName = self.rd.reducer.save_file_name
       outWS = Load(Filename=saveFileName+'.nxs')
       return "outWS"   
    def get_reference_file(self):
        return "MARIReduction.nxs"

#----------------------------------------------------------------------
class ISISLoadFilesRAW(stresstesting.MantidStressTest):


    def __init__(self):
       stresstesting.MantidStressTest.__init__(self)
       self.valid = False

    def runTest(self):
        propman = PropertyManager('MAR')

        propman.sample_run = 11001
        propman.load_monitors_with_workspace = True

        mon_ws = PropertyManager.sample_run.get_monitors_ws()
        ws = PropertyManager.sample_run.get_workspace()
        
        self.assertTrue(isinstance(ws,Workspace))
        self.assertEqual(ws.getNumberHistograms(),922)

        DeleteWorkspace(ws)

        propman.load_monitors_with_workspace = False
        propman.sample_run = 11001
        ws = PropertyManager.sample_run.get_workspace()
        mon_ws = PropertyManager.sample_run.get_monitors_ws()

        self.assertEqual(ws.getNumberHistograms(),919)
        self.assertEqual(mon_ws.getNumberHistograms(),3)
        wsName = ws.name()
        self.assertEqual(wsName,PropertyManager.sample_run.get_ws_name())

        #
        propman = PropertyManager('MAPS')
        propman.sample_run = 17186
        propman.load_monitors_with_workspace = False

        mon_ws = PropertyManager.sample_run.get_monitors_ws()
        ws = PropertyManager.sample_run.get_workspace()
        self.assertTrue(isinstance(ws,Workspace))
        self.assertEqual(ws.getNumberHistograms(),41472)
        self.assertEqual(mon_ws.getNumberHistograms(),4)
        #
        self.valid = True

    def validate(self):
        return self.valid

class ISISLoadFilesMER(stresstesting.MantidStressTest):


    def __init__(self):
       stresstesting.MantidStressTest.__init__(self)
       self.valid = False

    def runTest(self):
        #
        propman = PropertyManager('MER')
        propman.sample_run = 6398
        propman.det_cal_file = 6399 
        propman.load_monitors_with_workspace = False

        mon_ws = PropertyManager.sample_run.get_monitors_ws()
        ws = PropertyManager.sample_run.get_workspace()
        self.assertTrue(isinstance(ws,Workspace))
        self.assertEqual(ws.getNumberHistograms(),69632)
        self.assertEqual(mon_ws.getNumberHistograms(),9)

        # 
        propman.sample_run = 18492
        propman.det_cal_file = None 
        mon_ws = PropertyManager.sample_run.get_monitors_ws()
        ws = PropertyManager.sample_run.get_workspace()
        self.assertTrue(isinstance(ws,Workspace))
        self.assertEqual(ws.getNumberHistograms(),69632)
        self.assertEqual(mon_ws.getNumberHistograms(),9)


        self.valid = True


    def validate(self):
        return self.valid

class ISISLoadFilesLET(stresstesting.MantidStressTest):


    def __init__(self):
       stresstesting.MantidStressTest.__init__(self)
       self.valid = False

    def runTest(self):

        # 
        propman = PropertyManager('LET')
        propman.sample_run = 6278
        propman.load_monitors_with_workspace = False

        mon_ws = PropertyManager.sample_run.get_monitors_ws()
        ws = PropertyManager.sample_run.get_workspace()

        self.assertTrue(isinstance(ws,IEventWorkspace))
        self.assertEqual(ws.getNumberHistograms(),40960)
        self.assertTrue(isinstance(mon_ws,Workspace))
        self.assertEqual(mon_ws.getNumberHistograms(),9)


        self.valid = True


    def validate(self):
        return self.valid

if __name__=="__main__":
    ISISLoadFilesMER.runTest()
