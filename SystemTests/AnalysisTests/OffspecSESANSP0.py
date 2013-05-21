from stresstesting import MantidStressTest
from mantid.simpleapi import config,mtd
import offspec

class OffspecSESANSP0(MantidStressTest):
    
    def requiredFiles(self):
        return ["OFFSPEC00010792.raw"]
    
    def runTest(self):
        binning=["2.0","0.2","12.0","2"]
        config["default.instrument"] = "OFFSPEC"
        offspec.nrSESANSP0Fn("10792","P055","109","119","2","1",binning)
        
    def cleanup(self):
        pass
        
    def validate(self):
        return "P055pol","OffspecSESANSP0.nxs"
