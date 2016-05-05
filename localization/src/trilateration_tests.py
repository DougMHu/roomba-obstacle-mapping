#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  trilateration.py
import setup
import math
import numpy
import json
import measure_rssi as measure
import analyze_calibration as analyze

def calc_r_sq(i_j,loc):
	""" i_j: list with x y
		loc: list with x0 y0
	"""
	return math.pow(i_j[0]-loc[0],2) + math.pow(i_j[1]-loc[1],2)

def calc_SE(estimate_list,actual_list):
	""" make sure input lists are of same size
	"""
	len_list=len(actual_list)
	total=0
	for i in range(0,len_list):
		total += math.pow(actual_list[i]-estimate_list[i],2)
	return math.sqrt(total/len_list)

def calc_xy(xlimits,ylimits,d1,d2,loc1,loc2):
	"""	xlimits: input list of room boundaries in x axis
		ylimits: input list of room boundaries in y axis
		d1 and d2: actual distance estimated using rssi
		loc1 and loc2: actual location of motes
		Returns:
	"""
	# make sure the locations are not the same
	if loc1 == loc2:
		print "Tmote locations cannot be the same!"
		return None
	min_ij=[0,0]
	minSE = float('inf')
	xlen = xlimits[1] - xlimits[0]
	ylen = ylimits[1] - ylimits[0]
	step = 0.1
	for i in numpy.linspace(xlimits[0],xlimits[1],num=int(xlen/step+1)):
		for j in numpy.linspace(ylimits[0],ylimits[1],num=int(ylen/step+1)):
			r1=math.sqrt(calc_r_sq([i,j],loc1))
			r2=math.sqrt(calc_r_sq([i,j],loc2))
			SE = calc_SE([r1,r2],[d1,d2])
			if SE <= minSE:
				minSE=SE
				min_ij=[i,j]
	#print "minSE = ",minSE, " at ",min_ij
	return (min_ij, minSE)

