"""
Test some features of MDWorkspaces, such as 
file-backed MDWorkspaces.
"""

import stresstesting
import os
from mantidsimple import *

###############################################################################
class PlusMDTest(stresstesting.MantidStressTest):
    
    _saved_filename = None

    def compare_binned(self, wsname):
        """ Compare the given workspace to the previously-binned original """
        BinMD(InputWorkspace=wsname,AlignedDim0='Q_lab_x, -3, 3, 100',AlignedDim1='Q_lab_y, -3, 3, 100',AlignedDim2='Q_lab_z, -3, 3, 100',ForceOrthogonal='1',OutputWorkspace="test_binned")
        ws = mtd["test_binned"]
        EqualToMD(ws, self.original_binned, 'comparison')
        comparison = mtd['comparison']
        for i in xrange(comparison.getNPoints()):
            if not comparison.signalAt(i):
                raise Exception("Difference in workspace %s vs original_binned at index %d" % (wsname, i))
    
    def runTest(self):
        # Some platforms can't clean up the open file handle on cncs.nxs from the last test, so run cleanup here as well
        barefilename = "cncs.nxs"
        self._saved_filename = os.path.join(mtd.settings["defaultsave.directory"], barefilename)
        self.cleanup()

        # Load then convert to Q in the lab frame
        LoadEventNexus(Filename=r'CNCS_7860_event.nxs',OutputWorkspace='cncs_nxs')
        ConvertToDiffractionMDWorkspace(InputWorkspace='cncs_nxs', OutputWorkspace='cncs_original', SplitInto=2)
        alg = SaveMD(InputWorkspace='cncs_original', Filename=barefilename)

        self.assertDelta( mtd['cncs_original'].getNPoints(), 112266, 1)
        BinMD(InputWorkspace='cncs_original',AlignedDim0='Q_lab_x, -3, 3, 100',AlignedDim1='Q_lab_y, -3, 3, 100',AlignedDim2='Q_lab_z, -3, 3, 100',ForceOrthogonal='1',OutputWorkspace='cncs_original_binned')
        # Scale by 2 to account for summing
        self.original_binned = mtd['cncs_original_binned']
        self.original_binned *= 2
        
        # Load into memory
        LoadMD(Filename='cncs.nxs',FileBackEnd='0',Memory='100',OutputWorkspace='cncs_mem')

        # ======== Mem + Mem ===========
        LoadMD(Filename='cncs.nxs',FileBackEnd='0',OutputWorkspace='cncs_mem2')
        PlusMD("cncs_mem2", "cncs_mem", "cncs_mem2")
        self.assertDelta( mtd['cncs_mem2'].getNPoints(), 112266*2, 1)
        self.compare_binned('cncs_mem2')
        DeleteWorkspace('cncs_mem2')

        # ======== File + mem, with write buffer ===========
        LoadMD(Filename='cncs.nxs',FileBackEnd='1',Memory='100',OutputWorkspace='cncs_file')
        PlusMD("cncs_file", "cncs_mem", "cncs_file")
        self.compare_binned('cncs_file')
        SaveMD("cncs_file", UpdateFileBackEnd="1")
        self.assertDelta( mtd['cncs_file'].getNPoints(), 112266*2, 1)
        self.compare_binned('cncs_file')
        DeleteWorkspace('cncs_file')

        # Refresh the original file
        SaveMD(InputWorkspace='cncs_original', Filename='cncs.nxs')
        
        # ======== File + mem, with a small write buffer (only 1MB) ======== 
        LoadMD(Filename='cncs.nxs',FileBackEnd='1',Memory='1',OutputWorkspace='cncs_file_small_buffer')
        PlusMD("cncs_file_small_buffer", "cncs_mem", "cncs_file_small_buffer")
        SaveMD("cncs_file_small_buffer", UpdateFileBackEnd="1")
        self.assertDelta( mtd['cncs_file_small_buffer'].getNPoints(), 112266*2, 1)
        self.compare_binned('cncs_file_small_buffer')
        DeleteWorkspace('cncs_file_small_buffer')
                
        # Refresh the original file
        SaveMD(InputWorkspace='cncs_original', Filename='cncs.nxs')

        # ========  File + mem, without a write buffer ======== 
        LoadMD(Filename='cncs.nxs',FileBackEnd='1',Memory='0',OutputWorkspace='cncs_file_nobuffer')
        PlusMD("cncs_file_nobuffer", "cncs_mem", "cncs_file_nobuffer")
        SaveMD("cncs_file_nobuffer", UpdateFileBackEnd="1")
        self.assertDelta( mtd['cncs_file_nobuffer'].getNPoints(), 112266*2, 1)
        self.compare_binned('cncs_file_nobuffer')
        DeleteWorkspace('cncs_file_nobuffer')

        # Refresh the original file
        SaveMD(InputWorkspace='cncs_original', Filename='cncs.nxs')
        
        # ======== File + mem to a new (cloned) file ========  
        LoadMD(Filename='cncs.nxs',FileBackEnd='1',Memory='100',OutputWorkspace='cncs_file')
        PlusMD("cncs_file", "cncs_mem", "cncs_added")
        SaveMD("cncs_added", UpdateFileBackEnd="1")
        self.compare_binned('cncs_added')
        self.assertDelta( mtd['cncs_added'].getNPoints(), 112266*2, 1)

        # Make sure we delete the workspaces so the file handles are freed
        workspaces_to_delete = ["cncs_file", "cncs_mem", "cncs_added"]
        for name in workspaces_to_delete:
            DeleteWorkspace(name)

    def doValidation(self):
        # If we reach here, no validation failed
        return True

    def cleanup(self):
        """
            Remove files create during test
        """
        if self._saved_filename is not None:
            try:
                os.remove(self._saved_filename)
                mtd.sendLogMessage("Removed %s" % self._saved_filename)
            except OSError:
                mtd.sendLogMessage("Failed to remove %s" % self._saved_filename)

            # Plus the _clone version
            filename = os.path.splitext(self._saved_filename)[0]
            filename += '_clone.nxs'
            try:
                os.remove(filename)
                mtd.sendLogMessage("Removed %s " % filename)
            except OSError:
                mtd.sendLogMessage("Failed to remove %s" % self._saved_filename)

