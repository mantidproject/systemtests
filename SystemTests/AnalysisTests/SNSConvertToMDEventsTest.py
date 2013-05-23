import stresstesting
import numpy
import os
from mantid.simpleapi import *

######################################################################
# Common configuration
# Main data file /SNS/SEQ/IPTS-4783/data
DATA_FILE = "SEQ_11499_event.nxs" 
# Vanadium file
VAN_FILE = "SEQ_van.nxs"
# Initial energy guess
E_GUESS = 50
# Energy bins: Emin, Estep, Emax
E_RANGE = "-10.0,0.2,45.0"
#######################################################################

def makeOutputName(ws_name, dohist, doproj):
    md_ws_name = ws_name + '_md'
    tag=""
    if dohist:
    	tag += "h"
    else:
    	tag += "e"
    if doproj:
    	tag += "wp"
    else:
    	tag += "np"
        
    md_ws_name += "_" + tag
    return md_ws_name

def GetEiT0(ws_name, EiGuess):
    # Run GetEi algorithm (old API)
    alg = GetEi(InputWorkspace=ws_name, Monitor1Spec="1",
    	                          Monitor2Spec="2", EnergyEstimate=EiGuess)
    # Extract incident energy and T0
    return [alg[0],-alg[3]]

def execReduction(dohist, doproj):
    # Load event data
    LoadEventNexus(Filename=DATA_FILE, OutputWorkspace="IWS")
    # Load the monitors
    LoadNexusMonitors(Filename=DATA_FILE, OutputWorkspace="MonWS")
    # Get Ei and -T0 using the function defined before
    (Efixed, T0) = GetEiT0("MonWS", E_GUESS)
    # Change all TOF by -T0
    ChangeBinOffset(InputWorkspace="IWS", OutputWorkspace="OWS", Offset=T0)
    # Normalize by proton charge
    NormaliseByCurrent(InputWorkspace="OWS", OutputWorkspace="OWS")
    # The algorithm for He3 tube efficiency requires wavelength units
    ConvertUnits(InputWorkspace="OWS", OutputWorkspace="OWS",
                 Target="Wavelength", EMode="Direct", EFixed=Efixed)	
    # Apply correction due to absorption in He3
    He3TubeEfficiency(InputWorkspace="OWS", OutputWorkspace="OWS")
    # Switch  to energy transfer
    ConvertUnits(InputWorkspace="OWS", OutputWorkspace="OWS", Target="DeltaE",
                 EMode="Direct", EFixed=Efixed)
    # Apply k_i/k_f factor
    CorrectKiKf(InputWorkspace="OWS", OutputWorkspace="OWS")
    if dohist:
    	# Make sure the bins are correct
    	Rebin(InputWorkspace="OWS", OutputWorkspace="OWS", Params=E_RANGE,
              PreserveEvents=False)
    	# Convert to differential cross section by dividing by the energy
        # bin width
    	ConvertToDistribution(Workspace="OWS")
    
    # Load vanadium file
    LoadNexus(Filename=VAN_FILE, OutputWorkspace="VAN")
    # Apply overall mask
    MaskDetectors(Workspace="OWS", MaskedWorkspace="VAN")
    # Normalize by Vanadium
    Divide(LHSWorkspace="OWS", RHSWorkspace="VAN", OutputWorkspace="OWS")
    
    # Rename workspace to something meaningful
    workspace_name = "_".join(DATA_FILE.split('.')[0].split('_')[:2])
    RenameWorkspace(InputWorkspace="OWS",  OutputWorkspace=workspace_name)
    # Need to fix the goniometer angle by 49.73 degrees
    w = mtd[workspace_name]
    psi = w.getRun()["CCR13VRot"].getStatistics().mean + 49.73
    AddSampleLog(Workspace=workspace_name, LogName="CCR13VRot_Fixed",
                 LogType="Number Series", LogText=str(psi))
    # Set the Goiniometer information
    SetGoniometer(Workspace=workspace_name, Axis0="CCR13VRot_Fixed,0,1,0,1")
    # Set the information for the UB matrix
    SetUB(Workspace=workspace_name,
          a=3.643, b=3.643, c=5.781, alpha=90, beta=90, gamma=120,
          u='1,1,0', v='0,0,1')
    # Create the MDEventWorkspace
    md_output_ws = makeOutputName(workspace_name, dohist, doproj)

    if not doproj:
        ConvertToMD(InputWorkspace=workspace_name,
                          OutputWorkspace=md_output_ws,
    	                  QDimensions='Q3D', MinValues='-5,-5,-5,-10',
    	                  QConversionScales='HKL',
    	                  MaxValues='5,5,5,45', MaxRecursionDepth='1')
    else:
    	ConvertToMD(InputWorkspace=workspace_name,
                          OutputWorkspace=md_output_ws,
    	                  QDimensions='Q3D', MinValues='-5,-5,-5,-10',
    	                  QConversionScales='HKL',
    	                  MaxValues='5,5,5,45', MaxRecursionDepth='1',
    	                  Uproj='1,1,0', Vproj='1,-1,0', Wproj='0,0,1')
    	
    # Remove SPE workspace
    DeleteWorkspace(Workspace=workspace_name)
	
    return md_output_ws

