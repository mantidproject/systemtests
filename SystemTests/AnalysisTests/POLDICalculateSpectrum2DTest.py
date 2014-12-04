import stresstesting
from mantid.simpleapi import *
import numpy as np

'''Checking results of POLDICalculateSpectrum2DTest.'''
class POLDICalculateSpectrum2DTest(stresstesting.MantidStressTest):
  def runTest(self):
    dataFiles = ["poldi2013n006904"]

    self.loadAndPrepareData(dataFiles)
    self.loadReferencePeakData(dataFiles)
    self.loadReferenceSpectrum(dataFiles)
    self.runCalculateSpectrum2D(dataFiles)
    self.analyseResults(dataFiles)

  def loadAndPrepareData(self, filenames):
    for dataFile in filenames:
      LoadSINQFile(Instrument='POLDI',Filename=dataFile + ".hdf",OutputWorkspace=dataFile)
      LoadInstrument(Workspace=dataFile, InstrumentName="POLDI", RewriteSpectraMap=True)
      PoldiTruncateData(InputWorkspace=dataFile, OutputWorkspace=dataFile)

  def loadReferencePeakData(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_2d_reference_Peaks.nxs" % (dataFile), OutputWorkspace="%s_reference_Peaks" % (dataFile))

  def loadReferenceSpectrum(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_2d_reference_Spectrum.nxs" % (dataFile), OutputWorkspace="%s_2d_reference_Spectrum" % (dataFile))

  def runCalculateSpectrum2D(self, filenames):
    for dataFile in filenames:
      PoldiCalculateSpectrum2D(InputWorkspace=dataFile,
                               PoldiPeakWorkspace="%s_reference_Peaks" % (dataFile),
                               PeakProfileFunction="Gaussian",
                               RefinedPoldiPeakWorkspace="%s_refined_Peaks" % (dataFile),
                               OutputWorkspace="%s_2d_calculated_Spectrum" % (dataFile))

  def analyseResults(self, filenames):
    for dataFile in filenames:
      calculatedSpectrum = mtd["%s_2d_calculated_Spectrum" % (dataFile)]
      referenceSpectrum = mtd["%s_2d_reference_Spectrum" % (dataFile)]

      self.assertEqual(calculatedSpectrum.getNumberHistograms(), referenceSpectrum.getNumberHistograms())

      for i in range(calculatedSpectrum.getNumberHistograms()):
        refHisto = referenceSpectrum.readY(i)
        calHisto = calculatedSpectrum.readY(i)

        absDiff = np.fabs(refHisto - calHisto)
        self.assertTrue(np.all(absDiff < 7e-4))
