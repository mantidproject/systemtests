"""
These system tests are to verify the behaviour of the ISIS reflectometry reduction scripts
"""

import stresstesting
from mantidsimple import *

class ReflectometryISIS(stresstesting.MantidStressTest):

    def runTest(self):
        
        PIX=1.1E-3 #m
        SC=75
        avgDB=29
        
        Load(Filename='POLREF00004699.raw',OutputWorkspace='POLREF00004699')
        X=mtd['POLREF00004699']
        ConvertUnits(InputWorkspace=X,OutputWorkspace=X,Target="Wavelength",AlignBins="1")
        #Reference intensity to normalise by
        CropWorkspace(InputWorkspace=X,OutputWorkspace='Io',XMin=0.8,XMax=14.5,StartWorkspaceIndex=2,EndWorkspaceIndex=2)
        #Crop out transmission and noisy data 
        CropWorkspace(InputWorkspace=X,OutputWorkspace='D',XMin=0.8,XMax=14.5,StartWorkspaceIndex=3)
        Io=mtd['Io']
        D=mtd['D']
    
        #Peform the normaisation step
        Divide(D,Io,'I','1','1')
        I=mtd['I']
        
        #Should now have signed theta vs Lambda
        ConvertSpectrumAxis(InputWorkspace=I,OutputWorkspace='tl1',Target='signed_theta')
        
        # Move the detector so that the detector channel matching the reflected beam is at 0,0
        MoveInstrumentComponent(Workspace=I,ComponentName="lineardetector",X=0,Y=0,Z=-PIX*( (SC-avgDB)/2.0 +avgDB) )
        
        ConvertSpectrumAxis(InputWorkspace=I,OutputWorkspace='tl2',Target='signed_theta')
        
        #Check that signed two theta is being caluclated correctly (not normalised)
        ws1 = mtd['tl2_1']
        upperHistogram = ws1.getNumberHistograms()-1
        for i in range(0, upperHistogram):
            thisTheta = ws1.detectorSignedTwoTheta(ws1.getDetector(i))
            nextTheta = ws1.detectorSignedTwoTheta(ws1.getDetector(i+1)) 
            #This check would fail if negative values were being normalised.
            self.assertTrue(thisTheta < nextTheta)
        return True;
        
    def doValidate(self):
        return True;
    