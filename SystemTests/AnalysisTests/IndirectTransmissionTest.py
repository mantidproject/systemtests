import stresstesting
from mantid.simpleapi import *

class IndirectTransmissionTest(stresstesting.MantidStressTest):

	def runTest(self):
		instrument = "IRIS"
		analyser = "graphite"
		reflection = "002"

		#using water
		formula = "H2-O"
		density = 0.1
		thickness = 0.1

		IndirectTransmission(Instrument=instrument, Analyser=analyser, Reflection=reflection,
										ChemicalFormula=formula, NumberDensity=density, Thickness=thickness)

	def validate(self):
		return 'IRIS_graphite_002_Transmission','IndirectTransmissionTest.nxs'