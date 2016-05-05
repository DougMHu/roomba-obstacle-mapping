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
	tmote_ID = repr(tmote_ID)
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
	"""Prints the average RSSI from tmote_ID"""
	if tmote_ID in tmotes:
		tmote_data = tmotes[tmote_ID]
		rssi = tmote_data["rssi"]
		print "RSSI list: ", rssi
		print
	else:
		print "tmote_ID does not exist"
		print

def sample_RSSI(sample_interval):
	"""Returns tmotes dictionary"""
	# Store dictionary of Tmote IDs
	tmotes = {}

	# Set timeout for how long to take samples
	#timeout = time.time() + sample_interval
	samples = sample_interval

	while (1):
		# Break if timeout
		#if time.time() > timeout:
		#	break
		#print tmotes.values()
		if ( len(tmotes.values()) > 0 ):
			
			if ( len(tmotes.values()[0]["rssi"]) >= samples ):
				break

		# read from Tmote serial output
		with open('/dev/ttyUSB0','r') as f:
			lines = f.read()
		print lines

		# parse different received Tmote IDs
		lines_list = lines.split("\n")
		#print lines_list
		for line in lines_list:
			line_list = line.split(",")
			if (len(line_list) == 2):
				data = line_list[1]
				data_list = data.split(" ")
				#print data_list
				data_list = [string.replace('\x00', '') for string in data_list]
				if (len(data_list) == 3):
					part1 = int(data_list[0])
					part2 = int(data_list[1])
					tmote_ID = (part1, part2)
					#print tmote_ID
					rssi = int(data_list[2])
					#print rssi
					update_tables(tmotes, tmote_ID, rssi)
					#print tmotes
					#print_tmote_data(tmotes, tmote_ID)

		time.sleep(2)

	# return tmotes dictionary
	return tmotes


# Open serial connection with USB port
#ser = serial.Serial('/dev/ttyUSB0')
#ser.parity = serial.PARITY_ODD # work around pyserial issue #30
#ser.parity = serial.PARITY_NONE
#ser.close()

def run_trial(locations):
	"""Returns locations list"""
	# Ask user for location coordinates
	print "Please enter distance:"
	d = input("d = ")
	print "You entered: ", d, " meters."
	print

	# Set sampling interval in seconds
	print "Please specify a number of samples:"
	sample_time = input("N = ")
	print "You entered: ", sample_time, " samples."
	print

	# Store RSSI samples into locations dictionary
	locations[d] = {}

	# Sample RSSI for one sampling interval
	tmotes = sample_RSSI(sample_time)

	# Store RSSI samples into locations dictionary
	location = locations[d]

	# Store rssi list for each tmote_ID
	for tmote_ID in tmotes.keys():
		location[tmote_ID] = tmotes[tmote_ID]["rssi"]

	# Return the RSSI samples
	print "Done!"
	print locations
	print
	return locations

def main():
	"""Runs multiple trials until user quits."""
	# Store RSSI samples for each distance in a dictionary
	locations = {}

	while (1):
		# Run trials
		locations = run_trial(locations)

		# Ask user if they want to repeat
		print "Would you like to run a new trial? [y/n]"
		response = raw_input("response: ")
		print "You said: ", response
		print

		# Break if user wants to quit
		if (response == "n"):
			break

	# Return trials
	return locations


if __name__ == "__main__":
	# logfile name
	# Try 1, 4, 8m
	logFile = "../calibrate_samples/Dougs_apt/ID_2_0/4m.json"

	print
	locations = main()

	# write outputs to a JSON file
	with open(logFile, "w") as f:
		json.dump(locations, f)

	# load JSON output
	with open(logFile, "r") as f: 
		dictionary = json.load(f)
		print dictionary

