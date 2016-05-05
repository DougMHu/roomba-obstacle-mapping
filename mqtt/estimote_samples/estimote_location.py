def parse(message):
	s=message
	x = float(s.split(",")[0].split(":")[1])
	y = float(s.split(",")[1].split(":")[1])
	#s = s.split(",")
	x_y = [x,y]
	return x_y

infile = 'test_1_3.txt'
actual_loc = (int(infile[5]), int(infile[7]))

locations = []

with open(infile, 'r') as f:
	for line in f:
		locations.append(parse(line))

xs = [location[0] for location in locations]
ys = [location[1] for location in locations]
x_avg = float(sum(xs))/len(xs)
y_avg = float(sum(ys))/len(ys)
estimated_loc = (x_avg, y_avg)
x_range = (min(xs), max(xs))
y_range = (min(ys), max(ys))
error = (actual_loc[0] - estimated_loc[0])**2 + (actual_loc[1] - estimated_loc[1])**2

print "\nactual loc = ", actual_loc
print "\nestimated loc = ", estimated_loc
print "\nerror = ", error
print "\nx range = ", x_range
print "\ny range = ", y_range
print