###############################################################################
class MergeMDTest(stresstesting.MantidStressTest):
    
    _saved_filenames = []

    def runTest(self):
        LoadEventNexus(Filename='CNCS_7860_event.nxs',
        OutputWorkspace='CNCS_7860_event_NXS',CompressTolerance=0.1)
        
        for omega in xrange(0, 5):
            print "Starting omega %03d degrees" % omega
            CreateMDWorkspace(Dimensions='3',Extents='-5,5,-5,5,-5,5',Names='Q_sample_x,Q_sample_y,Q__sample_z',Units='A,A,A',SplitInto='3',SplitThreshold='200',MaxRecursionDepth='3',
            MinRecursionDepth='3', OutputWorkspace='CNCS_7860_event_MD')
            
            # Convert events to MD events
            AddSampleLog("CNCS_7860_event_NXS", "omega", "%s" % omega, "Number Series")
            AddSampleLog("CNCS_7860_event_NXS", "chi", "%s" % 0, "Number Series")
            AddSampleLog("CNCS_7860_event_NXS", "phi", "%s" % 0, "Number Series")
            ConvertToDiffractionMDWorkspace(InputWorkspace='CNCS_7860_event_NXS',OutputWorkspace='CNCS_7860_event_MD',OutputDimensions='Q (sample frame)',LorentzCorrection='1', Append=True)
        
            alg = SaveMD("CNCS_7860_event_MD", "CNCS_7860_event_rotated_%03d.nxs" % omega)
            self._saved_filenames.append(alg.getPropertyValue("Filename"))
        # End for loop
        alg = MergeMDFiles(Filenames='CNCS_7860_event_rotated_000.nxs,CNCS_7860_event_rotated_001.nxs,CNCS_7860_event_rotated_002.nxs,CNCS_7860_event_rotated_003.nxs,CNCS_7860_event_rotated_004.nxs',
                           OutputFilename=r'merged.nxs',OutputWorkspace='merged')
        self._saved_filenames.append(alg.getPropertyValue("OutputFilename"))

        # 5 times the number of events in the output workspace.
        self.assertDelta( mtd['merged'].getNPoints(), 553035, 1)

    def doValidation(self):
        # If we reach here, no validation failed
        return True

    def cleanup(self):
        for filename in self._saved_filenames:
            try:
                os.remove(filename)
                mtd.sendLogMessage("Removed %s" % filename)
            except OSError:
                mtd.sendLogMessage("Failed to remove %s" % filename)
            
