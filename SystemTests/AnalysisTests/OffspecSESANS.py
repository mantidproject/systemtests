from stresstesting import MantidStressTest
from mantid.simpleapi import mtd, config
import offspec

class OffspecSESANS(MantidStressTest):
    
    def requiredFiles(self):
        return ["OFFSPEC00010791.raw","OFFSPEC00010792.raw","OFFSPEC00010793.raw"]
    
    def runTest(self):
        binning=["2.0","0.2","12.0","2"]
        config["default.instrument"] = "OFFSPEC"
        offspec.nrSESANSP0Fn("10792","P055","109","119","2","1",binning)
        offspec.nrSESANSFn("10791+10793","dPMMA","","P055pol",
                           "100","130","2","1","2","3009.9",binning,"2","0")
        
    def validate(self):
        return "dPMMASESANS","OffspecSESANS.nxs"
