import stresstesting
import os
from mantid.simpleapi import *
from IndirectImport import is_supported_f2py_platform

class QLresTest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True
            
    def runTest(self):
        import IndirectBayes as Main
        nbins = ['1', '1']
        sname = 'irs26176_graphite002_red'
        rname = 'irs26173_graphite002_res'
        rsname = ''
        wfile = ''
        erange = [-0.5, 0.5]
        fitOp = [1, 2, 0, 0]
        loopOp = False
        verbOp = False
        plotOp = False
        saveOp = False

        spath = sname+'.nxs'    # path name for sample nxs file
        LoadNexusProcessed(Filename=spath, OutputWorkspace=sname)
        rpath = rname+'.nxs'    # path name for res nxs file
        LoadNexusProcessed(Filename=rpath, OutputWorkspace=rname)
        Main.QLRun('QL',sname,rname,rsname,erange,nbins,fitOp,wfile,loopOp,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26176_graphite002_QLr_Fit','ISISIndirectBayes_QlresTest.nxs'

#========================================================================
class ResNormTest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True
    
    def runTest(self):
        import IndirectBayes as Main
        nbin = '1'
        vname = 'irs26173_graphite002_red'
        rname = 'irs26173_graphite002_res'
        erange = [-0.2, 0.2]
        verbOp = False
        plotOp = False
        saveOp = False

        vpath = vname+'.nxs'    # path name for van nxs file
        LoadNexusProcessed(Filename=vpath, OutputWorkspace=vname)
        rpath = rname+'.nxs'    # path name for res nxs file
        LoadNexusProcessed(Filename=rpath, OutputWorkspace=rname)
        Main.ResNormRun(vname,rname,erange,nbin,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26173_graphite002_ResNorm_Fit','ISISIndirectBayes_ResNormTest.nxs'

#=========================================================================
class QuestTest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True
    
    def runTest(self):
        import IndirectBayes as Main
        nbins = [1, 1]
        nbs = [50, 30]
        sname = 'irs26176_graphite002_red'
        rname = 'irs26173_graphite002_res'
        erange = [-0.5, 0.5]
        fitOp = [1, 2, 0, 0]
        loopOp = False
        verbOp = False
        plotOp = 'None'
        saveOp = False

        spath = sname+'.nxs'   # path name for sample nxs file
        LoadNexusProcessed(Filename=spath, OutputWorkspace=sname)
        rpath = rname+'.nxs'    # path name for res nxs file
        LoadNexusProcessed(Filename=rpath, OutputWorkspace=rname)
        Main.QuestRun(sname,rname,nbs,erange,nbins,fitOp,loopOp,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26176_graphite002_Qst_Fit','ISISIndirectBayes_QuestTest.nxs'

#=============================================================================
class QSeTest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True
            
    def runTest(self):
        import IndirectBayes as Main
        nbins = ['1', '1']
        sname = 'irs26176_graphite002_red'
        rname = 'irs26173_graphite002_res'
        rsname = ''
        wfile = ''
        erange = [-0.5, 0.5]
        fitOp = [1, 2, 0, 0]
        loopOp = False
        verbOp = False
        plotOp = False
        saveOp = False

        spath = sname+'.nxs'    # path name for sample nxs file
        LoadNexusProcessed(Filename=spath, OutputWorkspace=sname)
        rpath = rname+'.nxs'    # path name for res nxs file
        LoadNexusProcessed(Filename=rpath, OutputWorkspace=rname)
        Main.QLRun('QSe',sname,rname,rsname,erange,nbins,fitOp,wfile,loopOp,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26176_graphite002_QSe_Fit','ISISIndirectBayes_QSeTest.nxs'

#=============================================================================
class QLDataTest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True
    
    def runTest(self):
        import IndirectBayes as Main
        nbins = ['1', '1']
        sname = 'irs26176_graphite002_red'
        rname = 'irs26173_graphite002_red'
        rsname = ''
        wfile = ''
        erange = [-0.5, 0.5]
        fitOp = [1, 2, 0, 0]
        loopOp = False
        verbOp = False
        plotOp = False
        saveOp = False

        spath = sname+'.nxs'    # path name for sample nxs file
        LoadNexusProcessed(Filename=spath, OutputWorkspace=sname)
        rpath = rname+'.nxs'    # path name for res nxs file
        LoadNexusProcessed(Filename=rpath, OutputWorkspace=rname)
        Main.QLRun('QL',sname,rname,rsname,erange,nbins,fitOp,wfile,loopOp,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26176_graphite002_QLd_Fit','ISISIndirectBayes_QLDataTest.nxs'

#=============================================================================
class JumpCETest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True

    def runTest(self):
        import IndirectBayes as Main
        sname = 'irs26176_graphite002_QLr'
        cropOp = False
        qrange = [0.0, 5.0]
        verbOp = False
        plotOp = False
        saveOp = False

        filename = sname+'_Parameters.nxs' # path name for nxs file
        LoadNexusProcessed(Filename=filename, OutputWorkspace=sname+'_Parameters')
        
        Main.JumpRun(sname,'CE','QLr','FW11',cropOp,qrange,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26176_graphite002_QLr_CEfit_FW11','ISISIndirectBayes_JumpCETest.nxs'


#=============================================================================
class JumpSSTest(stresstesting.MantidStressTest):
    
    def skipTests(self):
        if is_supported_f2py_platform():
            return False
        else:
            return True
    
    def runTest(self):
        import IndirectBayes as Main
        sname = 'irs26176_graphite002_QLr'
        cropOp = False
        qrange = [0.0, 5.0]
        verbOp = False
        plotOp = False
        saveOp = False

        path = sname+'_Parameters.nxs'  # path name for nxs file
        LoadNexusProcessed(Filename=path, OutputWorkspace=sname+'_Parameters')
        Main.JumpRun(sname,'SS','QLr','FW11',cropOp,qrange,verbOp,plotOp,saveOp)

    def validate(self):
        return 'irs26176_graphite002_QLr_SSfit_FW11','ISISIndirectBayes_JumpSSTest.nxs'

#=============================================================================
