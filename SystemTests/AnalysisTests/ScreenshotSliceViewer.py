"""System test that takes a screenshot
of a GUI element and posts it to the WIKI"""

import stresstesting
from mantidsimple import *
from PyQt4 import Qt



class ScreenshotSliceViewer(stresstesting.MantidScreenshotTest):
 

    def runTest(self):
        """ Set up and create a SliceViewer widget """
        CreateWorkspace('workspace2d', '1,2,3', '2,3,4')
        
        # TODO: Finish this "test" and re-enable
        #return
        
        import mantidqtpython
        
        # Create the application
        app = Qt.QApplication(sys.argv)

        # Create a test data set
        CreateMDWorkspace(Dimensions='3',Extents='0,10,0,10,0,10',Names='x,y,z', 
            Units='m,m,m',SplitInto='5',SplitThreshold=100, MaxRecursionDepth='20',OutputWorkspace='mdw')
        FakeMDEventData("mdw",  UniformParams="1e4")
        FakeMDEventData("mdw",  PeakParams="1e3, 1, 2, 3, 1.0")
        BinMD("mdw", "uniform",  AxisAligned=1, AlignedDimX="x,0,10,30",  AlignedDimY="y,0,10,30",  AlignedDimZ="z,0,10,30", IterateEvents="1", Parallel="0")

        # Get the factory to create the SliceViewerWindow in C++
        svw = mantidqtpython.WidgetFactory.Instance().createSliceViewerWindow("uniform", "")
        svw.show()
        
        # Grab a screenshot
        pix = Qt.QPixmap.grabWidget(svw)
        # Save to file
        self.uploadScreenshot(pix, "ScreenshotSliceViewer")
        
        # Now delete the widget        
        svw.deleteLater()
        # Timer to exit the app immediately after opening
        Qt.QTimer.singleShot(0, app, Qt.SLOT("closeAllWindows()"))
        # This is required for deleteLater() to do anything (it deletes at the next event loop
        app.exec_()

