import stresstesting
import mantid
from mantid.simpleapi import *
import re

SPECIAL = ["InputWorkspace", "OutputWorkspace", "Workspace",
           "ReductionProperties"]
SPECIAL_UPPER = [name.upper for name in SPECIAL]

# TODO this list should be empty
ALG_BAD_PARAMS = {
    "CalculateUMatrix(v1)":("a", "b", "c", "alpha", "beta", "gamma"),
    "ConvertToMD(v1)":("dEAnalysisMode"),
    "ConvertToMDHelper(v1)":("dEAnalysisMode"),
    "FindUBUsingLatticeParameters(v1)":("a", "b", "c", "alpha", "beta", "gamma"),
    "IndexSXPeaks(v1)":("a", "b", "c", "alpha", "beta", "gamma", "dTolerance"),
    "ModeratorTzero(v1)":("tolTOF"),
    "MuscatFunc(v1)":("dQ", "dW"),
    "OptimizeCrystalPlacement(v1)":("nPeaks", "nParams", "nIndexed"),
    "PDFFourierTransform(v1)":("rho0"),
    "PoldiAutoCorrelation(v5)":("wlenmin", "wlenmax"),
    "PoldiLoadChopperSlits(v1)":("nbLoadedSlits"),
    "PoldiLoadSpectra(v1)":("nbSpectraLoaded"),
    "PoldiProjectRun(v1)":("wlenmin", "wlenmax"),
    "PoldiRemoveDeadWires(v1)":("nbExcludedWires", "nbAuteDeadWires"),
    "SaveIsawQvector(v1)":("Qx_vector", "Qy_vector", "Qz_vector"),
    "SCDCalibratePanels(v1)":("a", "b", "c", "alpha", "beta", "gamma",
                          "useL0", "usetimeOffset", "usePanelWidth",
                          "usePanelHeight", "usePanelPosition",
                          "usePanelOrientation", "tolerance",
                          "MaxPositionChange_meters"),
    "SetUB(v1)":("a", "b", "c", "alpha", "beta", "gamma", "u", "v"),
    "ViewBOA(v1)":("CD-Distance")
    }


class CodeConventAlgorithms(stresstesting.MantidStressTest):
    def verifyAlgName(self, name):
        if not self.algRegExp.match(name):
            print name + " has a name that violates conventions"
            return False

        MAX_LEN = 40 # TODO convention says 20 is the maximum
        if bool(len(name) > MAX_LEN):
            print "%s has a name that is longer than " % name, \
                "%d characters (%d > %d)" % (MAX_LEN, len(name), MAX_LEN)
            return False

        # passed all of the checks
        return True

    def checkAllowed(self, alg_descr, name):
        if alg_descr not in ALG_BAD_PARAMS.keys():
            return False

        return name in  ALG_BAD_PARAMS[alg_descr]

    def verifyProperty(self, alg_descr, name):
        upper = name.upper()
        if (upper in SPECIAL_UPPER) and (not name in SPECIAL):
            index = SPECIAL_UPPER.index(upper)
            print alg_descr + " property (" + name + ") has special name "\
                + "with wrong case: " + name + " should be " + SPECIAL[index]
            return False

        if not self.paramRegExp.match(name):
            if not self.checkAllowed(alg_descr, name):
                print alg_descr + " property (" + name +") violates conventions"
                return False

        # passed all of the checks
        return True

    def runTest(self):
        self.__ranOk = 0
        self.algRegExp = re.compile(r'^[A-Z][a-zA-Z0-9]+$')
        self.paramRegExp = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

        algs = AlgorithmFactory.getRegisteredAlgorithms(True)

        for (name, versions) in algs.iteritems():
            if not self.verifyAlgName(name):
                self.__ranOk += 1
                continue
            for version in versions:
                # get an instance
                alg = mantid.FrameworkManager.createAlgorithm(name, version)
                alg_descr = "%s(v%d)" % (name, version)

                # verify the categories

                # verify the properties
                props = alg.getProperties()
                for prop in props:
                    if not self.verifyProperty(alg_descr, prop.name):
                        self.__ranOk += 1


    def validate(self):
        if self.__ranOk > 0:
            print "Found %d errors. Coding conventions found at" % self.__ranOk,\
                "http://www.mantidproject.org/Mantid_Standards"
            return False

        return True
