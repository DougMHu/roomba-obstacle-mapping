import numpy
import Queue
import os
import inspect
import sys
import time

include_paths = ["../visualization"]
for path in include_paths:
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],path)))
	sys.path.insert(0, cmd_subfolder)
import turtle_roomba as rb

# inputs: room length, room width, step distance (mm)
# output: grid with marked obstacles

# Example room
length = 4500
width = 4000
step = 500

# Roomba starts in the center of a square, so range does not include the endpoint
xs = numpy.arange(0,length, step)
ys = numpy.arange(0, width, step)

discovered = numpy.zeros((len(xs),len(ys)))		#discovery map formed
processed = numpy.zeros((len(xs),len(ys)))		#to check if locn already visited
#remove processed if you want to check grid from all sides
curloc = (0,0)									#current location of Roomba
path = []

# Simulate this obstacle map
input_obstacle = numpy.zeros((len(xs),len(ys)))
input_obstacle[1][3]=1
input_obstacle[1][4]=1
input_obstacle[2][3]=1
input_obstacle[2][4]=1

# input_obstacle[0][3]=1
# input_obstacle[0][4]=1
# input_obstacle[1][3]=1
# input_obstacle[1][4]=1
# input_obstacle[0][7]=1
# input_obstacle[1][7]=1

# input_obstacle[4][3]=1
# input_obstacle[4][4]=1
# input_obstacle[5][3]=1
# input_obstacle[5][4]=1

# input_obstacle[1][5]=1
# input_obstacle[1][6]=1
# input_obstacle[2][5]=1
# input_obstacle[2][6]=1
# input_obstacle[4][1]=1
# input_obstacle[4][2]=1
# input_obstacle[5][1]=1
# input_obstacle[5][2]=1
# input_obstacle[6][1]=1
# input_obstacle[6][2]=1
# input_obstacle[7][1]=1
# input_obstacle[7][2]=1

# Instantiate a roomba
roomba = rb.CuteTurtle(width*0.001, length*0.001, step*0.001, input_obstacle)

def bfs( dest ):
	global path
	(destx,desty)=dest
	distance = numpy.empty((len(xs),len(ys)))
	distance.fill(numpy.inf)
	visited = numpy.zeros((len(xs),len(ys)))	
	#print distance
	q = Queue.Queue()
	q.put(curloc)
	visited[curloc[0]][curloc[1]]=1
	distance[curloc[0]][curloc[1]]=0
	while not q.empty():
		(x,y)=q.get()
		flag=0
		for i in [1, -1]:
			if x+i in range(len(xs)) and visited[x+i][y]==0 and discovered[x+i][y]==1:
				visited[x+i][y]=1
				distance[x+i][y]=distance[x][y]+1
				q.put((x+i,y))
				if x+i==destx and y==desty: flag=1
		if flag: break
		for j in [1, -1]:
			if y+j in range(len(ys)) and visited[x][y+j]==0 and discovered[x][y+j]==1:
				visited[x][y+j]=1
				distance[x][y+j]=distance[x][y]+1
				q.put((x,y+j))
				if x==destx and y+j==desty: flag=1
		if flag: break
	print "distance map:"
	print distance
		
	lst=[(destx,desty)]
	dst=distance[destx][desty]
	(x,y)=(destx,desty)
	while dst>0:
		flag=0
		for i in [1, -1]:
			if x+i in range(len(xs)) and distance[x+i][y]==dst-1:
				x=x+i
				flag=1
				lst.append((x,y))
				dst=distance[x][y]
				break
		if not flag:
			for j in [1, -1]:
				if y+j in range(len(ys)) and distance[x][y+j]==dst-1:
					y=y+j
					flag=1
					lst.append((x,y))
					dst=distance[x][y]
					break
	print "list:",lst
	for i in range(len(lst)-1,-1,-1):
		path.append(lst[i])
	locStack = [ [lst[i],lst[i+1]] for i in range(0,len(lst)-1) ]
	print "locStack:",locStack
	return locStack

def NOobstacleAt(dest):
	'''	Go to square 1 step away from dest and call Roomba obstacle checker
		return true if NO obstacle
	'''
	global curloc, step
	[(x,y),(parentx,parenty)]=dest
	(xold,yold)=curloc
	if ( abs(x-xold) + abs(y-yold) )==0: #at destn square already
		return True
	if ( abs(x-xold) + abs(y-yold) )!=1: #more than 1 x or y step required
		print "destn:",dest
		print "more steps needed"
		print "curloc:", curloc
		locStack = bfs( (parentx,parenty) ) 
		#call roomba functions to reach parentx,parenty
		while (len(locStack) != 0):
			next_loc = locStack.pop()
			print "next_loc = ", next_loc
			roomba.move(next_loc, input_obstacle[next_loc[0][0]][next_loc[0][1]])
		curloc = (parentx,parenty)
	#Only 1 step needed to destn now
	if not roomba.move([(x,y), curloc], input_obstacle[x][y]): #call roomba obstacle checker here
		return True
	return False

def dfs(start):
	'''	Given start:[(x,y),(parentx,parenty)]...run dfs...with priority
		to y over x and lower values of y over higher values of y
	'''
	global curloc, path
	stack = []
	stack.append(start)
	while (len(stack) != 0):
		popped_node = stack.pop()
		#time.sleep(2)
		[(x,y),(parentx,parenty)]=popped_node
		if (discovered[x][y] == 0 and processed[x][y]==0): #if not discovered
			if( NOobstacleAt(popped_node) ):#if no obstacle
				discovered[x][y] = 1
				print "curloc:", curloc
				print "x:",x,"y",y,"discovered:"
				print discovered
				print
				for i in [1, -1]:
					if x+i in range(len(xs)):
						stack.append([(x+i,y),(x,y)])
				for j in [1, -1]:
					if y+j in range(len(ys)):
						stack.append([(x,y+j),(x,y)])
				curloc = (x,y)
				path.append(curloc)
				print "curloc = ", curloc
			processed[x][y]=1



dfs([(0,0),(0,-1)])
print "final map:\n", discovered
print "path:\n", path
roomba.exit()

#print processed
#bfs((0,0))


