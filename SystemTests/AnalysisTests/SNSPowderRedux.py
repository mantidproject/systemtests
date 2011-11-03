import stresstesting
from mantidsimple import *

class PG3Analysis(stresstesting.MantidStressTest):
    ref_file  = 'PG3_4844_reference.gsa'
    cal_file  = "PG3_FERNS_d4832_2011_08_24.cal"
    char_file = "PG3_characterization_2011_08_31-HR.txt"

    def requiredFiles(self):
        files = [self.ref_file, self.cal_file, self.char_file] 
        files.append("/SNS/PG3/IPTS-2767/0/4844/NeXus/PG3_4844_event.nxs")
        files.append("/SNS/PG3/IPTS-2767/0/4866/NeXus/PG3_4866_event.nxs")
        files.append("/SNS/PG3/IPTS-2767/0/5226/NeXus/PG3_5226_event.nxs")
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        # run the actual code
        SNSPowderReduction(Instrument="PG3", RunNumber=4844, Extension="_event.nxs",
                           PreserveEvents=True,
                           CalibrationFile=self.cal_file,
                           CharacterizationRunsFile=self.char_file,
                           UnwrapRef=62, LowResRef=15000, RemovePromptPulseWidth=50,
                           Binning=-0.0004, BinInDspace=True, FilterBadPulses=True,
                           SaveAs="gsas", OutputDirectory=savedir,
                           NormalizeByCurrent=True, FinalDataUnits="dSpacing")


        # load output gsas file and the golden one
        LoadGSS("PG3_4844.gsa", "PG3_4844")
        LoadGSS(self.ref_file, "PG3_4844_golden")

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        return ('PG3_4844','PG3_4844_golden')
