import math
from queue import PriorityQueue
MAX_VAL = 100

# ---SUB FUNCTIONS START HERE---

# calcMoves takes the board and coordinates as input
# and returns the number of moves possible from that coordinate
def calcMoves(board, row, col):
	
	moves = 0
	for pos in range(0,4): 
		# Cycle through directions based on rotation around unit circle
		rowDelta = int(math.sin(pos*(math.pi/2)))
		colDelta = int(math.cos(pos*(math.pi/2)))
		
		# Either the adjacent space OR the one next to it has to be empty and within the board
		if 0 <= row + 2*rowDelta <= 7 and 0 <= col + 2*colDelta <= 7:
			moves += board[row+rowDelta][col+colDelta] == '-' or board[row+2*rowDelta][col+2*colDelta] == '-'
		# Otherwise check only adjacent space and if it's within the board
		elif 0 <= row + rowDelta <= 7 and 0 <= col + colDelta <= 7:
			moves += board[row+rowDelta][col+colDelta] == '-'
	return moves

# Change position of icon
def ChangeBoardState(oldPos, newPos, icon):
    # move the piece to another location, or remove a piece by having icon = '-'
    board[oldPos[0]][oldPos[1]] = '-'
    board[newPos[0]][newPos[1]] = icon
    
# get all positions of all icons
def NumberOfPieces(icon):
    # searches all the positions of the icon in the board
    # returns a dictionary and the value of the key is the previous node of that key
    pieces = []
    for i in range(0,8):
        for j in range(0,8):
            # append the x and y coordinates of that icon
            if(board[i][j] == icon):
                pieces.append((i,j))
    return pieces  

# get the first black piece and 2 closest white pieces to that black piece
def SelectPieces():
    # get the first black piece in the iteration
    bPiece = ()
    for row in range(8):
        for col in range(8):
            if(board[row][col] == '@'):
                bPiece = (row,col)
                break
        if(bPiece != ()):
            break
    
    # get all white pieces and find 2 closest pieces to bPiece
    wPieces = NumberOfPieces('0')
    
    lowestDist = MAX_VAL
    for piece in wPieces:
        # calculate distance by the x,y differences
        dist = abs(piece[0]-bPiece[0])+abs(piece[1]-bPiece[1])
        if(dist < lowestDist):
            lowestDist = dist
            closestPiece1 = piece
            
    lowestDist = MAX_VAL
    for piece in wPieces:
        dist = abs(piece[0]-bPiece[0])+abs(piece[1]-bPiece[1])
        if(dist < lowestDist and piece != closestPiece1):
            lowestDist = dist
            closestPiece2 = piece
            
    return bPiece, closestPiece1, closestPiece2

# get the 2 most suitable positions to place the 2 white pieces to kill the enemy
def CheckSides(bPiece, w1, w2):

    # find the best position by getting the lowest cost to go there
    lowestCost = MAX_VAL
    for pos in range(0,4): 
        
        rowDelta = int(math.sin(pos*(math.pi/2)))
        colDelta = int(math.cos(pos*(math.pi/2)))
        
        # position must be valid and another black piece is not occupying it
        if(0 <= bPiece[0] + rowDelta <= 7 and 0 <= bPiece[1] + colDelta <= 7 and 
           0 <= bPiece[0] - rowDelta <= 7 and 0 <= bPiece[1] - colDelta <= 7 and
           board[bPiece[0]+rowDelta][bPiece[1]+colDelta] != '@' and
           board[bPiece[0]-rowDelta][bPiece[1]-colDelta] != '@'):
            
            # cost is the difference between the x and y coordinates
            cost = abs(w1[0] -(bPiece[0]+rowDelta)) + abs(w1[1] - (bPiece[1]+colDelta))
            cost += abs(w2[0] -(bPiece[0]-rowDelta)) + abs(w2[1] - (bPiece[1]-colDelta))
            
            if(cost < lowestCost):
                lowestCost = cost
                bestPos1 = (bPiece[0]+rowDelta,bPiece[1]+colDelta)
                bestPos2 = (bPiece[0]-rowDelta,bPiece[1]-colDelta)
                
    return bestPos1,bestPos2

# check if a black piece is being surrounded by 2 white pieces or not
# destroy that piece if so
def CheckBoard():
    bPieces = NumberOfPieces('@')
    
    for pos in bPieces:
        x = 1
        y = 0
        # check the vertical and horizontal neighbours of the black piece
        for side in range(2): 
            x = abs(x-1)
            y = abs(y-1)
            # if the 2 sides are surrounded by 2 white pieces, destroy this enemy
            if(0 <= pos[0] + x <= 7 and 0 <= pos[1] + y <= 7 and
               0 <= pos[0] - x <= 7 and 0 <= pos[1] - y <= 7 and 
               (board[pos[0]+x][pos[1]+y] == '0' or board[pos[0]+x][pos[1]+y] == 'X') and
               (board[pos[0]-x][pos[1]-y] == '0' or board[pos[0]-x][pos[1]-y] == 'X')):
                
                ChangeBoardState(pos,pos,'-')
                break
                    
# check if the position is surrounded by 2 enemies or not                     
def IsSafe(pos):
    x = 1
    y = 0
    # check the vertical and horizontal neighbours of the black piece
    for side in range(2): 
        x = abs(x-1)
        y = abs(y-1)
        if(0 <= pos[0] + x <= 7 and 0 <= pos[1] + y <= 7 and
           0 <= pos[0] - x <= 7 and 0 <= pos[1] - y <= 7 and 
          (board[pos[0]+x][pos[1]+y] == '@' or board[pos[0]+x][pos[1]+y] == 'X') and
          (board[pos[0]-x][pos[1]-y] == '@' or board[pos[0]-x][pos[1]-y] == 'X')):
                return False
    return True