def main():
	print
	## Test calc_xy for edge cases:
	## d1 and d2 don't intersect
	#print "Edge case: don't intersect"
	#print "((x,y), minSE) = ", calc_xy([0,8],[0,8],3,3,[0,0],[0,8])
	#print
	## d1 and d2 intersect outside the map
	#print "Edge case: intersect outside the map"
	#print "((x,y), minSE) = ", calc_xy([0,8],[0,8],9,9,[0,0],[0,8])
	#print

	# call calc_xy 6 times, then average x,y coordinates
	# Assumes input dictionary, Tmotes:
	# keys:		Tmote_IDs
	# values:	dictionary
	#			keys: 		"rssi", "loc"
	#			values: 	list of RSSI measurements
	#						location of Tmote
	# Example Input
	# tmotes = {	"(192,168)": {"rssi":[-16,-15,-14],
	# 						  "loc": (0,0)
	# 						 } ,
	# 			"(172,11)":	 {"rssi":[-20,-15,-10],
	# 						  "loc": (8,0)
	# 						 },
	# 			"(1,289)":	 {"rssi":[-17,-15,-13],
	# 						  "loc": (0,8)
	# 						 },
	# 			"(0,10)":	 {"rssi":[-19,-15,-11],
	# 						  "loc": (8,8)
	# 						 }
	# 		 }

	# Define the boundaries of the room
	xlimits = (0,3.8)
	ylimits = (0,4.8)

	# Take RSSI measurements
	tmote_loc = { "(100,0)": (0,0),	
			  	  "(5,171)": (3.8,4.8),
			  	  "(2,0)": (0,4.8),
			  	  "(6,242)": (3.8,0)
				}

	# Hardcode locations of Tmotes:
	infile = "../location_experiments/Dougs_apt/test_2_2.json"
	with open(infile, "r") as f: 
		measurements = json.load(f)
	actual_loc = measurements.keys()[0]
	adict = measurements.values()[0]
	tmotes = {}
	for key in adict:
		tmotes[key] = {"rssi":adict[key]}

	for ID in tmote_loc:
		if ID in tmotes:
			tmotes[ID]["loc"] = tmote_loc[ID]

	# Convert median RSSI measurements to estimated distances using the Model
	# input: calibration measurements from 2 distances
	# file1 = ["../calibrate_samples/ID_100_0/1m.json", "../calibrate_samples/ID_131_215/1m.json",
	# 		 "../calibrate_samples/ID_251_122/1m.json", "../calibrate_samples/ID_2_0/1m.json"]
	# file2 = ["../calibrate_samples/ID_100_0/4m.json", "../calibrate_samples/ID_131_215/4m.json",
	# 		 "../calibrate_samples/ID_251_122/4m.json", "../calibrate_samples/ID_2_0/4m.json"]
	tmote_file1 = { "(100,0)": "../calibrate_samples/Dougs_apt/ID_100_0/1m.json",
				  	"(5,171)": "../calibrate_samples/Dougs_apt/ID_5_171/1m.json",
				  	"(2,0)": "../calibrate_samples/Dougs_apt/ID_2_0/1m.json",
				  	"(6,242)": "../calibrate_samples/Dougs_apt/ID_6_242/1m.json"
				  }
	tmote_file2 = { "(100,0)": "../calibrate_samples/Dougs_apt/ID_100_0/4m.json",
				  	"(5,171)": "../calibrate_samples/Dougs_apt/ID_5_171/4m.json",
				  	"(2,0)": "../calibrate_samples/Dougs_apt/ID_2_0/4m.json",
				  	"(6,242)": "../calibrate_samples/Dougs_apt/ID_6_242/4m.json"
				  }
	tmote_calib1 = {}
	tmote_calib2 = {}
	for ID in tmote_file1:
		tmote_calib1[ID] = analyze.extract_json(tmote_file1[ID])
	for ID in tmote_file2:
		tmote_calib2[ID] = analyze.extract_json(tmote_file2[ID])
	# extract1_list = [analyze.extract_json(infile) for infile in file1]
	# extract2_list = [analyze.extract_json(infile) for infile in file2]
	# dist1 = [x[0] for x in extract1_list]
	# rssi1_list = [x[1] for x in extract1_list]
	# dist2 = [x[0] for x in extract2_list]
	# rssi2_list = [x[1] for x in extract2_list]

	# Remove tmotes that do not belong to us
	tmote_set = set(tmotes)
	tmote_loc_set = set(tmote_loc)
	aliens = tmote_set - tmote_loc_set
	for alien in aliens:
		del tmotes[alien]

	# Estimate distances
	for ID in tmotes:
		if ID in tmote_loc:
			rssi_list = tmotes[ID]["rssi"]
			dist1, rssi1_list = tmote_calib1[ID]
			dist2, rssi2_list = tmote_calib2[ID]
			dist = analyze.calc_distance(dist1, dist2, rssi1_list, rssi2_list, rssi_list)
			tmotes[ID]["dist"] = dist
			print "distance from ", ID, " = ", dist

	# Create a set of Tmote IDs
	tmote_set = set(tmotes)

	# For every combination of tmotes, calculate x and y
	# store list of calculated (x,y)
	locations = []
	for i in range(len(tmote_set)):
		current_ID = tmote_set.pop()
		for remaining_ID in tmote_set:
			d1 = tmotes[current_ID]["dist"]
			d2 = tmotes[remaining_ID]["dist"]
			loc1 = tmotes[current_ID]["loc"]
			loc2 = tmotes[remaining_ID]["loc"]
			((x,y),minSE) = calc_xy(xlimits,ylimits,d1,d2,loc1,loc2)
			#print "minSE = ", minSE
			locations.append(numpy.array([x,y]))
	print
	print "location solutions = ", locations
	print

	xs = [elem[0] for elem in locations]
	ys = [elem[1] for elem in locations]

	# Average over all locations
	x ,y = sum(locations)/len(locations)
	print "actual location = ", actual_loc
	print
	print "estimated location = ", (x,y)
	print
	print "error = ", (int(actual_loc[1])-x)**2 + (int(actual_loc[3])-y)**2
	print
	print "x range: ", min(xs), " ", max(xs)
	print
	print "y range: ", min(ys), " ", max(ys)
	print
	return (x,y)

if __name__ == '__main__':
	main()

