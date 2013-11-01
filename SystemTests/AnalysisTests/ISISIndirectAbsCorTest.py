import stresstesting
import os
from mantid.simpleapi import *
from IndirectImport import is_supported_f2py_platform

#====================================================================================================
class CylAbsTest(stresstesting.MantidStressTest):

    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True

    def runTest(self):
        import IndirectAbsCor as Main

        sname = 'irs26176_graphite002_red'
        LoadNexusProcessed(Filename=sname, OutputWorkspace=sname)

        beam = [3.0, 1.0, -1.0, 2.0, -2.0, 0.0, 3.0, 0.0, 3.0]
        size = [0.2, 0.25, 0.26, 0.0]
        density = [0.1, 0.1, 0.1]
        sigs = [5.0, 0.1, 0.1]
        siga = [0.0, 5.0, 5.0]
        avar = 0.002
        verbOp = True
        saveOp = False
        Main.AbsRun(sname, 'cyl', beam, 2, size, density,
            sigs, siga, avar, verbOp, saveOp)
    
    def validate(self):
        self.tolerance = 1e-3
        return 'irs26176_graphite002_cyl_Abs', 'ISISIndirectAbsCor_CylAbsTest.nxs'

#====================================================================================================
class FltAbsTest(stresstesting.MantidStressTest):

    def runTest(self):
        import IndirectAbsCor as Main

        sname = 'irs26176_graphite002_red'
        LoadNexusProcessed(Filename=sname, OutputWorkspace=sname)
        
        beam = ''
        size = [0.1, 0.01, 0.01]
        density = [0.1, 0.1, 0.1]
        sigs = [5.0, 0.1, 0.1]
        siga = [0.0, 5.0, 5.0]
        avar = 45.0
        verbOp = True
        saveOp = False
        Main.AbsRun(sname, 'flt', beam, 2, size, density,
            sigs, siga, avar, verbOp, saveOp)
    
    def validate(self):
        self.tolerance = 1e-3
        return 'irs26176_graphite002_flt_Abs', 'ISISIndirectAbsCor_FltAbsTest.nxs'


class FltAbsTSecCloseTo90Test(stresstesting.MantidStressTest):

    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True

    def runTest(self):
        import IndirectAbsCor as Main

        sname = 'irs59330_graphite002_red'
        LoadNexusProcessed(Filename=sname, OutputWorkspace=sname)

        beam = ''
        size = [0.1, 0.01, 0.01]
        density = [0.05, 0.5, 0.5]
        sigs = [5.0, 0.1, 0.1]
        siga = [0.0, 5.0, 5.0]
        avar = 45.0
        verbOp = True
        saveOp = False
        Main.AbsRun(sname, 'flt', beam, 2, size, density,
            sigs, siga, avar, verbOp, saveOp)
    
    def validate(self):
        self.tolerance = 1e-3
        return 'irs59330_graphite002_flt_Abs', 'ISISIndirectAbsCor_FltAbsTSecCloseTo90Test.nxs'