class SNSConvertToMDEventsNoHistNoProjTest(stresstesting.MantidStressTest):
    truth_file = "SEQ_11499_md_enp.nxs"

    def requiredMemoryMB(self):
        """ Require about 2.5GB free """
        return 2500
    
    def requiredFiles(self):
        files = [self.truth_file, DATA_FILE]
        return files	
    
    def runTest(self):    
        self.output_ws = execReduction(False, False)
        
        self.gold_ws_name = self.truth_file.split('.')[0] + "_golden"
        LoadMD(self.truth_file, OutputWorkspace=self.gold_ws_name)
        
    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"
    
    def validate(self):
        self.tolerance = 1.0e-1
        return (self.output_ws, self.gold_ws_name)

class SNSConvertToMDEventsHistNoProjTest(stresstesting.MantidStressTest):
    truth_file = "SEQ_11499_md_hnp.nxs"

    def requiredMemoryMB(self):
        """ Require about 2.5GB free """
        return 2500
    
    def requiredFiles(self):
        files = [self.truth_file, DATA_FILE]
        return files	
    
    def runTest(self):
        self.output_ws = execReduction(True, False)
        
        self.gold_ws_name = self.truth_file.split('.')[0] + "_golden"
        LoadMD(self.truth_file, OutputWorkspace=self.gold_ws_name)
        
    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"
    
    def validate(self):
        self.tolerance = 1.0e-1
        return (self.output_ws, self.gold_ws_name)

class SNSConvertToMDEventsNoHistProjTest(stresstesting.MantidStressTest):
    truth_file = "SEQ_11499_md_ewp.nxs"

    def requiredMemoryMB(self):
        """ Require about 2.5GB free """
        return 2500
    
    def requiredFiles(self):
        files = [self.truth_file, DATA_FILE]
        return files	
    
    def runTest(self):
        self.output_ws = execReduction(False, True)
        
        self.gold_ws_name = self.truth_file.split('.')[0] + "_golden"
        LoadMD(self.truth_file, OutputWorkspace=self.gold_ws_name)
        
    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"
    
    def validate(self):
        self.tolerance = 1.0e-3
        return (self.output_ws, self.gold_ws_name)

class SNSConvertToMDEventsHistProjTest(stresstesting.MantidStressTest):
    truth_file = "SEQ_11499_md_hwp.nxs"

    def requiredMemoryMB(self):
        """ Require about 2.5GB free """
        return 2500
    
    def requiredFiles(self):
        files = [self.truth_file, DATA_FILE]
        return files	
    
    def runTest(self):
        self.output_ws = execReduction(True, True)
        
        self.gold_ws_name = self.truth_file.split('.')[0] + "_golden"
        LoadMD(self.truth_file, OutputWorkspace=self.gold_ws_name)
        
    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"
    
    def validate(self):
        self.tolerance = 1.0e-3
        return (self.output_ws, self.gold_ws_name)

