"""
System Test for BASIS autoreduction
"""
from mantid.simpleapi import *

import stresstesting
import shutil
import os

class BASISAutoReductionTest(stresstesting.MantidStressTest):
	
	def requiredFiles(self):
		return ['BSS_13387_event.nxs']

	def cleanup(self):
		return True

	def runTest(self):
		idfdir = config['instrumentDefinition.directory']
		autows = 'data_ws'
		autows_monitor = 'monitor_ws'
		Load(Filename='BSS_13387_event.nxs', OutputWorkspace=autows)
		LoadMask(Instrument='BASIS', OutputWorkspace='BASIS_MASK', InputFile='BASIS_AutoReduction_Mask.xml')
		MaskDetectors(Workspace=autows, MaskedWorkspace='BASIS_MASK')
		ModeratorTzeroLinear(InputWorkspace=autows,OutputWorkspace=autows)
		LoadParameterFile(Workspace=autows, Filename=os.path.join(idfdir,'BASIS_silicon_111_Parameters.xml'))
		LoadNexusMonitors(Filename='BSS_13387_event.nxs', OutputWorkspace=autows_monitor)
		Rebin(InputWorkspace=autows_monitor,OutputWorkspace=autows_monitor,Params='10')
		ConvertUnits(InputWorkspace=autows_monitor, OutputWorkspace=autows_monitor, Target='Wavelength')
		OneMinusExponentialCor(InputWorkspace=autows_monitor, OutputWorkspace=autows_monitor, C='0.20749999999999999', C1='0.001276')
		Scale(InputWorkspace=autows_monitor, OutputWorkspace=autows_monitor, Factor='9.9999999999999995e-07')
		ConvertUnits(InputWorkspace=autows, OutputWorkspace=autows, Target='Wavelength', EMode='Indirect')
		RebinToWorkspace(WorkspaceToRebin=autows, WorkspaceToMatch=autows_monitor, OutputWorkspace=autows)
		Divide(LHSWorkspace=autows, RHSWorkspace=autows_monitor,  OutputWorkspace=autows)
		ConvertUnits(InputWorkspace=autows, OutputWorkspace=autows, Target='DeltaE', EMode='Indirect')
		CorrectKiKf(InputWorkspace=autows, OutputWorkspace=autows,EMode='Indirect')

		Rebin(InputWorkspace=autows, OutputWorkspace=autows, Params='-0.12,0.0004,0.12')
		#GroupDetectors(InputWorkspace=autows, OutputWorkspace=autows, MapFile='/SNS/BSS/shared/autoreduce/BASIS_Grouping.xml', Behaviour='Sum')
		SofQW3(InputWorkspace=autows, OutputWorkspace=autows+'_sqw', QAxisBinning='0.2,0.2,2.0', EMode='Indirect', EFixed='2.082')
		#SaveDaveGrp(Filename=dave_grp_filename, InputWorkspace=autows+'_sqw', ToMicroEV=True)
		#SaveNexus(Filename="basis_auto_sqw.nxs", InputWorkspace=autows+'_sqw') 

	def validate(self):
		# Need to disable checking of the Spectra-Detector map because it isn't
		# fully saved out to the nexus file; some masked detectors should be picked
		# up with by the mask values in the spectra
		self.tolerance = 1e-7
		self.disableChecking.append('Axes')
		self.disableChecking.append('SpectraMap')
 		self.disableChecking.append('Instrument')
        	return 'data_ws_sqw','BASISAutoReduction.nxs'

