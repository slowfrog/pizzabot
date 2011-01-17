##################
#Bejeweled Blitz bot
#12/23/10 nibblerslitterbox
##################

#When I saw this post: http://www.reddit.com/r/programming/comments/eptes/i_programmed_a_bot_to_play_bejeweled_blitz_scored/ of a bejeweled blitz bot and how the source was promised and not released, I started work on my own version in Python.  I'm not a programmer by trade, I'm a sysadmin, and my programming skills are.... lacking.  But in a few hours of downtime I was able to put this together. Then I look for that thread to post in and I see that the OP posted his java source.  Aww man... 
#
#So, here it is anyway. It's not AI, it just brute forces every possible move (in a probably highly inefficient manner.)  It also gets hella confused on special gems, which I tried to work around, but I think I just made it worse.  Regardless, I beat my wife and mom's scores, so my goals are satisfied.  Feel free to make it not suck, or mock my terrible code, or both!
#
#Source: http://diffra.com/blitzbot.py
#
#Video: http://www.youtube.com/watch?v=6KB8YDhxSYQ

import win32api, win32con
import PIL, ImageGrab, time,sys

###CHANGE THIS!!!###
#board location is variable on browser
boardstartx=327
boardstarty=348


#square size
sqx=40
sqy=40

#screenshot function
def sshot(lx,ly,ux,uy):
	im=ImageGrab.grab((lx,ly,ux,uy))
	#im.save("img.png")
	return im.load()

#mouse control
def drag(x,y,movx,movy):
	win32api.SetCursorPos((x,y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(.1)
	win32api.SetCursorPos((x+movx,y+movy))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	
#execute move
def domove(tile, axis):
	if axis=="x":
		drag(boardstartx+20+(sqx*tile[0]),boardstarty+20+(sqy*tile[1]),40,0)
	if axis=="y":
		drag(boardstartx+20+(sqx*tile[0]),boardstarty+20+(sqy*tile[1]),0,40)

#hack to hopefully handle "special" gems
def comparepixel(px1, px2, acc=10):
	#print px1
	#print px2
	a=px1[1]-px2[1]
	b=px1[2]-px2[2]
	c=px1[0]-px2[0]
	d=a+b+c
	negacc=-1*acc
	#print d
	#print negacc
	#if negacc < d:
	#	print "true1"
	#if d < acc:
	#	print "true2"
	#sys.exit()
	if negacc < d < acc:
		#print "cactus"
		#sys.exit()
		return 1
	else:
		#sys.exit()
		return 0

#function to look for standard X/Y moves
def findmove(status):
	#print status
	l=0
	for line in status:
		#print "line "+str(l)
		for i in range(0,5):
			#print line[i:i+4].count(line[i])
			if line[i:i+4].count(line[i]) == 3:
				print comparepixel(line[i],line[i+3])
				print "match found, line "+str(l)+", column "+str(i)
				#return coordinates on board, x,y
				if i==0:
					if line[0]!=line[1]:
						coord=[0,l]
						
					elif line[1]!=line[2]:
						coord=[2,l]
						
					elif line[2]!=line[3]:
						coord=[3,l]
					else:
						print "unable to find match.  error."
						return 0
				else:
					if line[i]!=line[i+1]:
						coord=[i, l]
					else:
						coord=[i+2, l]
				return coord
		l=l+1
	#print "no match found"
	return 0

#looks for every possible case of a 2-line move
def findTmove(status):
	l=0
	#convert list to dict
	matrix={}
	for line in status:
		matrix[l]=line
		l=l+1
	#print matrix
	l=0
	#top down
	for l in range(0,7): 
		for i in range(0,6):
			#VVx
			#xxV
			if comparepixel(matrix[l][i],matrix[l][i+1])==1 and comparepixel(matrix[l][i],matrix[l+1][i+2])==1:
					print "T match found1"
					coord=[i+2,l]
					return coord
			#Vxx
			#xVV
			if comparepixel(matrix[l][i],matrix[l+1][i+1])==1 and comparepixel(matrix[l][i],matrix[l+1][i+2])==1:
					print "T match found2"
					coord=[i,l]
					return coord
			#xxV
			#VVx
			if comparepixel(matrix[l+1][i],matrix[l+1][i+1])==1 and comparepixel(matrix[l+1][i],matrix[l][i+2])==1:
					print "T match found3"
					coord=[i+2,l]
					return coord
			#xVV
			#Vxx
			if comparepixel(matrix[l+1][i],matrix[l][i+1])==1 and comparepixel(matrix[l+1][i],matrix[l][i+2])==1:
					print "T match found4"
					coord=[i,l]
					return coord
			#VxV
			#xVx
			if comparepixel(matrix[l][i],matrix[l+1][i+1])==1 and comparepixel(matrix[l][i],matrix[l][i+2])==1:
					print "T match found5"
					coord=[i+1,l]
					return coord
			#xxV
			#VVx
			if comparepixel(matrix[l+1][i],matrix[l+1][i+1])==1 and comparepixel(matrix[l+1][i],matrix[l][i+2])==1:
					print "T match found6"
					coord=[i+2,l]
					return coord
			#xVx
			#VxV
			if comparepixel(matrix[l+1][i],matrix[l][i+1])==1 and comparepixel(matrix[l+1][i],matrix[l+1][i+2])==1:
					print "T match found7"
					coord=[i+1,l]
					return coord
	#no match
	#print "no match found"
	return 0
				
def getcolors(px, board):
	y=0
	while y<8:
		board.append([])
		x=0
		while x<8:
			board[y].append(px[20+(40*x),20+(40*y)])
			x=x+1
		y=y+1

	
def rungame():
	win32api.SetCursorPos((0,0))
	img=sshot(boardstartx,boardstarty,boardstartx+(8*sqx),boardstarty+(8*sqy))
	gameboard=[]
	getcolors(img,gameboard)
	#print gameboard
	move=findmove(gameboard)
	if move==0:
		#no match, look for vertical matches
		gameboardy=zip(*gameboard)
		#print gameboard
		#print " "
		#print gameboardy
		move=findmove(gameboardy)
		if move!=0:
			ymove=[move[1],move[0]]
			print "Y move: "+str(move[0])+","+str(move[1])
			domove(ymove,"y")
			return 1
		else:
			tmove=findTmove(gameboard)
			if tmove!=0:
				domove(tmove,"y")
				return 1
			else:
				tmove=findTmove(gameboardy)
				if tmove!=0:
					tymove=[tmove[1],tmove[0]]
					print "found T Y move."
					domove(tymove,"x")
					return 1
				else:
					return 0
	else: 
		print move
		domove(move,"x")
		return 1

#2 second head start.  Start the script, then hit "play now"
ticks=time.time()
time.sleep(2)
#game is terrible at counting seconds during times of heavy animation.  
#I've seen games take up to 70 wall clock seconds, so giving a 5 sec buffer here.
while time.time()<ticks+75:
#while 1:
	rtn=rungame()
	if rtn==1:
		#this delay is needed to prevent overlapping moves
		time.sleep(.1)
	else:
		#increase this delay to 1 or 2 seconds if you want to see what's going on and follow the logic.
		time.sleep(.01)
	
