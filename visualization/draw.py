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
