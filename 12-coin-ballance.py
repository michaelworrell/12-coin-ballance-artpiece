# Python Code Imports
import csv
import pandas as pd
import numpy as npy
import math
import random
# Arduino Communication Imports
import serial


#################################################################################
#################################### Classes ####################################
#################################################################################


"""
Class that stores and modifies label and weight guess marker for a coin
"""
class Coin:
	# Initialize the coin object
	def __init__(self, label):
		self.marker = "Unmarked"
		self.label = label

	# Mark a coin object as being potentially lighter
	def markLighter(self):
		if self.marker == "Standard":
			return
		elif self.marker == "Heavier":
			self.marker = "Standard"
			return
		else:
			self.marker = "Lighter"
			return

	# Mark a coin object as being potentially heavier
	def markHeavier(self):
		if self.marker == "Standard":
			return
		elif self.marker == "Lighter":
			self.marker = "Standard"
			return
		else:
			self.marker = "Heavier"
			return

	# Mark a coin as having a standard weight
	def markStandard(self):
		self.marker = "Standard"


"""
Class that stores the information and functions that allow this code
to keep track of coin states, modify coin states, randomize which coins
are selected first for each guess, and whether the puzzle has been solved.
"""
class CoinPools:
	# Initializes the lists of coin pools
	def __init__(self, numCoins):
		self.unmarkedCoins = []
		for i in range(numCoins):
			newCoin = Coin(i + 1)
			self.unmarkedCoins.append(newCoin)
		self.lightCoins, self.heavyCoins, self.standardCoins = [], [], []

	# Get the lists of how coins are currently identified
	def getDistinctPools(self):
		return self.lightCoins, self.heavyCoins, self.unmarkedCoins, self.standarCoins

	# Return the number of coins in each list
	def getNumberInEachPool(self):
		return len(self.lightCoins), len(self.heavyCoins), len(self.unmarkedCoins), \
		len(self.standardCoins)

	# Retrieve some number of coins from the lighter coins list, and
	# removes them from said list.
	def retrieveFromLighter(self, num):
		toRetrieve = self.lightCoins[0:num]
		self.lightCoins = self.lightCoins[num:]
		return toRetrieve

	# Retrieve some number of coins from the heavier coins list, and
	# removes them from said list.
	def retrieveFromHeavier(self, num):
		toRetrieve = self.heavyCoins[0:num]
		self.heavyCoins = self.heavyCoins[num:]
		return toRetrieve

	# Retrieve some number of coins from the unmarked coins list, and
	# removes them from said list.
	def retrieveFromUnmarked(self, num):
		toRetrieve = self.unmarkedCoins[0:num]
		self.unmarkedCoins = self.unmarkedCoins[num:]
		return toRetrieve

	# Retrieve some number of coins from the standard coins list, and
	# removes them from said list.
	def retrieveFromStandard(self, num):
		toRetrieve = self.standardCoins[0:num]
		self.standardCoins = self.standardCoins[num:]
		return toRetrieve

	# Place coins present in an input list into their appropriate
	# lists withing this class based on marker.
	def distributeUnsorted(self, unsortedList):
		for i in range(len(unsortedList)):
			curCoin = unsortedList[i]
			if curCoin.marker == "Lighter":
				self.lightCoins.append(curCoin)
			elif curCoin.marker == "Heavier":
				self.heavyCoins.append(curCoin)
			elif curCoin.marker == "Unmarked":
				self.unmarkedCoins.append(curCoin)
			elif curCoin.marker == "Standard":
				self.standardCoins.append(curCoin)

	# Randomize the order of coins within each list
	def randomizePoolOrder(self):
		random.shuffle(self.lightCoins)
		random.shuffle(self.heavyCoins)
		random.shuffle(self.standardCoins)
		random.shuffle(self.unmarkedCoins)

	# Checks whether the target coin has been identified, or if
	# no valid solution exists based on user choices
	def isCoinIdentified(self):
		if len(self.heavyCoins) + len(self.lightCoins) <= 1:
			if len(self.unmarkedCoins) == 0:
				return True
		return False


