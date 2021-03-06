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
import sys
import os
import inspect

include_paths = ["../localization/src", "../mqtt", "../visualization"]
for path in include_paths:
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],path)))
	sys.path.insert(0, cmd_subfolder)
import trilateration
import turtle_roomba
import mqtt_paho_subscribe

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
		#print "reading remaining bytes = ", in_bytes
		connection.read(in_bytes)
		#print "Cleanup thread exiting..."

	def stream_sensors(self):
		global semaphore, connection
		# begin streaming
		print "Stream thread running..."
		sendCommandASCII('148 3 7 43 44')
		#print "Thread streaming..."
		while True:
			waitSec(0.01)   # a little faster than 15ms rate from Roomba
			if self.stopped():
				#print "Thread stopping stream..."
				# stop streaming and exit
				sendCommandASCII('150 0')
				print "Stream thread exiting..."
				break
			with semaphore:
				#print "Thread polling..."
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
			#print "valid update!"
			bump = (data1 > 0)
			curr_left_count = data2
			curr_right_count = data3
			if (bump):
				print "Bump detected! Thread killing itself..."
				sendCommandASCII('145 0 0 0 0')
				self.stop()

class Roomba(object):
	
	def __init__(self, length, width, step, location_sampling=False, sampler_type=None):
		# Used for roomba distance and rotation
		self.thread = None
		self.last_left_count = 0
		self.last_right_count = 0
		self.initEncoderCounts()
		self.orient = 0
		# Used to draw map using turtle graphics
		self.length = length
		self.width = width
		self.step = step
		self.turtle = turtle_roomba.CuteTurtle(width*0.001, length*0.001, step*0.001)
		# Used for sampling locations if necessary
		self.location_sampling = location_sampling
		if (location_sampling):
			if (sampler_type == 0):
				self.sampler = mqtt_paho_subscribe.mqtt_sampler()
			if (sampler_type == 1):
				self.sampler = trilateration.Tmote_Sampler(self)

	########################################
	# Turtle graphics commands
	########################################
	def keep_map_open(self):
		# return self.sampler.get_samples()
		return self.turtle.exit()

	########################################
	# GET SAMPLES TAKEN
	########################################
	def get_samples(self):
		return self.sampler.get_samples()

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
		obstacle = self.discover(self.step)#distance)
		#time.sleep(1)
		#self.sampler.take_sample()
		self.turtle.move(xylist, obstacle)
		return obstacle

	def redirect(self, new_orient):
		angle = 95
		sleep_time = 5
		if (self.orient - new_orient) % 4 == 0:
			self.orient = new_orient
			return
		elif (self.orient - new_orient) % 4 == 1:
			self.rotate(-angle,200)
			self.orient = new_orient
			if (self.location_sampling):
				self.sampler.take_sample()
			else:
				time.sleep(sleep_time)
			return
		elif (self.orient - new_orient) % 4 == 2:
			self.rotate(angle,200)
			self.rotate(angle,200)
			self.orient = new_orient
			if (self.location_sampling):
				self.sampler.take_sample()
			else:
				time.sleep(sleep_time)
			return
		else:
			self.rotate(angle,200)
			self.orient = new_orient
			if (self.location_sampling):
				self.sampler.take_sample()
			else:
				time.sleep(sleep_time)
			return

	def thread_wrapper(self, func, arg):
		# Cleanup port berfore reading measurements
		self.thread = StoppableThread(process="cleanup_stream")
		self.thread.start()
		self.thread.join()
		# Start collecting bump and distance measurements
		self.thread = StoppableThread()
		self.thread.start()
		try:
			waitSec(0.1)	# give Roomba some time to stream data to port
			ret_val = func(arg)
			self.thread.stop()
			self.thread.join()
			return ret_val
		except KeyboardInterrupt:
			print "Caught Ctrl-C"
			sendCommandASCII('145 0 0 0 0')
			print "Roomba stopped"
			self.thread.stop()
			print "Thread stopped"
			self.thread.join()
			print "Thread joined. Goodbye."
			sys.exit()

	def discover(self, distance):
		""""""
		sleep_time = 5
		# Cleanup port berfore reading measurements
		self.thread = StoppableThread(process="cleanup_stream")
		self.thread.start()
		self.thread.join()
		# Start collecting bump and distance measurements
		self.thread = StoppableThread()
		self.thread.start()
		try:
			waitSec(0.1)	# give Roomba some time to stream data to port
			# Initialize distance measurement
			dist_traveled = self.getRelativeDistance()
			#print "dist_traveled: {} mm".format(dist_traveled)
			# discover unkown territory
			obstacle = self.drive(distance, 200)
			if (obstacle):
				self.thread.join()
				print "thread joined :)"
				if (self.location_sampling):
					# call Estimote location function
					# Might block for a few seconds and do an average
					# then append it to the location list!
					#self.sampler.take_sample()
					pass
				self.retreat()
			else:
				self.thread.stop()
				self.thread.join()
				dist_traveled = self.getRelativeDistance()
				#print "distance = ", dist_traveled
		except KeyboardInterrupt:
			print "Caught Ctrl-C"
			sendCommandASCII('145 0 0 0 0')
			print "Roomba stopped"
			self.thread.stop()
			print "Thread stopped"
			self.thread.join()
			print "Thread joined. Goodbye."
			sys.exit()
		# return whether an obstacle was encountered
		time.sleep(sleep_time)
		return obstacle

	def retreat(self):
		# Take distance measurement
		dist_traveled = self.getRelativeDistance()
		#print "dist_traveled: {} mm".format(dist_traveled)
		# Travel the opposite distance
		self.drive(-dist_traveled, 200)


	def drive(self, distance, speed):
		"""Input: integer distance (mm), integer speed (mm/s)
		Sends appropriate serial command to Roomba"""
		# calculate time to execute drive command
		if (distance < 0):
			speed = -speed
		seconds = abs(float(distance)/speed)
		#print "seconds = ", seconds
		# create drive command
		cmd = struct.pack(">Bhh", 145, speed, speed)#-15)
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

	def rotate_threaded(self, angle):
		return self.thread_wrapper(self.rotate_feedback, angle)

	def rotate_feedback(self, angle):
		self.getRelativeAngle()
		speed = 200
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
		return 0

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
		#print "seconds = ", seconds
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
		#print "left_count = ", left_count
		#print "right count = ", right_count
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
			#print "left count = ", left_count
			#print "right count = ", right_count
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
		#print "left_distance = ", left_distance
		#print "right_distance = ", right_distance
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
			#print "Timeout!"
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
	roomba = Roomba(4000,4000,200, location_sampling=True, sampler_type=1)
	roomba.sampler.take_sample()
	print roomba.sampler.get_samples()
	# obstacle = roomba.discover(500)
	# print "obstacle = ", obstacle
	# roomba.rotate(-90,200)
	# obstacle = roomba.discover(500)
	# print "obstacle = ", obstacle
	# roomba.rotate(90,200)