# ---SUB FUNCTIONS END HERE---

def Move(icon):
    count = 0
    # returns all positions of the icon in the board
    pieces = NumberOfPieces(icon)
    # calculate number of moves for each piece
    for piece in pieces:
        count += calcMoves(board,piece[0],piece[1])
    print(count)
    
def Massacre():
    # while there are still enemies
    while len(NumberOfPieces('@')) > 0:
        
        # select 1 black piece and 2 closest white pieces
        bPiece, wPiece1, wPiece2 = SelectPieces()
        # get best position where to put the 2 white pieces
        pos1,pos2 = CheckSides(bPiece,wPiece1,wPiece2)
        
        # apply A* to get best path, move the piece after doing A*
        if(IsSafe(pos1)):
            w1Sequence = A(wPiece1,pos1)
            ChangeBoardState(wPiece1, pos1, '0')
            w2Sequence = A(wPiece2,pos2)
            ChangeBoardState(wPiece2, pos2, '0')
        else:
            w2Sequence = A(wPiece2,pos2)
            ChangeBoardState(wPiece2, pos2, '0')
            w1Sequence = A(wPiece1,pos1)
            ChangeBoardState(wPiece1, pos1, '0')
            
        # fixed formatting and print the path from initialState to goalState
        # for both pieces
        direction = []
        index = pos1
        while w1Sequence[index] is not None:
            direction.append(index)
            index = w1Sequence[index]
        direction.append(index)
        
        # if a piece doesn't move, dont print it
        if(len(direction) > 1):
            for i in reversed(range(1,len(direction))):
                print((direction[i][1],direction[i][0]),'->',(direction[i-1][1],direction[i-1][0]))
        
        direction = []
        index = pos2
        while w2Sequence[index] is not None:
            direction.append(index)
            index = w2Sequence[index]
        direction.append(index)
       
        if(len(direction) > 1):
            for i in reversed(range(1,len(direction))):
                print((direction[i][1],direction[i][0]),'->',(direction[i-1][1],direction[i-1][0]))
        
        # update board if the moves kill an enemy
        CheckBoard()
    
# ---A* search algorithm---

def A(start, goal):
    pq = PriorityQueue()

    # cost of start is 0
    pq.put((0,start))
    # record all the previous positions of each node
    sequence = {}
    # cost of each node
    cost = {}
    # there is no previous node from the start
    sequence[start] = None
    cost[start] = 0
    
    while not pq.empty():
        
        # pq.get[0] is the cost, pq.get[1] is the coordinates
        current = pq.get()[1]
        if(current == goal):
            break
        
        # iterate through all four sides
        for i in range(4):
            rowDelta = int(math.sin(i*(math.pi/2)))
            colDelta = int(math.cos(i*(math.pi/2)))
            
            pos = (current[0]+rowDelta, current[1]+colDelta)
            pos2 = (current[0]+rowDelta*2, current[1]+colDelta*2)
            
            # if position is appropriate and it is empty
            if(0 <= pos[0] <=7 and 0 <= pos[1] <= 7 and board[pos[0]][pos[1]] == '-'):
                # cost to travel 1 tile or jumping a tile is 1
                newCost = (cost[current] + 1)
                # if position is not recorded yet or the cost is better
                if(pos not in cost or newCost < cost[pos]):
                    cost[pos] = newCost
                    priority = newCost + Heuristics(pos,goal)
                    pq.put((priority,pos))
                    sequence[pos] = current
                
            # if it isnt then we check the tile ahead
            elif(0<=pos2[0]<=7 and 0<=pos2[1]<=7 and board[pos2[0]][pos2[1]] == '-'):
                newCost = cost[current] + 1
                if(pos2 not in cost or newCost < cost[pos2]):
                    cost[pos2] = newCost
                    priority = newCost + Heuristics(pos2,goal)
                    pq.put((priority,pos2))
                    sequence[pos2] = current
                
    return sequence

def Heuristics(start, goal):
    # euclidean distance
    x = abs(start[0]-goal[0])
    y = abs(start[1]-goal[1])
    xSide = 1
    ySide = 0
    
    addedCost = 0
    if(start is not goal):
        # check the vertical and horizontal neighbours of the black piece
        for side in range(2): 
            xSide = abs(x-1)
            ySide = abs(y-1)
            if(0 <= start[0] + xSide <= 7 and 0 <= start[1] + ySide <= 7 and
               0 <= start[0] - xSide <= 7 and 0 <= start[1] - ySide <= 7 and 
              (board[start[0]+xSide][start[1]+ySide] == '@' or board[start[0]+xSide][start[1]+ySide] == 'X') and
              (board[start[0]-xSide][start[1]-ySide] == '@' or board[start[0]-xSide][start[1]-ySide] == 'X')):
                addedCost = MAX_VAL
                break
        
    return (x**2+y**2)**(0.5) + addedCost
          

board = []

# Transform input into 2D list
for row in range(8):
	 board.append(input().split())

action = input()

if action == "Moves":
    Move('0')
    Move('@')
elif action == "Massacre":
    Massacre()		
				

# ---MAIN PROGRAM ENDS HERE---