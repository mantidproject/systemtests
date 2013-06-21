
import stresstesting
from mantid.simpleapi import *
from isis_reflgui.l2q import *

class L2QScriptTest(stresstesting.MantidStressTest):

    
    def runTest(self):
        ws = Load(Filename="INTER00013469.nxs")
        ws = ConvertUnits(InputWorkspace=ws,Target="Wavelength",AlignBins=1)
        Io=CropWorkspace(InputWorkspace=ws,XMin=0.8,XMax=14.5,StartWorkspaceIndex=2,EndWorkspaceIndex=2)
        D=CropWorkspace(InputWorkspace=ws,XMin=0.8,XMax=14.5,StartWorkspaceIndex=3)
        I= Divide(LHSWorkspace=D,RHSWorkspace=Io,AllowDifferentNumberSpectra=True)
        detectorName =  'linear-detector'
        theta = 0.7
        l2q(ws, detectorName, theta) # This generates an output workspace called IvsQ
        
        
    def validate(self):
        return 'IvsQ','L2QReferenceResult.nxs'
        

