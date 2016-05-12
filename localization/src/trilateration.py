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
import time

# Output file names
outfile1 = "/home/douglamh/Documents/final_project/localization/location_experiments/Dougs_apt/measure_test_1_1.json"
outfile2 = "/home/douglamh/Documents/final_project/localization/location_experiments/Dougs_apt/trilaterate_test_1_1.json"

# Define the boundaries of the room
xlim = (0,3.8)
ylim = (0,4.8)

# Take RSSI measurements
tmote_loc = { "(100,0)": (0,0),	
		  	  "(5,171)": (3.8,4.8),
		  	  "(2,0)": (0,4.8),
		  	  "(6,242)": (3.8,0)
			}

# Input calibration files
tmote_file1 = { "(100,0)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_100_0/1m.json",
			  	"(5,171)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_5_171/1m.json",
			  	"(2,0)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_2_0/1m.json",
			  	"(6,242)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_6_242/1m.json"
			  }
tmote_file2 = { "(100,0)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_100_0/4m.json",
			  	"(5,171)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_5_171/4m.json",
			  	"(2,0)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_2_0/4m.json",
			  	"(6,242)": "/home/douglamh/Documents/final_project/localization/calibrate_samples/Dougs_apt/ID_6_242/4m.json" }

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

def trilaterate(tmotes):
	print "tmotes = ", tmotes
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

	global xlim, ylim, tmote_loc, tmote_file1, tmote_file2, outfile1, outfile2

	# Hardcode locations of Tmotes and write to file:
	for ID in tmote_loc:
		if ID in tmotes:
			tmotes[ID]["loc"] = tmote_loc[ID]
	with open(outfile1, "w") as f:
		json.dump(tmotes, f)

	# Extract input calibration files
	tmote_calib1 = {}
	tmote_calib2 = {}
	for ID in tmote_file1:
		tmote_calib1[ID] = analyze.extract_json(tmote_file1[ID])
	for ID in tmote_file2:
		tmote_calib2[ID] = analyze.extract_json(tmote_file2[ID])

	# Convert median RSSI measurements to estimated distances using the Model
	tmote_set = set(tmotes)
	tmote_loc_set = set(tmote_loc)
	aliens = tmote_set - tmote_loc_set
	for alien in aliens:
		del tmotes[alien]
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
			((x,y),minSE) = calc_xy(xlim,ylim,d1,d2,loc1,loc2)
			print "minSE = ", minSE
			locations.append(numpy.array([x,y]))
	print
	print "location solutions = ", locations
	print

	# Average over all locations
	xs = [elem[0] for elem in locations]
	ys = [elem[1] for elem in locations]
	x ,y = sum(locations)/len(locations)
	print "estimated location = ", (x,y)
	print
	print "x range: ", min(xs), " ", max(xs)
	print
	print "y range: ", min(ys), " ", max(ys)
	print

	# Write to file
	with open(outfile2, "w") as f: 
		locations = [elem.tolist() for elem in locations]
		json.dump(locations, f)

	return (x,y)

class Tmote_Sampler(object):

	def __init__(self, roomba):
		self.roomba = roomba
		self.samples = []

	def take_sample(self):
		angle = 95
		sample_time = 5
		tmotes = measure.sample_RSSI(sample_time)
		self.roomba.rotate(angle,200)
		for i in range(3):
			tmotes = measure.sample_RSSI(sample_time, tmotes)
			self.roomba.rotate(angle,200)
		self.samples.append(trilaterate(tmotes))
		time.sleep(sample_time)

	def get_samples(self):
		return self.samples

if __name__ == '__main__':
	tmotes = measure.sample_RSSI(5)
	trilaterate(tmotes)

