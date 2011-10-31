import stresstesting
from mantidsimple import *

''' Sample script from Tim Charlton. Described as Mantid version of quick:lam'''
class AAASkipableTest(stresstesting.MantidStressTest):
    
  def runTest(self):
    print "Just want to have an intentionally skipped test"
    import sys
    sys.exit(97) # special code for skipping test

  def validate(self):
    return []
