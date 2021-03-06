from copy import deepcopy

WHITE, BLACK, BLANK, CORNER = 'O', '@', '-', 'X'
RIGHT, UP, LEFT, DOWN = (1, 0), (0, -1), (-1, 0), (0, 1)
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]

# Player Class
class Player:
    
    def __init__(self, colour):
        # timer to indicate how close will the board shrink
        self.timer = 0
        # Y range is (0-5) for white, else (2-7)
        self.minY = 0 if colour == 'white' else 2
        self.icon = WHITE if colour == 'white' else BLACK
        # initate empty game state
        self.gameState = Gamestate(8)
        # get all positions for placing phase
        self.availablePosition = self.getAllPositions(self.gameState.getBoard(),self.minY)
    
    def action(self, turns):
        # during placing phase
        if self.timer < 24:
            move = self.abPruning(self.icon,self.gameState,self.gameState.getSize(),2,self.timer,True)[1]
            self.gameState.addPiece(move,self.icon)
        # during moving phase
        else:
            move = self.abPruning(self.icon,self.gameState,self.gameState.getSize(),2,self.timer,False)[1]
            self.gameState.movePiece(move[0],move[1])
        self.timer += 1
        #print(self.icon + "'s perspective at time " + str(self.timer) + str(self.gameState.whitePieces))
        self.gameState.updateKills()
        #print(self.icon + "'s perspective at time " + str(self.timer) + str(self.gameState.whitePieces))
        return move
	
    def update(self, action):
        if self.timer < 24:
            enemy = BLACK if self.icon == WHITE else WHITE
            self.gameState.addPiece(action, enemy)
        else:
            self.gameState.movePiece(action[0], action[1])
        self.timer += 1

        if(self.timer == 128+24):
            self.gameState.size = 6
            self.gameState.updateBoardSize(6)
            self.gameState.updatePiece(self.gameState.size)
        elif(self.timer == 192+24):
            self.gameState.size = 4
            self.gameState.updateBoardSize(4)
            self.gameState.updatePiece(self.gameState.size)
        #print(self.icon + "'s perspective at time " + str(self.timer) + str(self.gameState.blackPieces))
		#print(self.icon + "'s perspective at time " + str(self.timer) + str(self.gameState.blackPieces))
    
    def getAllPositions(self,board,minY):
        availablePosition = []
        # find all positions for player to place a piece during placing phase
        for pos in board:
            if(minY <= pos[1] <= minY+5 and board[pos] == BLANK):
                availablePosition.append(pos)
        return availablePosition
    
    # make a copy of the next state when it makes a move
    def createNextState(self,state,size,move):
        # copy current state
        tempState = deepcopy(state)
        # check if the board shrinks
        if(tempState.getSize() != size):
            tempState.updateBoardSize(size)
            tempState.updateKills()
        tempState.movePiece(move[0],move[1])
        tempState.updateKills()
        return tempState
		
    def createNextPlacementState(self,state, pos, tile):
        tempState = deepcopy(state)
        tempState.addPiece(pos, tile)
        tempState.updateKills()
        return tempState
    
    # minimax algorithm for the moving phase
    def abPruning(self,icon,state,size,layer,timer,isPlacing,maximizer=True,alpha=float("-inf"), beta=float("inf")):
        
        # a-b pruning
        floor = alpha
        ceiling = beta
        
        # get all moves for current player
        if(isPlacing):
            self.minY = 0 if icon == WHITE else 2
            moves = self.getAllPositions(state.getBoard(),self.minY)
        else:
            moves = state.availableMoves(icon)
        # shrink board if timer reaches certain value
        if(timer >= 128+24):
            size = 6
        if(timer >= 192+24):
            size = 4
        
        # if there are available moves
        if(len(moves)>0):
            # if there is still a layer in the tree
            if(layer > 0):
                # if current player is a Maximiser
                if(maximizer):
                    # set to be as low as possible
                    bestScore = float('-inf')
                    bestMove = moves[0]
                    for move in moves:
                        # create follow-up state
                        if(isPlacing):
                            nextState = self.createNextPlacementState(state,move,icon)
                        else:
                            nextState = self.createNextState(state,size,move)
                        # switch players
                        icon = WHITE if icon == BLACK else BLACK
                        
                        score = self.abPruning(icon,nextState,size,layer-1,timer+1,isPlacing,not maximizer,floor,ceiling)[0]
                        if(score > bestScore):
                            bestScore = score
                            bestMove = move
                            
                        # Alphabeta bookkeeping:
                        if(bestScore > floor):
                            floor = bestScore   # Constrains children at the next (minimizing) layer to be above this value
                        if(bestScore >= ceiling): # Stop searching any more if it's above the upper limit
                            break
                else:
                    # set to be as high as possible
                    bestScore = float('inf')
                    bestMove = moves[0]
                    for move in moves:
                        if(isPlacing):
                            nextState = self.createNextPlacementState(state,move,icon)
                        else:
                            nextState = self.createNextState(state,size,move)
                        
                        icon = WHITE if icon == BLACK else BLACK
                        
                        score = self.abPruning(icon,nextState,size,layer-1,timer+1,isPlacing,not maximizer,floor,ceiling)[0]
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
        
        return (bestScore, bestMove)
    
#==============================================================================
  
# GameState Class


