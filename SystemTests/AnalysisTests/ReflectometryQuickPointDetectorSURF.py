import stresstesting
from mantid.simpleapi import *
from isis_reflectometry import quick
reload(quick)

class ReflectometryQuickPointDetectorSURF(stresstesting.MantidStressTest):
    """
    This is a system test for the top-level quick routines. Quick is the name given to the 
    ISIS reflectometry reduction scripts.
    
    """
    
    def runTest(self):
        defaultInstKey = 'default.instrument'
        defaultInstrument = config[defaultInstKey]
        try
            config[defaultInstKey] = 'SURF'
            LoadISISNexus(Filename='102951', OutputWorkspace='102951')
            LoadISISNexus(Filename='102935', OutputWorkspace='102935')
            transmissionRuns = '102935'
            runNo = '102951'
            incidentAngle = 0.25
            quick.quick(runNo, trans=transmissionRuns, theta=incidentAngle)
        finally:
            config[defaultInstKey] = defaultInstrument
        
    def validate(self):
        self.disableChecking.append('Instrument')
        return '102951_IvsQ','ReflectometryQuickPointDetectorSURFReferenceResult.nxs'
