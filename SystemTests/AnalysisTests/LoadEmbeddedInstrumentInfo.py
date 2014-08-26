import stresstesting
from mantid.simpleapi import *

"""
Here testing against embedded instrument info in different raw file formats

This include to test that embedded information in raw ISIS Nexus file formats 
get loaded correctly.

"""	

# here test against a custom made ISIS raw hist nexus file created by Freddie
# where the A1_window has be, for the purpose of testing, been put at a 
# completely wrong location of (0,3,0)
class ISISRawHistNexus(stresstesting.MantidStressTest):
    
  def runTest(self):

    # ISIS raw hist nexus file with A1_window at location (0,3,0)
    MAPS00018314_raw_ISIS_hist = Load('MAPS00018314.nxs')

  def validate(self):

    MAPS00018314_raw_ISIS_hist = mtd['MAPS00018314_raw_ISIS_hist']
    inst = MAPS00018314_raw_ISIS_hist.getInstrument()
    A1window = inst.getComponentByName('MAPS/A1_window')
    
    if str(A1window.getPos()) != '[0,3,0]' :
    	    return False
    
    # check also instrument parameters added to MAPS component
    paramNames = inst.getParameterNames()
    paramString = ''
    for param in paramNames:
	paramString = paramString + param
	   
    if str(len(paramString)) != '483' :
    	    return False    
    
    return True


# here test against a raw event nexus LET dataset with embedded informatino. 
class ISISRawEventNexus(stresstesting.MantidStressTest):
    
  def runTest(self):

    LET00017675_raw_ISIS_event = Load('LET00017675.nxs')

  def validate(self):

    LET00017675_raw_ISIS_event = mtd['LET00017675_raw_ISIS_event']
    inst = LET00017675_raw_ISIS_event.getInstrument()
    normMon1Spec = int(inst.getNumberParameter('norm-mon1-spec')[0])
    
    if str(normMon1Spec) != '73729' :
        print str(normMon1Spec)
        return False
    
    paramNames = inst.getParameterNames()
    paramString = ''
    for param in paramNames:
        paramString = paramString + param
    
    if str(len(paramString)) != '979' :
        print len(paramString)
        return False
    
    return True