# MIT License

# Copyright (c) 2016 Aashiq Ahmed, Shuai Chen, Meha Deora, Douglas Hu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import struct
import serial
import time
import threading
import math

import os
import inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"localization/src")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)
import trilateration

# Global variables
#port = raw_input("Enter port: ")
port = "/dev/ttyUSB1"
connection = serial.Serial(port, baudrate=115200, timeout=1)
semaphore = threading.BoundedSemaphore()
bump = False
obstacle = False
curr_left_count = 0
curr_right_count = 0

class StoppableThread(threading.Thread):
	"""Thread class with a stop() method. The thread itself has to check
	regularly for the stopped() condition."""

	def __init__(self, process="stream_sensors"):
		if (process == "cleanup_stream"):
			super(StoppableThread, self).__init__(target=self.cleanup_stream)
		else:
			super(StoppableThread, self).__init__(target=self.stream_sensors)
		self._stop = threading.Event()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def cleanup_stream(self):
		# clean up remaining bytes
		"Cleanup thread running..."
		in_bytes = connection.inWaiting()
		print "reading remaining bytes = ", in_bytes
		connection.read(in_bytes)
		print "Cleanup thread exiting..."

	def stream_sensors(self):
		global semaphore, connection
		# begin streaming
		print "Stream thread running..."
		sendCommandASCII('148 3 7 43 44')
		print "Thread streaming..."
		while True:
			waitSec(0.01)   # a little faster than 15ms rate from Roomba
			if self.stopped():
				print "Thread stopping stream..."
				# stop streaming and exit
				sendCommandASCII('150 0')
				print "Stream thread exiting..."
				break
			with semaphore:
				print "Thread polling..."
				self.poll_sensors()

	def poll_sensors(self):
		global bump, curr_left_count, curr_right_count
		bytes = [0 for x in range(9)]
		#print "in bytes = ", connection.inWaiting()
		(header, bytes[0]) = get8Unsigned()  # Should be 19, CHECK THIS!
		(N, bytes[1]) = get8Unsigned()
		(ID1, bytes[2]) = get8Unsigned()
		(data1, bytes[3]) = get8Unsigned()
		(ID2, bytes[4]) = get8Unsigned()
		(data2, bytes[5]) = get16Signed()
		(ID3, bytes[6]) = get8Unsigned()
		(data3, bytes[7]) = get16Signed()
		(checksum, bytes[8]) = get8Unsigned()
		if ((header == 19) and valid(bytes)):
			print "valid update!"
			bump = (data1 > 0)
			curr_left_count = data2
			curr_right_count = data3
			if (bump):
				print "Bump detected! Thread killing itself..."
				sendCommandASCII('145 0 0 0 0')
				self.stop()

