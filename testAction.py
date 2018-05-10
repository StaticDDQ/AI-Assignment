from copy import deepcopy
import numpy

WHITE, BLACK, BLANK, CORNER = 'O', '@', '-', 'X'

# Player Class
class Player:
    
    def __init__(self, colour):
        # timer to indicate how close will the board shrink
        self.timer = 0
        # Y range is (0-5) for white, else (2-7)
        self.minY = 0 if colour == 'white' else 2
        self.icon = 'O' if colour == 'white' else '@'
        # initate empty game state
        self.gameState = Gamestate(8)
        # get all positions for placing phase
        self.availablePosition = self.getAllPositions(self.gameState.getBoard(),self.minY)
    
    def action(self, turns):
        self.timer += 1
        # first turn for player
        if(turns == 0):
            return self.placeFirst()
        # during placing phase
        elif(0<turns<24):
            

        # during moving phase
        else:
            move = self.abPruing(self.icon,self.gameState,self.gameState.getSize(),2,self.timer)
            
        return move
	
    def update(self, action):
        self.gameState.movePiece(action[0], action[1])
        self.gameState.updateKills()
    
    def getAllPositions(board,minY):
        availablePosition = []
        # find all positions for player to place a piece during placing phase
        for pos in board:
            if(pos[1] >= minY and board[pos] == '-'):
                availablePosition.append(pos)
        return availablePosition
    
    # method in cases where player moves first, called once
    def placeFirst(self):
        return 1
    
    # make a copy of the next state when it makes a move
    def createNextState(state,move):
        # copy current state
        tempState = deepcopy(state)
        tempState.movePiece(move[0],move[1])
        ''' update state in case when something gets destroyed'''
        return tempState
    
    # minimax algorithm for the moving phase
    def abPruing(self,icon,state,size,layer,timer,maximizer=True,alpha=float("-inf"), beta=float("inf")):
        
        # at gameover state
        if(state.isGameover()):
            return state.eval(icon)
        
        # a-b pruning
        floor = alpha
        ceiling = beta
        
        # get all moves for current player
        moves = state.availableMoves()
        # shrink board if timer reaches certain value
        if(timer == 128):
            size = 6
        elif (timer == 192):
            size = 4
        
        # if there are available moves
        if(len(moves)>0):
            if(layer > 0):
                if(maximizer):
                    bestScore = float('-inf')
                    bestMove = moves[0]
                    for move in moves:
                        # create follow-up state
                        nextState = self.createNextState(state,move)
                        
                        icon = WHITE if icon == BLACK else BLACK
                        
                        score = self.abPruing(icon,nextState,size,layer-1,timer+1,not maximizer,floor,ceiling)[0]
                        if(score > bestScore):
                            bestScore = score
                            bestMove = move
                            
                        # Alphabeta bookkeeping:
                        if(bestScore > floor):
                            floor = bestScore   # Constrains children at the next (minimizing) layer to be above this value
                        if(bestScore >= ceiling): # Stop searching any more if it's above the upper limit
                            break
                else:
                    bestScore = float('inf')
                    bestMove = moves[0]
                    for move in moves:
                        nextState = self.createNextState(state,move)
                        
                        icon = WHITE if icon == BLACK else BLACK
                        
                        score = self.abPruing(icon,nextState,size,layer-1,timer+1,not maximizer,floor,ceiling)[0]
                        if(score < bestScore):
                            bestScore = score
                            bestMove = move
                            
                        if(bestScore < ceiling):
                            ceiling = bestScore   # Constrains children at the next (maximizing) layer to be below this value
                        if(bestScore <= floor): # Stop searching any more if it's below the lower limit
                            break
            else:
                bestScore = state.eval(icon)
                bestMove = None
        else:
            bestScore = state.eval(icon)
            bestMove = None
        
        return bestScore, bestMove
    
#==============================================================================
  
# GameState Class
RIGHT, UP, LEFT, DOWN = (1, 0), (0, 1), (-1, 0), (0, 1)
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]
BLANK, CORNER = '-','X' #Initialized at top, might remove if file splitting can read const from player.py

