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

'''

'''
class CuteTurtle(object):

	def __init__(self, length, width, roomba_step, obstacles=None):
		'''
		###initialization
		'''
		self.obstacles = obstacles
		self.orient = 0
		self.length = length #assume length in m
		self.width = width #assume width in m
		self.roomba_step = roomba_step#assume in m
		self.multiply_factor = 50 #screenstep = multiply_factor * length/width
		self.step_l = self.length*self.multiply_factor
		self.step_w = self.width*self.multiply_factor
		self.roomba_l = self.roomba_step*self.multiply_factor
		self.t = turtle.Turtle()
		self.t.shape("classic")
		turtle.setup(self.step_l+100,self.step_w+100)
		turtle.screensize(self.step_l+10, self.step_w+10)
		#turtle.bgcolor("orange")
		self.t.penup()
		self.t.bk(self.step_l/2) # backward()
		self.t.lt(90) # left()
		self.t.fd(self.step_w/2) # forward()
		self.t.rt(90) # right()
		self.draw_boundary(self.step_l, self.step_w, self.roomba_l, self.t)
		###set pen width
		self.t.pendown()
		self.t.pencolor("green")
		self.t.pensize(self.roomba_l-1)

		self.t.fd(self.roomba_l)

		#exitonclick()

	
	### API commands ###
	def move(self, xylist, input_obstacle):
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
		obstacle = self.discover(input_obstacle)
		#self.t.stamp()
		return obstacle

	def redirect(self, new_orient):
		if (self.orient - new_orient) % 4 == 0:
			self.orient = new_orient
			return
		elif (self.orient - new_orient) % 4 == 1:
			self.right()
			self.orient = new_orient
			return
		elif (self.orient - new_orient) % 4 == 2:
			self.rotate(180)
			self.orient = new_orient
			return
		else:
			self.left()
			self.orient = new_orient
			return


	def discover(self, input_obstacle):
		""""""
		if (input_obstacle):
			return True
		else:
			self.forward()
			return False

	def drive(self, distance):
		"""Input: integer distance (mm), integer speed (mm/s)
		Sends appropriate serial command to Roomba"""
		self.t.fd(distance)

	def rotate(self, angle):
		"""Input: angle (degrees)"""
		self.t.lt(angle)

	def draw_boundary(self, step_l, step_w, roomba_l, t):
		"""
		###draw boundaries &
		###set turtle into roomba starting position
		"""
		self.t.pendown()
		for i in range(2):
			self.t.fd(step_l)
			self.t.rt(90)
			self.t.fd(step_w)
			self.t.rt(90)
		if (self.obstacles != None):
			self.draw_matrix(self.obstacles)
		self.t.penup()
		self.t.fd(-roomba_l/2)
		self.t.rt(90)
		self.t.fd(roomba_l/2)
		self.t.lt(90)
	
	def draw_row(self, width, mark):
		self.t.up()
		for i in range(width):
			if (mark[i]):
				self.t.down()
				self.t.begin_fill()
				for j in range(4):
					self.t.fd(self.roomba_l)
					self.t.right(90)
				self.t.up()
				self.t.end_fill()
			self.t.fd(self.roomba_l)

	def draw_matrix(self, mark):
		self.t.up()
		rows = len(mark)
		cols = len(mark[0])
		orig = self.t.fillcolor()
		self.t.fillcolor('red')
		for row in mark:
			self.draw_row(cols, row)
			self.t.fd(-cols*self.roomba_l)
			self.t.right(90)
			self.t.fd(self.roomba_l)
			self.t.left(90)
		self.t.fillcolor(orig)
		self.t.left(90)
		self.t.fd(rows*self.roomba_l)
		self.t.right(90)

	###Forward###
	def forward(self):
		'''
		update turtle as roomba moving forward one step
		'''
		self.t.fd(self.roomba_l/2)
		self.t.stamp()
		self.t.fd(self.roomba_l/2)


	###Left()###
	def left(self):
		'''
		update turtle as roomba turning left 90 degrees
		'''
		self.t.lt(90)

	###def Right()###
	def right(self):
		'''
		update turtle as roomba turning right 90 degrees
		'''
		self.t.rt(90)

	
	###onclickExit###
	def exit(self):
		'''
		exitonclick() for turtle GUI
		'''
		turtle.exitonclick()


#t = CuteTurtle(10,8,0.2)

