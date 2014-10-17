import stresstesting
import os
import re
from mantid.simpleapi import *
from mantid.geometry import *

'''Check that the space groups generated by Mantid are correct.'''
class SpaceGroupFactoryTest(stresstesting.MantidStressTest):
  def runTest(self):
    self.spaceGroupData = self.loadReferenceData()

    availableSpaceGroups = SpaceGroupFactoryImpl.Instance().allSubscribedSpaceGroupSymbols()

    for symbol in availableSpaceGroups:
      self.checkSpaceGroup(symbol)

  def checkSpaceGroup(self, symbol):
    group = SpaceGroupFactoryImpl.Instance().createSpaceGroup(symbol)

    groupOperations = set(group.getSymmetryOperationStrings())
    referenceOperations = self.spaceGroupData[group.number()]

    differenceOne = groupOperations - referenceOperations
    differenceTwo = referenceOperations - groupOperations

    self.assertTrue(len(differenceOne) == 0, "Problem in space group " + str(group.number()) + " (" + symbol + ")")
    self.assertTrue(len(differenceTwo) == 0, "Problem in space group " + str(group.number()) + " (" + symbol + ")")
    self.assertTrue(groupOperations == referenceOperations, "Problem in space group " + str(group.number()) + " (" + symbol + ")")

  def loadReferenceData(self):
    # Reference data.
    # Dictionary has a string set for each space group number.
    separatorMatcher = re.compile("(\d+)")

    fileName = os.path.join(os.path.dirname(__file__), 'ReferenceResults','SpaceGroupSymmetryOperations.txt')

    print fileName

    fileHandle = open(fileName, 'r')
    spaceGroups = {}
    currentGroup = 0
    for currentLine in fileHandle:
      matchedSeparator = separatorMatcher.match(currentLine)

      if matchedSeparator is not None:
        currentGroup = int(matchedSeparator.group(1))
        spaceGroups[currentGroup] = set()
      else:
        spaceGroups[currentGroup].add(currentLine.strip().replace(" ", ""))

    return spaceGroups

