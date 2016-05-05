#Assume we have RSSI1 & RSSI2
#we set up experiement for d1=1m (RSSI1) & d2=2m (RSSI2)

import math
def calc_const(RSSI1, RSSI2, d1, d2):
	"""Calculate n & A"""
	n = (RSSI1-RSSI2) / (-10*math.log10(d1) + 10*math.log10(d2))
	A = RSSI1 + 10*n*math.log10(d1)
	return [n, A]

def calc_distance(n, A, RSSI):
	"""Calculate d"""
	return math.pow(10, (RSSI-A)/(-10*n))

def calc_median(input_list):
	"""sort the list and return median"""
	new_list = sorted(input_list)
	len_list = len(new_list)
	if len_list%2 == 0:
		return (new_list[len_list/2-1] + new_list[len_list/2] ) / 2
	else:
		return new_list[len_list/2]
def calc_median_distance(RSSI_list, n, A):
	"""Input List RSSI
		find median of RSSI list
		calculate distance for it
	   Output is calculated distance
	"""
	median_RSSI=calc_median(RSSI_list)
	return calc_distance(n, A, median_RSSI)

### may use later ###
def calc_average(input_list):
	"""Input List median_distances
	   Output average distance calculated
	"""
	if len(input_list) != 0:
		return sum(input_list)/len(input_list)
	else:
		return 0



def main():
	#first calculate parameter n and A
	[n,A] = calc_const(-10, -20, 1, 2)
	print "n= ", n, "A= ", A
	#print calc_distance(n, A, -15)
	#we assume we have RSSI list

	median_distance = calc_median_distance(RSSI)



	return 0

if __name__ == '__main__':
	main()