class Gamestate:
    
    def __init__(self,size):
        self.size = size
        self.board = self.declareBoard(size)
        self.winner = ''
        self.whitePieces = []
        self.blackPieces = []
        
    def declareBoard(self,size):
        self.board = {}
        self.size = size
        calc = (int)((8-size)/2) # in case board has shrunk
        for row in range(calc,size+calc):
            for col in range(calc,size+calc):
                if((row == size+calc-1 and col == size+calc-1) or 
                   (row == size+calc-1 and col == size+calc-1) or
                   (row == calc and col == size-1) or 
                   (row == calc and col == calc)):
                    self.board[col,row] = CORNER
                else:
                    self.board[col,row] = BLANK
    
    # check if the game has ended
    def isGameOver(self):
        piece = ''
        for i in self.board:
            # if there is another piece thats different, 
            # then game is not over
            if(i=='O' or i=='@'):
                if(piece != i):
                    return False
                piece = i
        self.winner = piece
        return True
    
    # assumes that pos is valid, position is within bound and piece is correct
    # adds a piece, during placing phase
    def addPiece(self,pos, piece):
        self.board[pos[0],pos[1]] = piece
        self.whitePieces.append(pos) if(piece == WHITE) else self.blackPieces.append(pos)
        
    # removes a piece, if a piece destroys another piece
    def removePiece(self,pos):
        pieceIcon = self.board[pos[0],pos[1]]
        self.board[pos[0],pos[1]] = BLANK
        self.whitePieces.remove(pos) if(piece == WHITE) else self.blackPieces.remove(pos)
        
    # move a piece to a new direction, during moving phase
    def movePiece(self,oldPos,newPos):
        # get the icon of the piece
        icon = self.board[oldPos[0],oldPos[1]]
        self.board[newPos[0],newPos[1]] = icon
        self.board[oldPos[0],oldPos[1]] = BLANK
    
    # get available moves each piece has in moving phase
    def availableMoves(self,icon):
        currPos = self.whitePieces if(icon == WHITE) else self.blackPieces
        moves = []
        for piece in currPos:
            for direction in DIRECTIONS:
                # a normal move to an adjacent square
                adjacent_square = self.sumTuples(zip(piece, direction))
                if(adjacent_square in self.board and self.board[adjacent_square] == BLANK):
                    moves.append((piece,adjacent_square))
                    continue # a jump move is not possible in this direction
        
                # if not, jump another square ahead
                opposite_square = self.sumTuples(zip(piece, direction, direction))
                if(adjacent_square in self.board and self.board[adjacent_square] == BLANK):
                    moves.append((piece,opposite_square))
        return moves
	
	# sums up set of zipped tuples
	def sumTuples(zipped):
		return tuple([sum(x) for x in zipped])
    
	# add kills from shrinking
	def updateKills(self):
		for piece in self.getPieces():
			enemy = BLACK if self.board[piece[0],piece[1]] == WHITE else WHITE
			origin = (int)((8-self.size)/2)
			
			# checks x-axis, then y-axis
			for axis in range(0,2):
			
				# killed by surrounding enemies
				if origin < piece[axis] < origin+self.size:
					posAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis]))
					negAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))
					if (posAxis == CORNER or posAxis == enemy) and (negAxis == CORNER or negAxis == enemy):
						self.removePiece(piece)
						
				# killed by board shrinking
				else if piece[axis] < origin or piece[axis] > origin+self.size:
					self.removePiece(piece)
	
	# return array of all pieces of specified colour existing on board
	def getPieces(self, colour="Both"):
		pieces = []
		origin = (int)((8-self.size)/2) # in case board has shrunk
		for row in range(origin, origin+self.size):
			for col in range(origin, origin+self.size):
				if colour == "Both":
					if self.board[row, col] == WHITE or self.board[row, col] == BLACK:
				else:
					if self.board[row, col] == colour:
						pieces.append((row, col))
		return pieces
	
	# returns score for minimax evaluation of board state
	def eval(self, colour):
		enemy = BLACK if colour == WHITE else WHITE
		playerPieces = self.getPieces(colour)
		enemyPieces = self.getPieces(enemy)
		score = 0;
		
		# Score = Enemy Vulnerability - Player Vulnerability
		for piece in playerPieces:
			score -= self.calcVulnerability(piece, colour, enemy)
		for piece in enemyPieces:
			score += self.calcVulnerability(piece, enemy, colour)
			
		return score
	
	def calcVulnerability(self, piece, colour, enemy):
		vulnerableCount = 0;
		vulnerableSum = 0;
		origin = (int)((8-self.size)/2) # in case board has shrunk
		
		# check vulnerability horizontally and vertically
		for axis in range(0,2):
		
			# piece is safe in that axis is sticking to the edge
			if origin < piece[axis] < origin+self.size:
			
				# tiles beside piece
				posAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis]))
				negAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))
				
				# piece is safe in that axis if at least one friendly piece beside, can't be surrounded
				if !(posAxis == colour or negAxis == colour):
					vulnerableCount += 1
					# Vulnerability = # of enemy pieces surrounding piece * 0.5
					# Eg: 0 = no pieces, 0.5 = 1 enemy piece, 1 = killed
					vulnerableSum += (int(posAxis == CORNER or posAxis == enemy) + int(negAxis == CORNER or negAxis == enemy))*0.5
				
		vulnerableAvg = vulnerableSum/vulnerableCount if vulnerableCount != 0 else 0
		# Level of vulnerability has 3 times higher priority than number of vulnerable axes
		vulnerableWeighted = 0.25*vulnerableSum + 0.75*vulnerableAvg
		return vulnerableWeighted
    
    def getSize(self):
        return self.size
    
    def getWinner(self):
        return self.winner