import setup
import json
from scipy.stats import binom

def extract_json(infile):
	"""Returns distance and RSSI measurements as tuple"""
	# Load JSON output
	with open(infile, "r") as f: 
		data = json.load(f)

	# Extract data
	dist = float(data.keys()[0])
	adict = data.values()[0]
	rssi_list = adict.values()[0]

	return (dist,rssi_list)

def calc_distance(dist1, dist2, rssi1_list, rssi2_list, rssi_list):
	""" Input:	file1 and file2 are calibration RSSI data from 2 different distances
			  	rssi_list are measurements to be converted to distance based on calibrated model
		Returns: estimated distance 
	"""
	# Extract calibration files
	#dist1, rssi1_list = extract_json(file1)
	#dist2, rssi2_list = extract_json(file2)

	# Calculate median RSSI
	rssi1_median = setup.calc_median(rssi1_list)
	rssi2_median = setup.calc_median(rssi2_list)
	# print "rssi1_median = ", rssi1_median
	# print "rssi2_median = ", rssi2_median

	# Calculate n & A
	n, A = setup.calc_const(rssi1_median, rssi2_median, dist1, dist2)
	# print "(n, A) = ", (n,A)

	# Estimate the distance given rssi_list
	rssi_median = setup.calc_median(rssi_list)
	dist_estimate = setup.calc_distance(n, A, rssi_median)

	return dist_estimate

def main():
	### This script:
	###		- calculates n (path loss exponent) and A (system loss) for the
	###			Receive power - to - distance model:
	###			R = -10*n (log(d)) + A
	###		- estimates distance given an RSSI measurement from a location
	###			(works best when interpolating location, not extrapolating)
	###		- provides 95% confidence intervals, assuming 100 samples
	###			and median averaging

	# File input
	print
	file1 = "../calibrate_samples/ID_100_0/1m.json"	# file1 and file2 are used to calculate
	file2 = "../calibrate_samples/ID_100_0/4m.json"	# n and A for our model
	file3 = "../samples1/experiment1.json"	# file3 provides the "unkown" RSSI measurement
	print "file1: ", file1			# to estimate
	print "file2: ", file2
	print

	# Load JSON output
	with open(file1, "r") as f: 
		data1 = json.load(f)
	with open(file2, "r") as f: 
		data2 = json.load(f)
	with open(file3, "r") as f: 
		data3 = json.load(f)

	# Extract lists
	dist1 = float(data1.keys()[0])
	dict1 = data1.values()[0]
	rssi1_list = dict1.values()[0]

	dist2 = float(data2.keys()[0])
	dict2 = data2.values()[0]
	rssi2_list = dict2.values()[0]

	dist3 = float(data3.keys()[0])
	dict3 = data3.values()[0]
	rssi3_list = dict3.values()[0]

	# Calculate median RSSI with 95% Confidence Interval (for N=100)
	rssi1_median = setup.calc_median(rssi1_list)
	rssi1_list = sorted(rssi1_list)
	rssi1_LBE = rssi1_list[40]
	rssi1_UBE = rssi1_list[59]

	rssi2_median = setup.calc_median(rssi2_list)
	rssi2_list = sorted(rssi2_list)
	rssi2_LBE = rssi2_list[40]
	rssi2_UBE = rssi2_list[59]

	print "median 1 = ", rssi1_median, " ", (rssi1_LBE, rssi1_UBE)
	print "median 2 = ", rssi2_median, " ", (rssi2_LBE, rssi2_UBE)
	print

	# Calculate n & A
	const_list = setup.calc_const(rssi1_median, rssi2_median, dist1, dist2)
	const_LBE_list = setup.calc_const(rssi1_LBE, rssi2_LBE, dist1, dist2)
	const_UBE_list = setup.calc_const(rssi1_UBE, rssi2_UBE, dist1, dist2)
	print "constants: ", const_list
	print (const_LBE_list[0], const_UBE_list[0]), (const_LBE_list[1], const_UBE_list[1])
	print

	# Estimate what we think the true distance is...
	# find median of file3
	rssi3_median = setup.calc_median(rssi3_list)
	rssi3_list = sorted(rssi3_list)
	rssi3_LBE = rssi3_list[40]
	rssi3_UBE = rssi3_list[59]
	print "median 3 = ", rssi3_median, " ", (rssi3_LBE, rssi3_UBE)
	print

	# caculate estimated distance
	dist3_estimate = []
	dist3_UBE = []
	dist3_LBE = []

	constants = const_list
	dist3_estimate.append(setup.calc_distance(constants[0], constants[1], rssi3_median))
	dist3_UBE.append(setup.calc_distance(constants[0], constants[1], rssi3_LBE))
	dist3_LBE.append(setup.calc_distance(constants[0], constants[1], rssi3_UBE))

	constants = const_LBE_list
	dist3_estimate.append(setup.calc_distance(constants[0], constants[1], rssi3_median))
	dist3_UBE.append(setup.calc_distance(constants[0], constants[1], rssi3_LBE))
	dist3_LBE.append(setup.calc_distance(constants[0], constants[1], rssi3_UBE))

	constants = const_UBE_list
	dist3_estimate.append(setup.calc_distance(constants[0], constants[1], rssi3_median))
	dist3_UBE.append(setup.calc_distance(constants[0], constants[1], rssi3_LBE))
	dist3_LBE.append(setup.calc_distance(constants[0], constants[1], rssi3_UBE))

	print "true distance = ", dist3
	print "est. distance = ", dist3_estimate[0], " ", (min(dist3_LBE), max(dist3_UBE))
	print

if __name__ == '__main__':
	main()