"""
Class that stores and modifies informaiton about the state of the scale
"""
class Scale:
	# Initialize the scale object
	def __init__(self, numCoins):
		self.leftSide = []
		self.rightSide = []
		self.noSide = []
		# For all versions of the puzzle this program runs,
		# only 3 guesses are required.
		self.weighingsLeft = 3
		self.numEachSide = int(((3 ** (self.weighingsLeft - 1)) - 1) / 2)

	# Mark and / or eliminate coins, assuming the left side of the scale
	# has been proven to be heavier than the other side
	def leftHeavierMarkCoins(self):
		markedCoins = []
		while not len(self.leftSide) == 0:
			curCoin = self.leftSide.pop(0)
			curCoin.markHeavier()
			markedCoins.append(curCoin)
		while not len(self.rightSide) == 0:
			curCoin = self.rightSide.pop(0)
			curCoin.markLighter()
			markedCoins.append(curCoin)
		while not len(self.noSide) == 0:
			curCoin = self.noSide.pop(0)
			curCoin.markStandard()
			markedCoins.append(curCoin)
		return markedCoins

	# Mark and / or eliminate coins, assuming the right side of the scale
	# has been proven to be heavier than the other side
	def rightHeavierMarkCoins(self):
		markedCoins = []
		while not len(self.leftSide) == 0:
			curCoin = self.leftSide.pop(0)
			curCoin.markLighter()
			markedCoins.append(curCoin)
		while not len(self.rightSide) == 0:
			curCoin = self.rightSide.pop(0)
			curCoin.markHeavier()
			markedCoins.append(curCoin)
		while not len(self.noSide) == 0:
			curCoin = self.noSide.pop(0)
			curCoin.markStandard()
			markedCoins.append(curCoin)
		return markedCoins

	# Mark and / or eliminate coins, assuming the neither side of the scale
	# has been proven to be heavier than the other side
	def equalSidesMarkCoins(self):
		markedCoins = []
		while not len(self.leftSide) == 0:
			curCoin = self.leftSide.pop(0)
			curCoin.markStandard()
			markedCoins.append(curCoin)
		while not len(self.rightSide) == 0:
			curCoin = self.rightSide.pop(0)
			curCoin.markStandard()
			markedCoins.append(curCoin)
		markedCoins = markedCoins + self.noSide
		self.noSide = []
		return markedCoins

	# Mark all coins in the input lists as being heavier, or mark them as
	# standard if they are currently marked as lighter.
	def markAllHeavier(self, coinList):
		for i in range(len(coinList)):
			curCoin = coinList[i]
			curCoin.markHeavier()
			coinList[i] = curCoin
		return coinList

	# Mark all coins in the input lists as being Lighter, or mark them as
	# standard if they are currently marked as heavier.
	def markAllLighter(self, coinList):
		for i in range(len(coinList)):
			curCoin = coinList[i]
			curCoin.markLighter()
			coinList[i] = curCoin
		return coinList

	# Assigns new weights to the coins on the scale based on previous weighing
	def markSidesBasedOnWeighing(self, userResponse):
		markedCoins = []
		if userResponse == -1:
			markedCoins = self.leftHeavierMarkCoins()
		elif userResponse == 0:
			markedCoins = self.equalSidesMarkCoins()
		else:
			markedCoins = self.rightHeavierMarkCoins()
		return markedCoins


#################################################################################
################## Main decision making (puzzle solving) code  ##################
#################################################################################


