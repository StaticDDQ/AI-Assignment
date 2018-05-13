from copy import deepcopy

WHITE, BLACK, BLANK, CORNER = 'O', '@', '-', 'X'
RIGHT, UP, LEFT, DOWN = (1, 0), (0, -1), (-1, 0), (0, 1)
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]

# Player Class
class Player:
    
    def __init__(self, colour):
        # timer to indicate how close will the grid shrink
        self.timer = 0
        # Y range is (0-5) for white, else (2-7)
        self.minY = 0 if colour == 'white' else 2
        self.colour = WHITE if colour == 'white' else BLACK
        # initate empty game state
        self.board = Board(8)
        # get all positions for placing phase
        self.availablePosition = self.getAllPositions(self.board.grid, self.minY)
    
    def action(self, turns):
        # shrink to size of 6 when it reaches move 128
        if(self.timer == 128+24):
            self.board.updateGridSize(6)
            print("Shrinking for " + self.colour + " in action()")
        # shrink to size of 4 when it reaches move 192
        elif(self.timer == 192+24):
            self.board.updateGridSize(4)
        # during placing phase
        print(self.board.getPieces(BLACK))
        if self.timer < 24:
            move = self.abPruning(self.colour, self.board, self.board.size, 2, self.timer, True)[1]
            self.board.addPiece(move, self.colour)
        # during moving phase
        else:
            move = self.abPruning(self.colour, self.board, self.board.size, 2, self.timer, False)[1]
            self.board.movePiece(move[0], move[1])
        self.timer += 1
        self.board.updateKills()
        return move
    
    def update(self, action):
        # during placing phase
        if self.timer < 24:
            enemy = BLACK if self.colour == WHITE else WHITE
            self.board.addPiece(action, enemy)
        # during moving phase
        else:
            self.board.movePiece(action[0], action[1])
		# update board size if it shrinks
        if(self.timer == 128+24):
            self.board.updateGridSize(6)
            print("Shrinking for " + self.colour + " in update()")
        elif(self.timer == 192+24):
            self.board.updateGridSize(4)
        self.timer += 1
        self.board.updateKills()
        #print(self.board.getPieces(BLACK))
    
    # get all possible positions within appropriate range, for placing phase
    def getAllPositions(self, grid, minY):
        availablePosition = []
        # find all positions for player to place a piece during placing phase
        for pos in grid:
            if(minY <= pos[1] <= minY+5 and grid[pos] == BLANK):
                availablePosition.append(pos)
        return availablePosition
    
    # make a copy of the next state when it makes a move
    def createNextState(self, state, size, move):
        # copy current state
        tempState = deepcopy(state)
        # check if the grid shrinks
        # move piece to appropriate location
        tempState.movePiece(move[0], move[1])
        tempState.updateKills()
        if(tempState.size != size):
            tempState.updateGridSize(size)
            tempState.updateKills()
        return tempState
        
    # make a next state during placing phase
    def createNextPlacementState(self, state, pos, tile):
        # copy current state and add a piece
        tempState = deepcopy(state)
        tempState.addPiece(pos, tile)
        tempState.updateKills()
        return tempState
    
    # minimax algorithm for the moving phase
    def abPruning(self, colour, state, size, layer, timer, isPlacing ,maximizer=True, alpha=float("-inf"), beta=float("inf")):
        
        # a-b pruning
        floor = alpha
        ceiling = beta
        
        # get all moves for current player
        if(isPlacing):
            self.minY = 0 if colour == WHITE else 2
            moves = self.getAllPositions(state.grid,self.minY)
        else:
            moves = state.availableMoves(colour)
        # shrink grid if timer reaches certain value
        if(timer >= 128+24):
            size = 6
        if(timer >= 192+24):
            size = 4
        
        # if there are available moves
        if(len(moves) > 0):
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
                            nextState = self.createNextPlacementState(state, move, colour)
                        else:
                            nextState = self.createNextState(state, size, move)
                        # switch players
                        colour = WHITE if colour == BLACK else BLACK
                        
                        score = self.abPruning(colour, nextState, size, layer-1, timer+1, isPlacing, not maximizer, floor, ceiling)[0]
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
                            nextState = self.createNextPlacementState(state, move, colour)
                        else:
                            nextState = self.createNextState(state,size,move)
                        
                        colour = WHITE if colour == BLACK else BLACK
                        
                        score = self.abPruning(colour, nextState, size, layer-1, timer+1, isPlacing, not maximizer, floor, ceiling)[0]
                        if(score < bestScore):
                            bestScore = score
                            bestMove = move
                            
                        if(bestScore < ceiling):
                            ceiling = bestScore   # Constrains children at the next (maximizing) layer to be below this value
                        if(bestScore <= floor): # Stop searching any more if it's below the lower limit
                            break
            else:
                bestScore = state.eval(colour)
                bestMove = None
        else:
            bestScore = state.eval(colour)
            bestMove = None
        
        return (bestScore, bestMove)
    