class Roomba(object):
	
	def __init__(self):
		self.thread = None
		self.last_left_count = 0
		self.last_right_count = 0
		self.initEncoderCounts()
		self.orient = 0

	########################################
	# ROOMBA DRIVE COMMANDS
	########################################
	def move(self, xylist, distance):
		"""Input: 	xylist is list of tuples:
						src (tuple), dest (tuple)
					orient (0 - 3)
		ASSUMES: src and dest are only distance 1 away
		Moves Roomba from src to dest"""
		deltax = xylist[0][0]-xylist[1][0]
		deltay = xylist[0][1]-xylist[1][1]
		if deltax == 0:
			if deltay > 0:
				self.redirect(0)
			else:
				self.redirect(2)
		else:
			if deltax > 0:
				self.redirect(3)
			else:
				self.redirect(1)
		return self.discover(distance)

	def redirect(self, new_orient):
		if (self.orient - new_orient) % 4 == 0:
			self.orient = new_orient
			return
		elif (self.orient - new_orient) % 4 == 1:
			self.rotate(-90,200)
			self.orient = new_orient
			return
		elif (self.orient - new_orient) % 4 == 2:
			self.rotate(180,200)
			self.orient = new_orient
			return
		else:
			self.rotate(90,200)
			self.orient = new_orient
			return


	def discover(self, distance):
		""""""
		# Cleanup port berfore reading measurements
		self.thread = StoppableThread(process="cleanup_stream")
		self.thread.start()
		self.thread.join()
		# Start collecting bump and distance measurements
		self.thread = StoppableThread()
		self.thread.start()
		waitSec(0.1)	# give Roomba some time to stream data to port
		# Initialize distance measurement
		dist_traveled = self.getRelativeDistance()
		print "dist_traveled: {} mm".format(dist_traveled)
		# discover unkown territory
		#obstacle = self.drive(distance, 200)
		self.rotate_feedback(90,200)
		angle = self.getRelativeAngle()
		print "angle = ", angle
		obstacle = False
		if (obstacle):
			self.thread.join()
			print "thread joined :)"
			self.retreat()
		else:
			self.thread.stop()
			self.thread.join()
			print "distance = ", self.getRelativeDistance()
		# return whether an obstacle was encountered
		return obstacle

	def retreat(self):
		# Take distance measurement
		dist_traveled = self.getRelativeDistance()
		print "dist_traveled: {} mm".format(dist_traveled)
		# Travel the opposite distance
		self.drive(-dist_traveled, 200)


	def drive(self, distance, speed):
		"""Input: integer distance (mm), integer speed (mm/s)
		Sends appropriate serial command to Roomba"""
		# calculate time to execute drive command
		if (distance < 0):
			speed = -speed
		seconds = abs(float(distance)/speed)
		print "seconds = ", seconds
		# create drive command
		print
		print int(speed*0.905)
		print
		cmd = struct.pack(">Bhh", 145, speed, int(speed*0.905))
		sendCommandRaw(cmd)
		# wait for appropriate amount of time, or a bump. Then stop
		obstacle = wait_for_bump(seconds)
		if (obstacle):
			return True
			#print "Joining thread :)"
			#self.thread.join()
		else:
			sendCommandASCII('145 0 0 0 0')
			return False

	def rotate_feedback(self, angle, speed):
		#self.getRelativeAngle()
		total_angle = 0
		error = angle - total_angle
		while (abs(error) > 8):
			self.rotate(error*0.8, speed)
			curr_angle = self.getRelativeAngle()
			total_angle += curr_angle
			error = angle - total_angle
			print "\ntotal_angle = ", total_angle
			print "error = ", error
			print

	def rotate(self, angle, speed):
		"""Input: angle (degrees)"""
		if (angle < 0):
			speed = -speed
		# calculate time to execute drive command
		base_distance = 232 #248
		r = base_distance/2
		radians = angle*math.pi/180
		arc = radians*r
		seconds = abs(arc/speed)
		print "seconds = ", seconds
		# create drive command
		cmd = struct.pack(">Bhh", 145, speed, -speed)
		sendCommandRaw(cmd)
		# wait for appropriate amount of time, then stop
		waitSec(seconds)
		sendCommandASCII('145 0 0 0 0')

	########################################
	# SENSOR UPDATE AND RETRIEVAL
	########################################
	# Only call this once in the beginning right after connect
	def initEncoderCounts(self):
		# Make sure Roomba is in safe mode
		sendCommandASCII('128')
		sendCommandASCII('131')
		# Get Left and Right Encoder Counts (Packet ID #43, #44)
		(left_count, right_count) = self.getAbsoluteEncoderCounts()
		# Stores the absolute encoder count for later calculating relative counts
		self.last_left_count = left_count
		self.last_right_count = right_count

	# Read Left and Right Encoder Count packets (Packet ID #43, #44)
	# WaRnInG: DO NOT USE THIS AFTER STREAMING PACKETS
	def getAbsoluteEncoderCounts(self):
		# Get Left and Right Encoder Counts (Packet ID #43, #44)
		sendCommandASCII('142 43')
		(left_count, garbage) = get16Signed()
		sendCommandASCII('142 44')
		(right_count, garbage) = get16Signed()
		# Be CaReFuL! These counts wrap around outside of range: (-32768, 32767)
		print "left_count = ", left_count
		print "right count = ", right_count
		return (left_count, right_count)

	# Reads and returns the difference in Encoder Counts since the last call
	# NOTE: Calling this function WILL MODIFY the reference counts
	# i.e. last_left_count, last_right_count
	def getRelativeEncoderCounts(self):
		global semaphore, curr_left_count, curr_right_count
		# # Get Left and Right Encoder Counts (Packet ID #43, #44)
		# if ((left is None) and (right is None)):
		# 	(left_count, right_count) = self.getAbsoluteEncoderCounts()
		# else:
		# 	left_count = left
		# 	right_count = right
		with semaphore:
			left_count = curr_left_count
			right_count = curr_right_count
			print "left count = ", left_count
			print "right count = ", right_count
		# Return relative encoder counts
		relative_left_count = left_count - self.last_left_count
		relative_right_count = right_count - self.last_right_count
		# If overflow occurs:
		if ( relative_left_count > 32767 ):
			relative_left_count = relative_left_count - 65536
		if ( relative_left_count < -32767 ):
			relative_left_count = relative_left_count + 65536
		if ( relative_right_count > 32767 ):
			relative_right_count = relative_right_count - 65536
		if ( relative_right_count < -32767 ):
			relative_right_count = relative_right_count + 65536
		# Store new left and right counts
		self.last_left_count = left_count
		self.last_right_count = right_count
		return (relative_left_count, relative_right_count)

	# Returns the distance traveled since the last call to EITHER:
	#       getRelativeDistance() or getRelativeAngle()
	# ASSUMES: Roomba is purely translating in a straight line, NOT rotating
	def getRelativeDistance(self):
		# Convert relative counts into relative angle
		(left_count, right_count) = self.getRelativeEncoderCounts()
		# Convert to distances (mm) according to spec sheet
		left_distance = left_count * (math.pi*72.0) / 508.8
		right_distance = right_count * (math.pi*72.0) / 508.8
		# return the average to account for small differences between left and right
		print "left_distance = ", left_distance
		print "right_distance = ", right_distance
		return (left_distance + right_distance)/2

	# Returns the angle rotated since the last call to EITHER:
	#       getRelativeDistance() or getRelativeAngle()
	# ASSUMES Roomba is purely rotating in a circle, NOT translating
	def getRelativeAngle(self):
		# Convert relative counts into relative angle
		(left_count, right_count) = self.getRelativeEncoderCounts()
		# Convert to distances (mm) according to spec sheet
		left_distance = left_count * (math.pi*72.0) / 508.8
		right_distance = right_count * (math.pi*72.0) / 508.8
		# Convert to radians according to Section: Angle (Packet ID #20)
		base_distance = 232 #248
		radians = (right_distance - left_distance)/base_distance
		# Convert to degrees
		degrees = (radians * 360) / (2*math.pi)
		# Map to range (-180, 180)
		degrees = degrees % 360
		if (degrees > 180):
			degrees = degrees - 360
		return degrees