"""
Determine which coins to place on which side of the scale, and which to
set aside, based on weight markers.
"""
def divideCoins(scale, coinPools):
	# Retrieve coins from the coin pools
	numLight, numHeavy, numUnmarked, numStandard = coinPools.getNumberInEachPool()
	numViable = numLight + numHeavy

	# Assign coins to sides of the scale, depending on whether all coins are
	# marked, and whether any standard coins has been identified.
	if numUnmarked == 0:
		# After First Weighing, all Coins Marked
		numPerSide = math.ceil(numViable / 3)
		numUnweighed = numViable - 2 * numPerSide

		# Add Light Coins if Appropriate
		lightPerSide = min(math.floor(numLight / 2), numPerSide)
		scale.leftSide = scale.leftSide + coinPools.retrieveFromLighter(lightPerSide)
		scale.rightSide = scale.rightSide + coinPools.retrieveFromLighter(lightPerSide)
		numLight -= lightPerSide
		numPerSide -= lightPerSide

		# Add Heavy Coins if Appropriate
		heavyPerSide = min(math.floor(numHeavy / 2), numPerSide)
		scale.leftSide = scale.leftSide + coinPools.retrieveFromHeavier(heavyPerSide)
		scale.rightSide = scale.rightSide + coinPools.retrieveFromHeavier(heavyPerSide)
		numHeavy -= heavyPerSide
		numPerSide -= heavyPerSide

		# Add Heavy and Standard Coin to Scale if Appropriate
		scale.leftSide = scale.leftSide + coinPools.retrieveFromHeavier(numPerSide)
		scale.rightSide = scale.rightSide + coinPools.retrieveFromStandard(numPerSide)

		# Add any coins remaining To No Side of Scale
		scale.noSide = scale.noSide + coinPools.retrieveFromHeavier(numHeavy)
		scale.noSide = scale.noSide + coinPools.retrieveFromLighter(numLight)
	elif numStandard != 0:
		# After First Weighing, Unmarked Coins Remaining
		numUnweighed = math.floor(numUnmarked / 3)
		numPerSide = numUnmarked - numUnweighed

		# Side sides of scale
		scale.leftSide = coinPools.retrieveFromUnmarked(numPerSide)
		scale.rightSide = coinPools.retrieveFromStandard(numPerSide)
		scale.noSide = coinPools.retrieveFromUnmarked(numUnweighed)
	else:
		# First Weighing Only
		numPerSide = math.ceil(numUnmarked / 3)
		numUnweighed = numUnmarked - 2 * numPerSide

		# Set sides of scale
		scale.leftSide = coinPools.retrieveFromUnmarked(numPerSide)
		scale.rightSide = coinPools.retrieveFromUnmarked(numPerSide)
		scale.noSide = coinPools.retrieveFromUnmarked(numUnweighed)

	# Return the scale and coin pools
	return scale, coinPools


#################################################################################
################## ------------------------------------------- ##################
#################################################################################


