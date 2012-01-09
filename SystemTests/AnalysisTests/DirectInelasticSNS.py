"""
Test the SNS inelatic reduction scripts.
"""

import stresstesting
import os
import shutil
import glob
from mantidsimple import *
from numpy import *

class DirectInelaticSNSTest(stresstesting.MantidStressTest):

    #setup routines
    def topbottom(self):
        #create top and bottom mask         
        LoadEventNexus(Filename='SEQ_12384_event.nxs', OutputWorkspace='mask',CompressTolerance=0.1)
        Rebin(InputWorkspace='mask',OutputWorkspace='mask',Params="500,15500,16000",PreserveEvents=False)
        w=mtd['mask']
        indexlist=[]
        for i in range(w.getNumberHistograms()):
            if (i%128) in [0,1,2,3,4,5,6,7,120,121,122,123,124,125,126,127]:
                indexlist.append(i)
        
        MaskDetectors(Workspace='mask',WorkspaceIndexList=indexlist)
        SaveNexus(InputWorkspace="mask",Filename=self.customDataDir+"mask_top_bottom.nxs")
        mtd.deleteWorkspace('mask')

    def setupFiles(self):
        self.customDataDir=mtd.settings['defaultsave.directory']+'temp/'
        datasearch = mtd.settings['datasearch.directories']
        datasearch = datasearch.split(';')
        filename=''
        for d in datasearch:
            temp = os.path.join(d, 'SEQ_12384_event.nxs')
            if os.path.exists(temp):
                filename=temp
        self.cleanup()
        os.mkdir(self.customDataDir)
        shutil.copyfile(filename,os.path.join(self.customDataDir,'SEQ_12384_event.nxs'))
        shutil.copyfile(filename,os.path.join(self.customDataDir,'SEQ_12385_event.nxs'))
        self.topbottom()


    #Routines from SNS scripts
    def createanglelist(self,ws,amin,amax,astep):
        """
        Function to create a map of detectors corresponding to angles in a certain range	
        """	
        bin_angles=arange(amin+astep*0.5,amax+astep*0.5,astep)
        a=[[] for i in range(len(bin_angles))] #list of list with detector IDs
        w=mtd[ws]
        origin = w.getInstrument().getSample().getPos()
        for i in range(w.getNumberHistograms()):
            ang=w.getDetector(i).getTwoTheta(origin,V3D(0,0,1))*180/math.pi
            index=int((ang-amin)/astep)
            if (index>=0) and (index<len(a)) and ((w.getDetector(i).getID())>0):
                a[index].append(w.getSpectrum(i).getSpectrumNo())
        #create lists with angles and detector ID only for bins where there are detectors 
        ang_list=[]
        detIDlist=[]
        for elem,ang in zip(a,bin_angles):
            if len(elem)>0:
                detIDlist.append(elem)
                ang_list.append(ang)
        # file with grouping information
        f=open(self.customDataDir+"group.map",'w')
        print >>f,len(ang_list)
        for i in range(len(ang_list)):
            print >>f,i
            print >>f,len(detIDlist[i])
            mystring=str(detIDlist[i]).strip(']').strip('[')
            mystring=mystring.replace(',','')
            print >>f,mystring
        f.close()
        # par file
        f=open(self.customDataDir+"group.par",'w')
        print >>f,len(ang_list)
        for i in range(len(ang_list)):
            print >>f,5.5,ang_list[i],0.0,1.0,1.0,1
        f.close()
        return [ang_list,detIDlist]

    def GetEiT0(self,ws_name,EiGuess):
        """
        Function to get Ei and  -T0
        """
        alg=GetEi(InputWorkspace=ws_name,Monitor1Spec="1",Monitor2Spec="2",EnergyEstimate=EiGuess)				#Run GetEi algorithm
        [Ei,Tzero]=[float(alg.getPropertyValue("IncidentEnergy")),-float(alg.getPropertyValue("Tzero"))]		#Extract incident energy and T0
        return [Ei,Tzero]

    def LoadPathMaker(self,runs,folder,prefix,suffix):
        """	
        Function to create paths to files from runnumbers
        return a list of lists with the path, and a corrected list of runs. Files in the inner lists are added together
        side effects: none
        """
        path=[]
        newruns=[]
        try:
            len(runs)
        except:
            runs=[runs]
        for r in runs:
            try:
                len(r)
            except:
                r=[r]
            temppath=[]
            tempnewruns=[]
            for i in range(len(r)):
                temppath.append(folder+prefix+str(r[i])+suffix)      
                tempnewruns.append(r[i])
                if (not(os.path.isfile(temppath[i]))):
                    raise IOError(temppath[i]+" not found")
            path.append(temppath)
            newruns.append(tempnewruns)
        return [path,newruns]

    def CreateMasksAndVanadiumNormalization(self,vanfile,maskfile=''):		
        """
        Creates the Van workspace, one bin for each histogram, containing the integrated Vanadium intensity
        VAN also contains the mask.
        """
    	if (not(os.path.isfile(self.customDataDir+"van.nx5"))):
    		LoadEventNexus(Filename=vanfile,OutputWorkspace="VAN")
		
    		Rebin(InputWorkspace="VAN",OutputWorkspace="VAN",Params="1000,15000,16000",PreserveEvents=False)	#integrate all events between 1000 and 16000 microseconds
    		NormaliseByCurrent(InputWorkspace="VAN",OutputWorkspace="VAN")									    #normalize by proton charge
    		MedianDetectorTest(InputWorkspace="VAN",OutputWorkspace="MASK",SignificanceTest=100,HighThreshold =100) #determine which detectors to mask, and store them in the "MASK" workspace
    		if len(maskfile)>0:
    		    LoadNexus(Filename=maskfile,OutputWorkspace="temp_mask")
    		    MaskDetectors(Workspace="MASK",MaskedWorkspace="temp_mask")		    						    #add detectors masked in "temp_mask" to "MASK"
    		    DeleteWorkspace(Workspace="temp_mask")
    		MaskDetectors(Workspace="VAN",MaskedWorkspace="MASK")										        #Mask "VAN". This prevents dividing by 0		
    		DeleteWorkspace(Workspace="MASK")														            #Mask is carried by VAN workspace
    		SaveNexus(InputWorkspace="VAN",Filename=self.customDataDir+"van.nx5")
    	else:
    		LoadNexus(Filename=self.customDataDir+"van.nx5",OutputWorkspace="VAN")
		    

    #functions from stresstesting 
    def requiredFiles(self):
        return ['SEQ_12384_event.nxs']


    def cleanup(self):
        for ws in ['IWS', 'OWST', 'VAN', 'monitor_ws']:
            if mtd.workspaceExists(ws):
                mtd.deleteWorkspace(ws)
        if os.path.exists(self.customDataDir):
            shutil.rmtree(self.customDataDir)
       
    def runTest(self):
        self.setupFiles()
        runs=[[12384,12385]]
        maskfile=self.customDataDir+'mask_top_bottom.nxs'
        V_file=self.customDataDir+'SEQ_12384_event.nxs'
        Eguess=35.0														#initial energy guess
        Erange="-10.0,0.25,32.0"										#Energy bins:    Emin,Estep,Emax
        datadir=self.customDataDir		                                #Data directory	
        outdir=self.customDataDir	                                    #Output directory
        fout_prefix="Ei_35.0_"      
        ang_offset=0.0
        angle_name='SEOCRot'                                            #Name of the angle to read
        maskandnormalize=True	                                        #flag to do the masking and normalization to Vanadium
        flag_spe=False                                                  #flag to generate an spe file
        flag_nxspe=True                                                 #flag to generate an nxspe file
        do_powder=True                                                  #group detectors by angle
        anglemin=0.				                                        #minumum angle
        anglemax=70.				                                    #maximum angle
        anglestep=1.				                                    #angle step - this can be fine tuned for pixel arc over detectors

        if (maskandnormalize):
	        self.CreateMasksAndVanadiumNormalization(V_file,maskfile=maskfile)	#Creates a worspaces for Vanadium normalization and masking

        [paths,runs]=self.LoadPathMaker(runs,self.customDataDir,'SEQ_','_event.nxs') #process teh runlist
        for flist,rlist,i in zip(paths,runs,range(len(paths))):	   		#rlist is the inner list of runnumbers
            psitmp=[]
            for f,j in zip(flist,range(len(flist))):
                if (j==0):
			        LoadEventNexus(Filename=f,OutputWorkspace="IWS")						#Load an event Nexus file
			        LoadNexusMonitors(Filename=f,OutputWorkspace="monitor_ws")				#Load monitors    		
                else:
			        LoadEventNexus(Filename=f,OutputWorkspace="IWS_temp")					#Load an event Nexus file
			        LoadNexusMonitors(Filename=f,OutputWorkspace="monitor_ws_temp")			#Load monitors   
			        Plus(LHSWorkspace="IWS",RHSWorkspace="IWS_temp",OutputWorkspace="IWS")	#Add events to the original workspcace 
			        Plus(LHSWorkspace="monitor_ws",RHSWorkspace="monitor_ws_temp",OutputWorkspace="monitor_ws")	#Add  monitors to the original monitor workspcace 
			        #cleanup
			        DeleteWorkspace("IWS_temp")                                                                 						
			        DeleteWorkspace("monitor_ws_temp")
        w=mtd["IWS"]
        psi=array(w.getRun()[angle_name].value).mean()+ang_offset                        
        FilterBadPulses(InputWorkspace="IWS",OutputWorkspace = "IWS",LowerCutoff = 50)	    # get psi before filtering bad pulses
        [Efixed,T0]=self.GetEiT0("monitor_ws",Eguess)											#Get Ei and -T0 using the function defined before
        ChangeBinOffset(InputWorkspace="IWS",OutputWorkspace="OWS",Offset=T0)				#Change all TOF by -T0
        NormaliseByCurrent(InputWorkspace="OWS",OutputWorkspace="OWS")						#normalize by proton charge
        ConvertUnits(InputWorkspace="OWS",OutputWorkspace="OWS",Target="Wavelength",EMode="Direct",EFixed=Efixed)	#The algorithm for He3 tube efficiency requires wavelength units
        He3TubeEfficiency(InputWorkspace="OWS",OutputWorkspace="OWS")										        #Apply correction due to absorption in He3
        ConvertUnits(InputWorkspace="OWS",OutputWorkspace="OWS",Target="DeltaE",EMode="Direct",EFixed=Efixed)		#Switch  to energy transfer
        CorrectKiKf(InputWorkspace="OWS",OutputWorkspace="OWS")                                                     # apply ki/kf correction
        Rebin(InputWorkspace="OWS",OutputWorkspace="OWST",Params=Erange,PreserveEvents=False)                       # go to histogram mode (forget events)
        ConvertToDistribution(Workspace="OWST")														                #Convert to differential cross section by dividing by the energy bin width
        DeleteWorkspace("OWS") 
        if (maskandnormalize):
            MaskDetectors(Workspace="OWST",MaskedWorkspace="VAN")						#apply overall mask
            # the following is commented, since it's the same run, not a real vanadium
		    #Divide(LHSWorkspace="OWST",RHSWorkspace="VAN",OutputWorkspace="OWST")		#normalize by Vanadium, if desired
        if (do_powder):
            if (i==0):
                mapping=self.createanglelist("OWST",anglemin,anglemax,anglestep)
            GroupDetectors(InputWorkspace="OWST",OutputWorkspace="OWST",MapFile=self.customDataDir+"group.map",Behaviour="Sum")
            SolidAngle(InputWorkspace="OWST",OutputWorkspace="sa")
            Divide(LHSWorkspace="OWST",RHSWorkspace="sa",OutputWorkspace="OWST")
            DeleteWorkspace("sa") 
        fname_out="%s%s%d_%g"%(outdir,fout_prefix,rlist[0],psi)
        fname_out=fname_out.replace('.','p')
        if flag_spe:
            SaveSPE(InputWorkspace="OWST",Filename=fname_out+".spe")					#save the data in spe format. 
            if (i==0):
                SavePHX(InputWorkspace="OWST",Filename=fname_out+".spe")
        if flag_nxspe:                                                                  #save in NXSPE format       
            if (do_powder):
                SaveNXSPE(InputWorkspace="OWST",Filename=fname_out+".nxspe",Efixed=Efixed,psi=psi,KiOverKfScaling=True,ParFile=outdir+"group.par")
            else:
                SaveNXSPE(InputWorkspace="OWST",Filename=fname_out+".nxspe",Efixed=Efixed,psi=psi,KiOverKfScaling=True)

    def validate(self):
        #check if required files are created
        self.assertTrue(os.path.exists(self.customDataDir+'group.map'))
        self.assertDelta(os.path.getsize(self.customDataDir+'group.map'),700000,100000)
        self.assertTrue(os.path.exists(self.customDataDir+'group.par'))
        self.assertGreaterThan(os.path.getsize(self.customDataDir+'group.par'),1000)
        self.assertTrue(os.path.exists(self.customDataDir+'van.nx5'))
        self.assertGreaterThan(os.path.getsize(self.customDataDir+'van.nx5'),10000000)
        #find the nxspe filename: it should be only one, but the name might depend on the rounding of phi
        nxspelist=glob.glob(self.customDataDir+'*.nxspe')
        if len(nxspelist)!=1:
            return False
        nxspefilename=nxspelist[0]
        self.assertGreaterThan(os.path.getsize(nxspefilename),100000)
        psifilename=float((nxspefilename.split('12384_')[1].split('.nxspe'))[0].replace('p','.'))
        self.assertDelta(psifilename,-24,0.01)
        #input workspace
        self.assertLessThan(mtd["IWS"].getNumberEvents(),100000)
        self.assertGreaterThan(mtd["IWS"].getNumberEvents(),90000)
        return "OWST",os.path.join(os.path.dirname(__file__), 'ReferenceResults','DirectInelasticSNS.nxs')