########################################
# SERIAL SEND FUNCTIONS
########################################
# sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
def sendCommandASCII(command):
	cmd = ""
	for v in command.split():
		cmd += chr(int(v))

	sendCommandRaw(cmd)

# sendCommandRaw takes a string interpreted as a byte array
def sendCommandRaw(command):
	global connection

	try:
		if connection is not None:
			connection.write(command)
		else:
			print "Not connected."
	except serial.SerialException:
		print "Lost connection"
		connection = None

########################################
# SERIAL RECEIVE FUNCTIONS
########################################
# getDecodedBytes returns a n-byte value decoded using a format string.
# Whether it blocks is based on how the connection was set up.
def getDecodedBytes(n, fmt, fmt2):
	"""fmt is for real data representation
	fmt2 should always be unsigned bytes in order to use for checksum"""
	global connection
	
	try:
		bytes = connection.read(n)
		return (struct.unpack(fmt, bytes)[0], struct.unpack(fmt2,bytes))
	except serial.SerialException:
		print "Lost connection"
		connection = None
		return None
	except struct.error:
		print "Got unexpected data from serial port."
		return None

# get8Unsigned returns an 8-bit unsigned value.
def get8Unsigned():
	return getDecodedBytes(1, "B", "B")

# get16Signed returns a 16-bit signed value.
def get16Signed():
	return getDecodedBytes(2, ">h", ">BB")

########################################
# MISC. HELPER FUNCTIONS
########################################
# wait for specified number of seconds
def waitSec(seconds):
	# Set timeout for when to return
	seconds = float(seconds)
	timeout = time.time() + seconds
	while (1):
		# Break if timeout
		if time.time() > timeout:
			break
		else:
			time.sleep(seconds/10)

def wait_for_bump(seconds):
	global semaphore, bump
	# Set timeout for when to return
	seconds = float(seconds)
	timeout = time.time() + seconds
	while (1):
		# Break if timeout
		if time.time() > timeout:
			print "Timeout!"
			return False
		else:
			with semaphore:
				if (bump):
					bump = False	# reset the bump flag
					return True
			time.sleep(seconds/10)

def valid(tuple_list):
	"""Returns True if checksum is correct. Returns False otherwise."""
	f = lambda x,y: x+y
	byte_sum = reduce(f, reduce(f, tuple_list))
	return ((byte_sum & 0xFF) == 0)

########################################
# MAIN
########################################
if __name__ == "__main__":
    roomba = Roomba()
    # obstacle = roomba.discover(500)
    # print "obstacle = ", obstacle
    # roomba.rotate(-90,200)
    # obstacle = roomba.discover(500)
    # print "obstacle = ", obstacle
    # roomba.rotate(90,200)
    #trilateration.main()
    angle = roomba.discover(0)
