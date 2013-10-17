"""
System test for ARCS reduction
"""

from mantid.simpleapi import *
import os
import stresstesting

class ARCSReductionTest(stresstesting.MantidStressTest):
	
	def requiredFiles(self):
		return ["ARCS_23961_event.nxs","WBARCS.nxs"]

	def requiredMemoryMB(self):
		return 4000

	def cleanup(self):     
		if os.path.exists(self.nxspeFile):
            		os.remove(self.nxspeFile)
		if os.path.exists(self.vanFile1):
            		os.remove(self.vanFile1)
		if os.path.exists(self.vanFile0):
            		os.remove(self.vanFile0)
		return True


	def runTest(self):
		self.vanFile1=os.path.join(config.getString('defaultsave.directory'),'ARCSvan_1.nxs')
		self.vanFile0=os.path.join(config.getString('defaultsave.directory'),'ARCSvan_0.nxs')

		config['default.facility']="SNS"
		DgsReduction(
             		SampleInputFile="ARCS_23961_event.nxs",
             		OutputWorkspace="reduced",
             		IncidentBeamNormalisation="ByCurrent",
             		DetectorVanadiumInputFile="WBARCS.nxs",
             		UseBoundsForDetVan=True,
             		DetVanIntRangeLow=0.35,
             		DetVanIntRangeHigh=0.75,
             		DetVanIntRangeUnits="Wavelength",
             		SaveProcessedDetVan=True,
             		SaveProcDetVanFilename=self.vanFile0,
            		)
		
		Ei=mtd["reduced"].run().get("Efixed").value[0]
		SaveNXSPE(InputWorkspace="reduced",Filename=self.nxspeFile,Efixed=Ei,psi=psi,KiOverKfScaling=True,ParFile=self.parFile)
		
	def validate(self):
		#test vanadium file
		self.assertTrue(os.path.exists(self.vanFile))
		van=Load(self.vanFile)
		self.assertEqual(van.blocksize(),1)
		self.assertEqual(van.getNumberHistograms(),51200)
		DeleteWorkspace(van)
		self.assertTrue(os.path.exists(self.nxspeFile))
		nxspe=LoadNXSPE(self.nxspeFile)
		self.disableChecking.append('Instrument')

		return 'nxspe','ARCSReduction.nxs'



