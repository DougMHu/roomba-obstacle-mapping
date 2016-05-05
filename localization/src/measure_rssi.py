# Don't forget you can change the timeout timer!
# The locations dictionary is our map!

# Breakdown of data structures:
# Locations: (x, y) coordinate
#		Tmote_ID: (part1, part2)
#				RSSI: average RSSI received over timeout sec.

# Tmotes:	Tmote_IDs
#		RSSI: average value
#		RSSI_counter: # of rssi packets received

# NEXT STEPS:
# Ask user for new locations every time!
# When user types "quit", then print the map!

import time
import serial
import json

def update_tables(tmotes, tmote_ID, rssi):
	"""	Input:	current dictionary of tmotes,
				received tmote_ID
				received rssi
		Updates the tmotes data structure
	"""
	#tmote_ID = repr(tmote_ID)
	if tmote_ID in tmotes:
		tmote_data = tmotes[tmote_ID]
		tmote_data["rssi_counter"] += 1
		tmote_data["rssi"].append(rssi)
		#prev_rssi = tmote_data["rssi"]
		#count = tmote_data["rssi_counter"]
		#curr_rssi = rssi
		#tmote_data["rssi"] = (float(count-1)/count)*prev_rssi + (float(1)/count)*curr_rssi
	else:
		tmotes[tmote_ID] = {}
		tmote_data = tmotes[tmote_ID]
		tmote_data["rssi"] = [rssi]
		tmote_data["rssi_counter"] = 1

def print_tmote_data(tmotes, tmote_ID):
	"""Prints RSSI from tmote_ID"""
	if tmote_ID in tmotes:
		tmote_data = tmotes[tmote_ID]
		rssi = tmote_data["rssi"]
		print "RSSI list: ", rssi
		print
	else:
		print "tmote_ID does not exist"
		print

def parse_packet(line):
	""" Input: message in packet payload
		Returns:
	"""
	# Assumes message structure:
	# "Id & RSSI,%d %d %d\n"

	# If any part was unsuccessfully parsed, return None
	(tmote_ID, rssi) = (None, None)

	# Split the message
	line_list = line.split(",")
	if (len(line_list) == 2):
		data = line_list[1]
		data_list = data.split(" ")
		#print data_list
		data_list = [string.replace('\x00', '') for string in data_list]
		if (len(data_list) == 3):
			part1 = int(data_list[0])
			part2 = int(data_list[1])
			tmote_ID = "({},{})".format(part1,part2)
			#print tmote_ID
			if (len(data_list[2]) > 0):
				rssi = int(data_list[2])
				#print rssi
				#update_tables(tmotes, tmote_ID, rssi)
				#print tmotes
				#print_tmote_data(tmotes, tmote_ID)
	return (tmote_ID, rssi)

# Open serial connection with USB port
#ser = serial.Serial('/dev/ttyUSB0')
#ser.parity = serial.PARITY_ODD # work around pyserial issue #30
#ser.parity = serial.PARITY_NONE
#ser.close()

def sample_RSSI(sample_interval):
	"""Returns tmotes dictionary"""
	# Store dictionary of Tmote IDs
	tmotes = {}

	# Set timeout for how long to take samples
	timeout = time.time() + sample_interval

	while (1):
		# Break if timeout
		if time.time() > timeout:
			break

		# read from Tmote serial output
		with open('/dev/ttyUSB0','r') as f:
			lines = f.read()
		print lines

		# parse different received Tmote IDs
		lines_list = lines.split("\n")
		#print lines_list
		for line in lines_list:
			(tmote_ID, rssi) = parse_packet(line)
			if all((tmote_ID, rssi)):
				update_tables(tmotes, tmote_ID, rssi)

		# Wait to receive more broadcasts
		time.sleep(2)

	# return tmotes dictionary
	return tmotes

def run_trial(locations, sample_time):
	""" Input: 	locations dictionary to update
				duration to sample for
		Returns locations dictionary
	"""
	# Ask user for location coordinates
	print "Please enter your location coordinates:"
	x = input("x: ")
	y = input("y: ")
	loc = "({},{})".format(x,y)
	print "You entered: ", loc

	# Store RSSI samples into locations dictionary
	locations[loc] = {}

	# Sample RSSI for one sampling duration
	tmotes = sample_RSSI(sample_time)

	# Store RSSI samples into locations dictionary
	location = locations[loc]

	# Store rssi list for each tmote_ID
	for tmote_ID in tmotes.keys():
		location[tmote_ID] = tmotes[tmote_ID]["rssi"]

	# Return the RSSI samples
	print "Finished trial!"
	print locations
	print
	return locations

def main(sample_time):
	"""Runs multiple trials until user quits."""
	# Store RSSI samples for each location in a dictionary
	rssi_map = {}

	while (1):
		# Run trials
		rssi_map = run_trial(rssi_map, sample_time)

		# Ask user if they want to repeat
		print "Sample a new location? [y/n]"
		response = raw_input("response: ")
		print "You said: ", response
		print

		# Break if user wants to quit
		if (response == "n"):
			break

	# Return trials
	return rssi_map

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# BEFORE RUNNING SCRIPT:
#
#	Plug in a Tmote Sky, or else /dev/ttyUSB0 will not exist!
#
# 	Power on a Broadcasting Tmote Sky, or else the file read will block forever!
#
#	Open a Terminal and run:
#		$ cd ~/contiki/examples/rime/
#		$ sudo python
#		>>> import serial
#		>>> ser = serial.Serial('/dev/ttyUSB0')
#		>>> ser.close()
#		$ sudo make login
#		<Ctrl-C>
#
#	Then run the script!
#		$ cd ~/contiki/examples/rime/localization/src/
#		$ sudo python measure_rssi.py

if __name__ == "__main__":
	# logfile name
	logFile = "../location_experiments/Dougs_apt/test_3_3.json"

	# sampling duration
	sample_time = 120

	print
	locations = main(sample_time)

	# write outputs to a JSON file
	with open(logFile, "w") as f:
		json.dump(locations, f)

	# load JSON output
	with open(logFile, "r") as f: 
		dictionary = json.load(f)
		print dictionary