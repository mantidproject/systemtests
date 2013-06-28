import stresstesting
from mantid.simpleapi import *

class VesuvioFittingTest(stresstesting.MantidStressTest):

    def runTest(self):
        LoadVesuvio(Filename='14188-14190',OutputWorkspace='raw_ws',SpectrumList='135',Mode='SingleDifference',
                    InstrumentParFile=r'IP0005.dat')
        CropWorkspace(InputWorkspace='raw_ws',OutputWorkspace='raw_ws',XMin=50,XMax=562)

        function_str = \
            "composite=ComptonScatteringCountRate,NumDeriv=1,IntensityConstraints=\"Matrix(1|3)0|-1|3\";"\
            "name=GramCharlierComptonProfile,WorkspaceIndex=0,Mass=1.007940,HermiteCoeffs=1 0 1;"\
            "name=GaussianComptonProfile,WorkspaceIndex=0,Mass=27.000000;"\
            "name=GaussianComptonProfile,WorkspaceIndex=0,Mass=91.000000"

        ties_str = "f1.Width=10.000000,f2.Width=25.000000,f0.FSECoeff=f0.Width*sqrt(2)/12"
        constraints_str = "2.000000 < f0.Width < 7.000000"

        ws_prefix = "fit"
        Fit(InputWorkspace='raw_ws',Function=function_str,Ties=ties_str,Constraints=constraints_str,
            Output=ws_prefix, CreateOutput=True,OutputCompositeMembers=True,MaxIterations=5000,
            Minimizer="Levenberg-Marquardt,AbsError=1e-08,RelError=1e-08")

        self.assertTrue(ws_prefix + "_Workspace" in mtd, "Expected function workspace in ADS")
        self.assertTrue(ws_prefix + "_Parameters" in mtd, "Expected parameters workspace in ADS")        
        self.assertTrue(ws_prefix + "_NormalisedCovarianceMatrix" in mtd, "Expected covariance workspace in ADS")
        
    def validate(self):
        self.tolerance = 1e-07
        return "fit_Workspace","VesuvioFittingTest.nxs"
