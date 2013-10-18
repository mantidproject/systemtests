import stresstesting
from mantid.simpleapi import *
from mantid import config
import SANSUtility as su
import SANSadd2 as add

import os

class SANSUtilityTest(stresstesting.MantidStressTest):

    def runTest(self):
        # created after issue reported in #8156
        ws = Load('LOQ54432')
        print su.getFilePathFromWorkspace(ws)
        self.assertTrue('Data/LOQ/LOQ54432.raw' in su.getFilePathFromWorkspace(ws))
        ws = Load('LOQ99618.RAW')
        print su.getFilePathFromWorkspace(ws)
        self.assertTrue('Data/LOQ/LOQ99618.RAW' in su.getFilePathFromWorkspace(ws))
        add.add_runs(('LOQ54432','LOQ54432'),'LOQ','.raw')
        ws = Load('LOQ54432-add')
        file_path =  su.getFilePathFromWorkspace(ws)
        self.assertTrue('logs/LOQ54432-add' in file_path)
        os.remove(file_path)
        
