import stresstesting
import os
from mantid.simpleapi import *

#====================================================================================================
class IN10SiliconTest(stresstesting.MantidStressTest):

    def runTest(self):
        import IndirectForce as Main 

        mode = 'INX'
        instr = 'IN10'
        ana = 'silicon'
        refl = '111'
        run = 'P3OT_350K'
        rejectZ = False
        useM = False
        verbOp = True
        saveOp = False
        plotOp = False
        Main.InxStart(instr,run,ana,refl,rejectZ,useM,'',verbOp,plotOp,saveOp)
        
    def validate(self):
        self.tolerance = 1e-2
        self.disableChecking.append("Instrument")
        return 'IN10_P3OT_350K_silicon111_red', 'ISISIndirectForce_IN10SiliconTest.nxs'


#====================================================================================================
class IN16SiliconTest(stresstesting.MantidStressTest):
    
    def runTest(self):
        import IndirectForce as Main

        mode = 'ASCII'
        instr = 'IN16'
        ana = 'silicon'
        refl = '111'
        run = '65722'
        rejectZ = True
        useM = False
        verbOp = True
        saveOp = False
        plotOp = False
        Main.IbackStart(instr,run,ana,refl,rejectZ,useM,'',verbOp,plotOp,saveOp)

    def validate(self):
        self.tolerance = 1e-2
        self.disableChecking.append("SpectraMap")
        self.disableChecking.append("Instrument")
        return 'IN16_65722_silicon111_red', 'ISISIndirectForce_IN16SiliconTest.nxs'


#====================================================================================================
