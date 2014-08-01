"""
THis test is moved from a unit test suit here because it takes too long to run for a unit test.
"""
import stresstesting
from mantid.simpleapi import CreateChunkingFromInstrument

class CreateChunkingFromInstrumentTest(stresstesting.MantidStressTest):
    def __init__(self):
        stresstesting.MantidStressTest.__init__(self)
        self.errorMessage=""

    def runTest(self):
        result = CreateChunkingFromInstrument(InstrumentName = "snap",\
                                              ChunkNames = "East,West",\
                                              MaxBankNumber = 20
                                              )
        if result.columnCount() != 1:
            self.errorMessage = "Result table doesn't have 1 column"
            return
        if result.getColumnNames()[0] != "BankName":
            self.errorMessage = "Column name isn't BankName"
            return
        if result.rowCount() != 2:
            self.errorMessage = "Result table doesn't have 2 rows"
            return
        
    def validate(self):
        if self.errorMessage!="":
            print "Found the following errors:\n",self.errorMessage
            return False

        return True   
