import stresstesting
from mantid.simpleapi import *

''' Simply tests that our LoadRaw and LoadISISNexus algorithms produce the same workspace'''
class RawVNexus(stresstesting.MantidStressTest):
    
  def runTest(self):
    LoadRaw('SANS2D00000808.raw', 'Raw')

  def validate(self):
    return 'Raw','SANS2D00000808.nxs'