#==============================================================================
  
# GameState Class


class Board:
    
    def __init__(self, size):
        self.size = size
        self.grid = self.gridInit(size)
        
    def gridInit(self, size):
        grid = {}
        calc = (int)((8-size)/2) # in case grid has shrunk
        for row in range(calc,size+calc):
            for col in range(calc,size+calc):
                if((row == size+calc-1 and col == size+calc-1) or 
                   (row == size+calc-1 and col == calc) or
                   (row == calc and col == size+calc-1) or 
                   (row == calc and col == calc)):
                    grid[col,row] = CORNER
                else:
                    grid[col,row] = BLANK
        
        return grid
    
    def updateGridSize(self, size):
        self.size = size
        origin = (int)((8-size)/2)
        deletion = []
        for tile in self.grid:
            if (tile == (origin,origin+size-1) or tile == (origin+size-1,origin) or 
                tile == (origin+size-1,origin+size-1) or tile == (origin,origin)):
                self.grid[tile] = CORNER
            elif not(origin+size-1 >= tile[0] >= origin and origin+size-1 >= tile[1] >= origin):
                deletion.append(tile)
        for tile in deletion:
            self.grid.pop(tile)

    
    # adds a piece, during placing phase
    def addPiece(self, pos, piece):
        self.grid[pos] = piece
        
    # removes a piece, if a piece destroys another piece
    def removePiece(self, pos):
        self.grid[pos] = BLANK
        
    # move a piece to a new direction, during moving phase
    def movePiece(self, oldPos, newPos):
        # get the colour of the piece
        if(oldPos in self.grid and self.grid[oldPos] != BLANK):
            colour = self.grid[oldPos]
            self.grid[newPos] = colour
            self.grid[oldPos] = BLANK
    
    # return list of all pieces's position, can search both, white, or black
    def getPieces(self, colour = "Both"):
        pieces = []
        origin = (int)((8-self.size)/2) # in case grid has shrunk
        for col in range(origin, origin+self.size):
            for row in range(origin, origin+self.size):
                # if want to search both black and white pieces
                if colour == "Both":
                    if self.grid[col, row] == WHITE or self.grid[col, row] == BLACK:
                        pieces.append((col, row))
                elif self.grid[col, row] == colour:
                    pieces.append((col, row))
        return pieces
    
    # get available moves each piece has in moving phase
    def availableMoves(self, colour):
        currPos = self.getPieces(colour)
        moves = []
        for piece in currPos:
            for direction in DIRECTIONS:
                # a normal move to an adjacent square
                adjacent_square = self.sumTuples(zip(piece, direction))
                if(adjacent_square in self.grid and self.grid[adjacent_square] == BLANK):
                    moves.append((piece,adjacent_square))
                    continue # a jump move is not possible in this direction
        
                # if not, jump another square ahead
                opposite_square = self.sumTuples(zip(piece, direction, direction))
                if(adjacent_square in self.grid and self.grid[adjacent_square] == BLANK):
                    moves.append((piece,opposite_square))
        return moves
    
    # sums up set of zipped tuples
    def sumTuples(self, zipped):
        return tuple([sum(x) for x in zipped])
    
    # add kills from shrinking
    def updateKills(self):
        totalPieces = self.getPieces()
        for piece in totalPieces:
            enemy = BLACK if self.grid[piece] == WHITE else WHITE
            origin = (int)((8-self.size)/2)
            
            # checks x-axis, then y-axis
            for axis in range(0,2):
                # killed by surrounding enemies
                if origin < piece[axis] < origin+self.size-1:
                    posAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis]))]
                    negAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))]
                    if (posAxis == CORNER or posAxis == enemy) and (negAxis == CORNER or negAxis == enemy):
                        self.removePiece(piece)
                        break
                        
                # killed by grid shrinking
                elif (piece[axis] < origin or piece[axis] > origin+self.size-1):
                    self.removePiece(piece)
                    break
                elif (piece[(axis+1)%2] == origin or piece[(axis+1)%2] == origin+self.size-1):
                    self.removePiece(piece)
                    break
    
    # returns score for minimax evaluation of grid state
    def eval(self, colour):
        enemy = BLACK if colour == WHITE else WHITE
        playerPieces = self.getPieces(colour)
        enemyPieces = self.getPieces(enemy)
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
        origin = (int)((8-self.size)/2) # in case grid has shrunk
        
        # check vulnerability horizontally and vertically
        for axis in range(0,2):
        
            # piece is safe in that axis is sticking to the edge
            if origin < piece[axis] < origin+self.size-1:
            
                # tiles beside piece
                posAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis]))]
                negAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))]
                
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