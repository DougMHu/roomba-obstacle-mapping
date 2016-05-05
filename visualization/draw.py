import turtle

turtle.setup(800,800)
wn = turtle.Screen()  

doug = turtle.Turtle()

# Draw a grid
length = 5
width = 2
step = 50

def draw_row(width, mark):
	doug.up()
	for i in range(width):
		if (mark[i]):
			doug.down()
			doug.begin_fill()
		for j in range(4):
			doug.fd(step)
			doug.right(90)
		if (mark[i]):
			doug.end_fill()
		doug.fd(step)
		doug.up()

#draw_row(width,[1,0])

def draw_matrix(mark):
	doug.up()
	rows = len(mark)
	cols = len(mark[0])
	orig = doug.fillcolor()
	doug.fillcolor('red')
	for row in mark:
		draw_row(cols, row)
		doug.fd(-cols*step)
		doug.right(90)
		doug.fd(step)
		doug.left(90)
	doug.fillcolor(orig)

draw_matrix([[0,1],[1,1]])

# doug.left(90)
# doug.fd((width-0.5)*step)
# doug.right(90)
# doug.up()
# doug.fd(0.5*step)
# doug.down()
# doug.pensize(step)
# doug.fd((length-1)*step)

turtle.getscreen()._root.mainloop()

#doug.fd(length*step)
