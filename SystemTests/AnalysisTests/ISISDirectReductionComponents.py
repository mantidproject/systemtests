import stresstesting
from mantid.simpleapi import *
from mantid.api import Workspace,IEventWorkspace

from Direct.PropertyManager import PropertyManager
from Direct.RunDescriptor   import RunDescriptor

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