"""
Runs the puzzle based on mode specified by the user

For more general information on the puzzle and mechanics,
check out the below wikipedia link:
https://en.wikipedia.org/wiki/Balance_puzzle

IsRandom causes exact choices made by the program to change between runs of
this program, while still being capable of solving each problem.

If runningMode is coinLighter, program knows that off coin is lighter.
If runningMode is coinHeavier, program knows that off coin is heavier.
If runningMode is coinUnknown, program knows that off coin is different,
but not whether the coin is heavier or lighter specifically.
"""
def coinsAndScale(numCoins, isRandom, runningMode, ser):
	# Initialization
	myCoinPools = CoinPools(numCoins)
	myScale = Scale(numCoins)
	w = myScale.weighingsLeft

	# Sets number of guesses (Arduino)
	numGuessesByteArray = (myScale.weighingsLeft).to_bytes(1, byteorder='big')
	testValuesArray = (0).to_bytes(1, byteorder='big')

	# Handle weighings until at most a single marked coin remains, or
	# until the problem is no longer solvable
	while not myCoinPools.isCoinIdentified():
		# Randomize the pool order (if specified)
		if isRandom:
			myCoinPools.randomizePoolOrder() # Shuffle Line

		# Assign coins to sides on the scale
		myScale, myCoinPools = divideCoins(myScale, myCoinPools)

		# Converts state of the scale into a 3-byte packet to give the Arduino
		outputResults = scaleStateToBytes(myScale)

		# Send guess and scale information to the Arduino
		combinedArray = [0] * (len(numGuessesByteArray) + len(outputResults))
		combinedArray[0] = numGuessesByteArray[0]
		combinedArray[1:] = outputResults[0:]
		pythonToArduino(combinedArray, ser)

		# Wait for User Response to Weighing from the Arduino
		userButton = arduinoToPython(1, ser)
		userResponse = userButton[0] - 1

		# Reduce number of weighings by 1
		myScale.weighingsLeft -= 1
		numGuessesByteArray = (myScale.weighingsLeft).to_bytes(1, byteorder='big')

		# Change Coin Pool and Scale based on User Response
		unsortedCoins = myScale.markSidesBasedOnWeighing(userResponse)

		# Handle cases where weight of the coin is known by the program
		if (runningMode == "coinLighter"):
			unsortedCoins = myScale.markAllLighter(unsortedCoins)
		elif (runningMode == "coinHeavier"):
			unsortedCoins = myScale.markAllHeavier(unsortedCoins)

		# Distribute coins to their respective lists in CoinPools object
		myCoinPools.distributeUnsorted(unsortedCoins)

	# Communicate Final Results to the Arduino
	if (len(myCoinPools.lightCoins) == 1):
		# Final coin identified, and it is lighter than the other coins.
		finalResultList = myCoinPools.lightCoins
		finalResult = finalResultList[0]
		outputResults = finalCoinToBytes(finalResult.label - 1)

		# Send to the Arduino
		combinedArray = [0] * (len(numGuessesByteArray) + len(outputResults))
		combinedArray[0] = numGuessesByteArray[0]
		combinedArray[1:] = outputResults[0:]
		pythonToArduino(combinedArray, ser)
	elif (len(myCoinPools.heavyCoins) == 1):
		# Final coin identified, and it is lighter than the other coins.
		finalResultList = myCoinPools.heavyCoins
		finalResult = finalResultList[0]
		outputResults = finalCoinToBytes(finalResult.label - 1)

		# Send to the Arduino
		combinedArray = [0] * (len(numGuessesByteArray) + len(outputResults))
		combinedArray[0] = numGuessesByteArray[0]
		combinedArray[1:] = outputResults[0:]
		pythonToArduino(combinedArray, ser)
	else:
		# No valid solution exists.
		outputResults = finalCoinToBytes(-1)
		# Send to the Arduino
		combinedArray[0] = numGuessesByteArray[0]
		combinedArray[1:] = outputResults[0:]
		pythonToArduino(combinedArray, ser)

	# Ends the run
	return


#################################################################################
######################## Arduino Communication Functions ########################
#################################################################################


"""
Establishes contact between the servo and the arduino.
"""
def establishContact():
	# String below is whatever port appears in "Tools, Ports" in the
	# Arduino software.
	ser = serial.Serial('/dev/cu.SLAB_USBtoUART', 9600)
	ser.read(1)
	return ser


"""
Reads a number of consecutive bytes from the Arduino and stores
them as an array of bytes.
"""
def arduinoToPython(numBytesToRead, ser):
	#  Initialization
	NUM_BYTES_TO_READ = numBytesToRead
	outputResults = [0] * NUM_BYTES_TO_READ

	# Calling read will block the prgram until appropriate number
	# of bytes can be and has been read
	arduinoValues = ser.read(NUM_BYTES_TO_READ)

	# Format and return results from the Arduino
	for i in range(NUM_BYTES_TO_READ):
		outputResults[i] = arduinoValues[i]
	return outputResults


