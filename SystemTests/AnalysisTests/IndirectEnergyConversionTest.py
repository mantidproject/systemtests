import stresstesting
from mantid.simpleapi import *

class IndirectEnergyConversionTest(stresstesting.MantidStressTest):

    def runTest(self):
        instrument = 'IRIS'
        analyser = 'graphite'
        reflection = '002'
        detector_range = [3, 53]
        files = 'irs21360.raw'
        rebin_string = '-0.5,0.005,0.5'
        output_workspace = 'IndirectEnergyConversionTest'

        InelasticIndirectReduction(OutputWorkspace=output_workspace,
                                   InputFiles=files,
                                   RebiNString=rebin_string,
                                   DetectorRange=detector_range,
                                   Instrument=instrument,
                                   Analyser=analyser,
                                   Reflection=reflection)


    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('SpectraMap')
        return 'IndirectEnergyConversionTest', 'IndirectEnergyConversionTest.nxs'
