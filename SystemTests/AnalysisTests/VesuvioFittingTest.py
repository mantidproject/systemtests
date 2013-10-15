import stresstesting
from mantid.simpleapi import *

#------------------------------------------------------------------------------------------------------------------
WS_PREFIX="fit"

def _do_fit(k_is_free):
    """
    Run the Vesuvio. If k_is_free is False then it is fixed to f0.Width*sqrt(2)/12
    
    """
    LoadVesuvio(Filename='14188-14190',OutputWorkspace='raw_ws',SpectrumList='135',Mode='SingleDifference',
                InstrumentParFile=r'IP0005.dat')
    CropWorkspace(InputWorkspace='raw_ws',OutputWorkspace='raw_ws',XMin=50,XMax=562)
    # Convert to seconds
    ScaleX(InputWorkspace='raw_ws',OutputWorkspace='raw_ws',Operation='Multiply',Factor=1e-06)
    
    function_str = \
        "composite=ComptonScatteringCountRate,NumDeriv=1,IntensityConstraints=\"Matrix(1|3)0|-1|3\";"\
        "name=GramCharlierComptonProfile,WorkspaceIndex=0,Mass=1.007940,HermiteCoeffs=1 0 1;"\
        "name=GaussianComptonProfile,WorkspaceIndex=0,Mass=27.000000;"\
        "name=GaussianComptonProfile,WorkspaceIndex=0,Mass=91.000000"

    if k_is_free:
        ties_str = "f1.Width=10.000000,f2.Width=25.000000"
    else:
        ties_str = "f1.Width=10.000000,f2.Width=25.000000,f0.FSECoeff=f0.Width*sqrt(2)/12"

    constraints_str = "2.000000 < f0.Width < 7.000000"
    
    Fit(InputWorkspace='raw_ws',Function=function_str,Ties=ties_str,Constraints=constraints_str,
        Output=WS_PREFIX, CreateOutput=True,OutputCompositeMembers=True,MaxIterations=5000,
        Minimizer="Levenberg-Marquardt,AbsError=1e-08,RelError=1e-08")
    # Convert to microseconds
    ScaleX(InputWorkspace=WS_PREFIX + '_Workspace',OutputWorkspace=WS_PREFIX + '_Workspace',Operation='Multiply',Factor=1e06)
    

#------------------------------------------------------------------------------------------------------------------

class VesuvioFittingTest(stresstesting.MantidStressTest):

    def runTest(self):
        _do_fit(k_is_free=False)

        self.assertTrue(WS_PREFIX + "_Workspace" in mtd, "Expected function workspace in ADS")
        self.assertTrue(WS_PREFIX + "_Parameters" in mtd, "Expected parameters workspace in ADS")        
        self.assertTrue(WS_PREFIX + "_NormalisedCovarianceMatrix" in mtd, "Expected covariance workspace in ADS")
        
    def validate(self):
        self.tolerance = 1e-06
        return "fit_Workspace","VesuvioFittingTest.nxs"

#------------------------------------------------------------------------------------------------------------------

class VesuvioFittingWithKFreeTest(stresstesting.MantidStressTest):

    def runTest(self):
        _do_fit(k_is_free=True)

        self.assertTrue(WS_PREFIX + "_Workspace" in mtd, "Expected function workspace in ADS")
        self.assertTrue(WS_PREFIX + "_Parameters" in mtd, "Expected parameters workspace in ADS")        
        self.assertTrue(WS_PREFIX + "_NormalisedCovarianceMatrix" in mtd, "Expected covariance workspace in ADS")
        
    def validate(self):
        self.tolerance = 1e-06
        return "fit_Workspace","VesuvioFittingWithKFreeTest.nxs"
