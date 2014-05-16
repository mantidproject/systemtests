import stresstesting
from mantid.simpleapi import *
import numpy as np

'''Checking results of PoldiFitPeaks1D.'''
class POLDIFitPeaks1DTest(stresstesting.MantidStressTest):
  def runTest(self):
    dataFiles = ["poldi2013n006904"]

    self.loadReferenceCorrelationData(dataFiles)
    self.loadReferencePeakData(dataFiles)
    self.loadReferenceFitResults(dataFiles)
    self.runPeakSearch(dataFiles)
    self.runPoldiFitPeaks1D(dataFiles)
    self.analyseResults(dataFiles)

  def loadReferenceCorrelationData(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_reference.nxs" % (dataFile), OutputWorkspace=dataFile)

  def loadReferencePeakData(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_reference_Peaks.nxs" % (dataFile), OutputWorkspace="%s_reference_Peaks" % (dataFile))

  def runPeakSearch(self, filenames):
    for dataFile in filenames:
      PoldiPeakSearch(InputWorkspace=dataFile, OutputWorkspace="%s_Peaks" % (dataFile))

  def loadReferenceFitResults(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_reference_1DFit.nxs" % (dataFile), OutputWorkspace="%s_reference_1DFit" % (dataFile))

  def runPoldiFitPeaks1D(self, filenames):
      for dataFile in filenames:
          PoldiFitPeaks1D(InputWorkspace=dataFile,
                          FwhmMultiples=5,
                          PoldiPeakTable="%s_Peaks" % (dataFile),
                          OutputWorkspace="%s_Peaks_Refined" % (dataFile),
                          ResultTableWorkspace="%s_Results" % (dataFile),
                          FitCharacteristicsWorkspace="%s_FitData" % (dataFile),
                          FitPlotsWorkspace="%s_FitPlots" % (dataFile))

  # This test makes sure that:
  #  - standard deviations of position and relative fwhm are acceptably small (indicates reasonable fit)
  #  - refined peak positions are within one standard deviation of reference results obtained from existing program
  #  - fwhms do not deviate too much from reference results
  #  - currently, only the first 10 peaks are compared (as in the peak search test)
  def analyseResults(self, filenames):
    for dataFile in filenames:
      calculatedPeaks = mtd["%s_Peaks_Refined" % (dataFile)]
      referencePeaks = mtd["%s_reference_1DFit" % (dataFile)]
      self.assertEqual(calculatedPeaks.rowCount(), referencePeaks.rowCount())

      positions = calculatedPeaks.column(2)
      referencePositions = referencePeaks.column(0)

      fwhms = calculatedPeaks.column(4)
      referenceFwhms = referencePeaks.column(1)

      for i in range(10):
          # extract position and fwhm with uncertainties
          positionparts = positions[i].split()
          position = [float(positionparts[0]), float(positionparts[2])]

          fwhmparts = fwhms[i].split()
          fwhm = [float(fwhmparts[0]), float(fwhmparts[2])]

          self.assertTrue(self.positionAcceptable(position))
          self.assertTrue(self.fwhmAcceptable(fwhm))

          # find closest reference peak
          deltas = np.array([np.abs(position[0] - x) for x in referencePositions])

          self.assertDelta(deltas.min(), 0.0, 1e-4)
          minIndex = deltas.argmin()

          self.assertTrue(self.uncertainValueEqualsReference(position, referencePositions[minIndex], 1.0))
          self.assertDelta(fwhm[0], referenceFwhms[minIndex], 2e-4)

  def positionAcceptable(self, position):
    return position[1] < 1e-3

  def fwhmAcceptable(self, fwhm):
    return fwhm[1] < 3e-3

  def uncertainValueEqualsReference(self, value, reference, sigmas):
    return np.abs(value[0] - reference) < (sigmas * value[1])
