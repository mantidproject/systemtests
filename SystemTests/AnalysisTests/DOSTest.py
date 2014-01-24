import stresstesting
from mantid.kernel import *
from mantid.api import *
from mantid.simpleapi import *

class DOSPhononTest(stresstesting.MantidStressTest):
    
    def runTest(self):
      file_name = 'squaricn.phonon'
      self.ouput_ws_name = 'squaricn'
      self.ref_result = 'II.DOSTest.nxs'

      DensityOfStates(File=file_name,OutputWorkspace=self.ouput_ws_name)

    def validate(self):
      return self.ouput_ws_name, self.ref_result

#------------------------------------------------------------------------------------

class DOSCastepTest(stresstesting.MantidStressTest):
    
    def runTest(self):
      file_name = 'squaricn.castep'
      self.ouput_ws_name = 'squaricn'
      self.ref_result = 'II.DOSTest.nxs'

      DensityOfStates(File=file_name,OutputWorkspace=self.ouput_ws_name)
    
    def validate(self):
      return self.ouput_ws_name, self.ref_result

#------------------------------------------------------------------------------------

class DOSRamanActiveTest(stresstesting.MantidStressTest):
    
    def runTest(self):
      file_name = 'squaricn.phonon'
      spec_type = 'Raman_Active'
      self.ouput_ws_name = 'squaricn'
      self.ref_result = 'II.DOSRamanTest.nxs'

      DensityOfStates(File=file_name, SpectrumType=spec_type, OutputWorkspace=self.ouput_ws_name)
    
    def validate(self):
      self.tolerance = 1e-3
      return self.ouput_ws_name, self.ref_result

#------------------------------------------------------------------------------------

class DOSIRActiveTest(stresstesting.MantidStressTest):
    
    def runTest(self):
      file_name = 'squaricn.phonon'
      spec_type = 'IR_Active'
      self.ouput_ws_name = 'squaricn'
      self.ref_result = 'II.DOSIRTest.nxs'

      DensityOfStates(File=file_name, SpectrumType=spec_type, OutputWorkspace=self.ouput_ws_name)

    def validate(self):
      return self.ouput_ws_name, self.ref_result

