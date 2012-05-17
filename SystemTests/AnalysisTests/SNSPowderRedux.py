import stresstesting
from mantidsimple import *

class PG3Analysis(stresstesting.MantidStressTest):
    ref_file  = 'PG3_4844_reference.gsa'
    cal_file  = "PG3_FERNS_d4832_2011_08_24.cal"
    char_file = "PG3_characterization_2011_08_31-HR.txt"

    def requiredFiles(self):
        files = [self.ref_file, self.cal_file, self.char_file] 
        files.append("PG3_4844_event.nxs") # /SNS/PG3/IPTS-2767/0/
        files.append("PG3_4866_event.nxs") # /SNS/PG3/IPTS-2767/0/
        files.append("PG3_5226_event.nxs") # /SNS/PG3/IPTS-2767/0/
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
                           LowResRef=15000, RemovePromptPulseWidth=50,
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

class PG3StripPeaks(stresstesting.MantidStressTest):
    ref_file = 'PG3_4866_reference.gsa'
    cal_file  = "PG3_FERNS_d4832_2011_08_24.cal"

    def requiredFiles(self):
        files = [self.ref_file, self.cal_file]
        files.append("PG3_4866_event.nxs") # vanadium
        return files

    def runTest(self):
        # determine where to save
        import os
        savedir = os.path.abspath(os.path.curdir)

        LoadEventNexus(Filename="PG3_4866_event.nxs",
                       OutputWorkspace="PG3_4866",
                       Precount=True)
        FilterBadPulses(InputWorkspace="PG3_4866",
                        OutputWorkspace="PG3_4866")
        RemovePromptPulse(InputWorkspace="PG3_4866",
                          OutputWorkspace="PG3_4866",
                          Width=50)
        CompressEvents(InputWorkspace="PG3_4866",
                       OutputWorkspace="PG3_4866",
                       Tolerance=0.01)
        SortEvents(InputWorkspace="PG3_4866")
        CropWorkspace(InputWorkspace="PG3_4866",
                      OutputWorkspace="PG3_4866",
                      XMax=16666.669999999998)
        LoadCalFile(InputWorkspace="PG3_4866",
                    CalFilename="/SNS/PG3/2011_2_11A_CAL/PG3_FERNS_d4832_2011_08_24.cal",
                    WorkspaceName="PG3")
        MaskDetectors(Workspace="PG3_4866",
                      MaskedWorkspace="PG3_mask")
        AlignDetectors(InputWorkspace="PG3_4866",
                       OutputWorkspace="PG3_4866",
                       OffsetsWorkspace="PG3_offsets")
        ConvertUnits(InputWorkspace="PG3_4866",
                     OutputWorkspace="PG3_4866",
                     Target="TOF")
        UnwrapSNS(InputWorkspace="PG3_4866",
                  OutputWorkspace="PG3_4866",
                  LRef=62)
        RemoveLowResTOF(InputWorkspace="PG3_4866",
                        OutputWorkspace="PG3_4866",
                        ReferenceDIFC=1500)
        ConvertUnits(InputWorkspace="PG3_4866",
                     OutputWorkspace="PG3_4866",
                     Target="dSpacing")
        Rebin(InputWorkspace="PG3_4866",
              OutputWorkspace="PG3_4866",
              Params=(0.1,-0.0004,2.2))
        SortEvents(InputWorkspace="PG3_4866")
        DiffractionFocussing(InputWorkspace="PG3_4866",
                             OutputWorkspace="PG3_4866",
                             GroupingWorkspace="PG3_group")
        EditInstrumentGeometry(Workspace="PG3_4866",
                               PrimaryFlightPath=60,
                               SpectrumIDs=[1],
                               L2=[3.2208],
                               Polar=[90.8074],
                               Azimuthal=[0])
        ConvertUnits(InputWorkspace="PG3_4866",
                     OutputWorkspace="PG3_4866",
                     Target="TOF")
        Rebin(InputWorkspace="PG3_4866",
              OutputWorkspace="PG3_4866",
              Params=[-0.0004])
        ConvertUnits(InputWorkspace="PG3_4866",
                     OutputWorkspace="PG3_4866",
                     Target="dSpacing")
        StripVanadiumPeaks(InputWorkspace="PG3_4866",
                           OutputWorkspace="PG3_4866",
                           PeakPositionTolerance=0.05,
                           FWHM=8,
                           BackgroundType="Quadratic")
        ConvertUnits(InputWorkspace="PG3_4866",
                     OutputWorkspace="PG3_4866",
                     Target="TOF")
        SaveGSS(InputWorkspace="PG3_4866",
                Filename=os.path.join(savedir, "PG3_4866.gsa"),
                SplitFiles="False",
                Append=False,
                Format="SLOG",
                MultiplyByBinWidth=False,
                ExtendedHeader=True)

        # load output gsas file and the golden one
        LoadGSS("PG3_4866.gsa", "PG3_4866")
        LoadGSS(self.ref_file, "PG3_4866_golden")

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        return ('PG3_4866','PG3_4866_golden')