class Gamestate:
    
    def __init__(self,size):
        self.size = size
        self.whitePieces = []
        self.blackPieces = []
        self.board = self.declareBoard(size)
        
    def declareBoard(self,size):
        board = {}
        calc = (int)((8-size)/2) # in case board has shrunk
        for row in range(calc,size+calc):
            for col in range(calc,size+calc):
                if((row == size+calc-1 and col == size+calc-1) or 
                   (row == size+calc-1 and col == calc) or
                   (row == calc and col == size+calc-1) or 
                   (row == calc and col == calc)):
                    board[col,row] = CORNER
                else:
                    board[col,row] = BLANK
        
        return board
	
    def updateBoardSize(self, size):
        origin = (int)((8-size)/2)
        deletion = []
        for tile in self.board:
            if tile[0] < origin or tile[0] > origin+size-1 or tile[1] < origin or tile[1] > origin+size-1:
                deletion.append(tile)
        for tile in deletion:
            self.board.pop(tile)
    
    def updatePiece(self,size):
        if(size == 6):
            self.whitePieces = [x for x in self.whitePieces if((x[0]>=1 or x[0]<=6) and (x[1]>=1 or x[1]<=6))]
            self.blackPieces = [x for x in self.blackPieces if((x[0]>=1 or x[0]<=6) and (x[1]>=1 or x[1]<=6))]
        elif(size == 4):
            self.whitePieces = [x for x in self.whitePieces if((x[0]>=2 or x[0]<=5) and (x[1]>=2 or x[1]<=5))]
            self.blackPieces = [x for x in self.blackPieces if((x[0]>=2 or x[0]<=5) and (x[1]>=2 or x[1]<=5))]
    # assumes that pos is valid, position is within bound and piece is correct
    # adds a piece, during placing phase
    def addPiece(self, pos, piece):
        self.board[pos] = piece
        self.whitePieces.append(pos) if(piece == WHITE) else self.blackPieces.append(pos)
        
    # removes a piece, if a piece destroys another piece
    def removePiece(self,pos):
        pieceIcon = self.board[pos]
        self.board[pos] = BLANK
        self.whitePieces.remove(pos) if(pieceIcon == WHITE) else self.blackPieces.remove(pos)
        
    # move a piece to a new direction, during moving phase
    def movePiece(self,oldPos,newPos):
        # get the icon of the piece
        if(oldPos in self.board and self.board[oldPos] != BLANK):
            icon = self.board[oldPos]
            self.board[newPos] = icon
            self.board[oldPos] = BLANK
            self.whitePieces.remove(oldPos) if icon == WHITE else self.blackPieces.remove(oldPos)
            self.whitePieces.append(newPos) if icon == WHITE else self.blackPieces.append(newPos)
    
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
    def sumTuples(self,zipped):
        return tuple([sum(x) for x in zipped])
    
    # add kills from shrinking
    def updateKills(self):
        totalPieces = self.whitePieces+self.blackPieces
        for piece in totalPieces:
            enemy = BLACK if self.board[piece] == WHITE else WHITE
            origin = (int)((8-self.size)/2)
			
            # checks x-axis, then y-axis
            for axis in range(0,2):
			
				# killed by surrounding enemies
                if origin < piece[axis] < origin+self.size-1:
                    posAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis]))]
                    negAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))]
                    if (posAxis == CORNER or posAxis == enemy) and (negAxis == CORNER or negAxis == enemy):
                        self.removePiece(piece)
                        break
						
				# killed by board shrinking
                elif (piece[axis] < origin or piece[axis] > origin+self.size-1):
                    #print(piece)
                    self.removePiece(piece)
                    break
                elif (piece[(axis+1)%2] == origin or piece[(axis+1)%2] == origin+self.size-1):
                    #print(piece)
                    self.removePiece(piece)
                    break
	
    # returns score for minimax evaluation of board state
    def eval(self, colour):
        enemy = BLACK if colour == WHITE else WHITE
        playerPieces = self.whitePieces if enemy == BLACK else self.blackPieces
        enemyPieces = self.whitePieces if enemy == WHITE else self.blackPieces
        score = 0;
		
        # Score = Player Defense - Enemy Defense
		# Defense = 5 - Vulnerability (5 = Max Vulnerability) (negative correlation)
        for piece in playerPieces:
            score += 5 - self.calcVulnerability(piece, colour, enemy)
        for piece in enemyPieces:
            score -= 5 - self.calcVulnerability(piece, enemy, colour)
			
        return score
	
    def calcVulnerability(self, piece, colour, enemy):
        vulnerableCount = 0;
        vulnerableSum = 0;
        origin = (int)((8-self.size)/2) # in case board has shrunk
		
        # check vulnerability horizontally and vertically
        for axis in range(0,2):
		
            # piece is safe in that axis is sticking to the edge
            if origin < piece[axis] < origin+self.size-1:
			
                # tiles beside piece
                posAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis]))]
                negAxis = self.board[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))]
				
                # piece is safe in that axis if at least one friendly piece beside, can't be surrounded
                if not (posAxis == colour or negAxis == colour):
                    vulnerableCount += 1
                    # Vulnerability = # of enemy pieces surrounding piece * 0.5
                    # Eg: 0 = no pieces, 0.5 = 1 enemy piece, 1 = killed
                    vulnerableSum += (int(posAxis == CORNER or posAxis == enemy) + int(negAxis == CORNER or negAxis == enemy))*0.5
				
        vulnerableAvg = vulnerableSum/vulnerableCount if vulnerableCount != 0 else 0
        # Level of vulnerability has 3 times higher priority than number of vulnerable axes
        vulnerableWeighted = vulnerableSum + 3*vulnerableAvg
        return vulnerableWeighted
    
    def getSize(self):
        return self.size
    
    def getBoard(self):
        return self.board