"""System test that takes a screenshot
of a GUI element and posts it to the WIKI"""

import stresstesting
from mantidsimple import *
from PyQt4 import Qt

import mwclient
import datetime

     
#======================================================================
def replace_section_text(contents, section, newtext):
    """ Search WIKI text to find a section text there.
    Sections start with 3 equals (===).
    Then, the contents of that section are replaced 
    
    @param contents :: string of the entire wiki page
    @param section :: string giving the text of the section
    @param newtext :: replacement contents of that section.
    @return the new contents of the entire page """
    
    lines = contents.splitlines()
    
    sections = dict()
    
    output = ""
    current_section = ""
    
    # Find the text in each section
    for line in lines:
        line_mod = line.replace(" ", "")
        # What section are we in?
        if line_mod.startswith("==="):
            current_section = line_mod[3:-3]
            print "Starting section %s"% current_section
        else:
            if not sections.has_key(current_section):
                 sections[current_section] = ""
            sections[current_section] += line + "\n"
    
    sections[section] = newtext
    
    # Make the output
    items = sections.items()
    items.sort()
    for (section_name, text) in items:
        output += "=== %s ===\n" % section_name
        output += text
    
    print output
    # Return the total text
    return output
    

class ScreenshotSliceViewer(stresstesting.MantidStressTest):
    
    def uploadScreenshot(self, pix, basename):
        """Save and upload the screenshot
        @param pix :: QPixmap with the screenshot
        @param basename :: base name of the screenshot file """
        
        env = stresstesting.envAsString()
        filename = "%s.%s.png" % (basename, env)
        pix.save("ScreenshotSliceViewer.%s.png" % env)
        
        # Init site object
        print "Connecting to site mantidproject.org"
        site = mwclient.Site('www.mantidproject.org', path='/')
        print "Logging in"
        site.login("Janik Zikovsky", "a9wrua4mvw")
        
        # Upload the screenshot
        print "Uploading %s" % filename
        f = open(filename, 'r')
        now = str(datetime.datetime.now())
        desc = "Screenshot for %s test taken on platform %s on %s" % (basename, env, now)
        site.upload(file=f, filename=filename, description=desc )
        f.close()
        
        # Modify the section in the wiki page
        print "Modifying Wiki page"
        page = site.Pages["SystemTests.%s" % basename]
        contents = page.edit()
        section = env
        section_text = """
Screenshot of %s taken on platform %s, on date: %s.

[[Image:%s|%s]]
""" % (basename, env, now, filename, desc)
        # This modifies the section
        newcontents = replace_section_text(contents, section, section_text)
        
        # Save the contents
        page.save(newcontents, summary="System tests - updating section %s" % section) 
    


    def runTest(self):
        """ Set up and create a SliceViewer widget """
        CreateWorkspace('workspace2d', '1,2,3', '2,3,4')
        
        # TODO: Finish this "test" and re-enable
        return
        
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
        #app.exec_()
        pass

    def validateMethod(self):
        return "ValidateWorkspaceToWorkspace"

    def validate(self):
        return ('workspace2d','workspace2d')