"""
Takes an array of bytes and writes them to the Arduino.
"""
def pythonToArduino(outputResults, ser):
	# Initialization
	OUTPUT_QUEUE_SIZE = 64
	numBytesToWrite = len(outputResults)

	# Returns false if unable to write to the arduino
	if ser.out_waiting > OUTPUT_QUEUE_SIZE - numBytesToWrite:
		return False

	# Writes outputResults to the arduino
	ser.write(outputResults)
	return True


#################################################################################
################## Convert Between Arduino and Python Messages ##################
#################################################################################


"""
Converts the state of the scale into a 3 byte informational packet
that is capable of being sent to the arduino directly.
"""
def scaleStateToBytes(myScale):
	# Default
	NUM_BYTES_TO_WRITE = 3
	NUM_BALLS = 12;

	# Convert scale state to a three byte integer
	bothSidesResult = 0

	# Add to result using the left side of the scale
	itemsToAssign = myScale.leftSide
	for i in range(len(itemsToAssign)):
		coin = itemsToAssign[i]
		resultIndex = coin.label - 1
		bothSidesResult += (2 ** resultIndex)

	# Add to result using the right side of the scale
	itemsToAssign = myScale.rightSide
	for i in range(len(itemsToAssign)):
		coin = itemsToAssign[i]
		resultIndex = coin.label - 1
		bothSidesResult += (2 ** (resultIndex + NUM_BALLS))

	# Formats state of the scale into byte sized information
	outputResults = [(0).to_bytes(1, byteorder='big')] * NUM_BYTES_TO_WRITE

	# Store information in byte array, then return said byte array
	scaleByteArray = (bothSidesResult).to_bytes(3, byteorder='big')

	# Removing this code segment breaks the code, for some reason
	for i in range(NUM_BYTES_TO_WRITE):
		outputResults[i] = scaleByteArray[NUM_BYTES_TO_WRITE - i - 1]

	return scaleByteArray


"""
Converts the final result into a 3 byte informational packet
that is capable of being sent to the arduino directly.
"""
def finalCoinToBytes(resultIndex):
	# Default values
	NUM_BYTES_TO_WRITE = 3
	NUM_BALLS = 12; # TODO FIX THIS LATER

	bothSidesResult = 0
	if resultIndex >= 0:
		# Convert coin index information to a three byte integer
		# on both sides of the scale
		bothSidesResult = (2 ** resultIndex)
		bothSidesResult += (2 ** (resultIndex + NUM_BALLS))
	else:
		# Mark all lights as active when no valid solution exists
		bothSidesResult = (2 ** 24)
		bothSidesResult -= 1

	# Formats state of the scale into byte sized information
	outputResults = [(0).to_bytes(1, byteorder='big')] * NUM_BYTES_TO_WRITE

	# Store information in byte array, then return said byte array
	trippleByteArray = (bothSidesResult).to_bytes(3, byteorder='big')

	# removing this code segment breaks the code, for some reason
	for i in range(NUM_BYTES_TO_WRITE):
		outputResults[i] = trippleByteArray[NUM_BYTES_TO_WRITE - i - 1]

	return trippleByteArray


#################################################################################
############################### Main program loop ###############################
#################################################################################


"""
Main Python Code Loop
"""
if __name__ == "__main__":
	# Setup communication with the Arduino
	ser = establishContact()

	# Continually loops through the code (just like the Arduino does)
	while (True):
		# Get mode to run fron the Arduino
		modeToRun = arduinoToPython(1, ser)

		# Set mode based on arduino response
		if (modeToRun[0] == 1):
			runningMode = "coinLighter"
		elif (modeToRun[0] == 2):
			runningMode = "coinUnknown"
		elif (modeToRun[0] == 3):
			runningMode = "coinHeavier"

		# Problem specific setup
		numCoins = 12
		isRandom = True
		# Run the puzzle code until completed
		coinsAndScale(numCoins, isRandom, runningMode, ser)
