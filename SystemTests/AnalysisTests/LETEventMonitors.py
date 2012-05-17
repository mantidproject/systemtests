"""Simply tests that the LET files can have their monitors loaded as events
The files are too big for a unit test
"""
import stresstesting
from mantidsimple import Load, mtd, EventWorkspace
import math

class LETEventMonitors(stresstesting.MantidStressTest):
    
  success = False

  def requiredMemoryMB(self):
    return 300

  def runTest(self):
    filename = 'LET00006278.nxs'
    outputws = 'LET00006278'
    monitor_ws = 'LET00006278_monitors'
    Load(Filename=filename, OutputWorkspace=outputws, 
         LoadMonitors=True, MonitorsAsEvents=True)
    if not mtd.workspaceExists(outputws):
      raise RuntimeError("Main LET workspace does not exist")

    if not mtd.workspaceExists(monitor_ws):
      raise RuntimeError("Monitors LET workspace does not exist")
    
    monitors = mtd[monitor_ws]
    if type(monitors._getHeldObject()) != EventWorkspace:
      raise RuntimeError("Monitor WS is not an event WS!")

    # Check values in main WS
    data = mtd[outputws]
    y0 = data.readY(0)[0]
    expectedY0 = 1.0
    y4 = data.readY(4)[0]
    expectedY4 = 29.0
    if math.fabs(y0 - expectedY0) > 1e-12:
      raise RuntimeError("Y0 count is not what was expected in main data WS: %f != %f" % (y0, expectedY0))
    if math.fabs(y4 - expectedY4) > 1e-12:
      raise RuntimeError("Y4 count is not what was expected in main data WS: %f != %f" % (y4, expectedY4))

    # Check values in monitors
    y0 = monitors.readY(0)[0]
    expectedY0 = 4002922.0
    y5 = monitors.readY(5)[0]
    expectedY5 = 666495.0
    if math.fabs(y0 - expectedY0) > 1e-12:
      raise RuntimeError("Y0 count is not what was expected in monitor WS: %f != %f" % (y0, expectedY0))
    if math.fabs(y5 - expectedY5) > 1e-12:
      raise RuntimeError("Y5 count is not what was expected in monitor WS: %f != %f" % (y5, expectedY5))

    # Fine here
    self.success = True

  def validate(self):
    return self.success
