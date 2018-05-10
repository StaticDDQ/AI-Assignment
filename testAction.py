from copy import deepcopy
# Player Class
class Player:
    
    def __init__(self, colour):
        # suppose to store all current positions of player and enemy's pieces
        self.currPiecePos = []
        self.enemyPiecePos = []
        # timer to indicate how close will the board shrink
        self.timer = 0
        # Y range is (0-5) for white, else (2-7)
        self.minY = 0 if colour == 'white' else 2
        self.icon = 'O' if colour == 'white' else '@'
        self.enemy = '@' if self.icon == 'O' else 'O'
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
            move = self.gameState.availablePosition(self.minY)

        # during moving phase
        else:
            move = self.Minimax(self.gameState)
            
        return move
    
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
    def Minimax(self,state,size,layer,timer,maximizer=True,alpha=float("-inf"), beta=float("inf")):
        
        # at gameover state
        if(state.isGameover(state)):
            return self.evaluate(state)
        
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
                        score = self.minimax(nextState,size,layer-1,timer+1,not maximizer,floor,ceiling)[0]
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
                        score = self.minimax(nextState,size,layer-1,timer+1,not maximizer,floor,ceiling)[0]
                        if(score < bestScore):
                            bestScore = score
                            bestMove = move
                            
                        if(bestScore < ceiling):
                            ceiling = bestScore   # Constrains children at the next (maximizing) layer to be below this value
                        if(bestScore <= floor): # Stop searching any more if it's below the lower limit
                            break
            else:
                bestScore = self.evaluate(state)
                bestMove = None
        else:
            bestScore = self.evaluate(state)
            bestMove = None
        
        return bestScore, bestMove

    # rough evaluation function
    def evaluate(self,state):
        return float('inf') if(state.getWinner() == self.icon) else float('-inf')
    
#==============================================================================
  
# GameState Class
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
BLANK, EDGE = '-','X'

class Gamestate:
    
    def __init__(self,size):
        self.board = self.declareBoard(size)
        self.winner = ''
        self.currWhitePos = []
        self.currBlackPos = []
        # True if it's white's turn, else black
        self.movingPlayer = True
        
    def declareBoard(self,size):
        self.board = {}
        calc = (int)((8-size)/2)
        for row in range(calc,size+calc):
            for col in range(calc,size+calc):
                if((row == size+calc-1 and col == size+calc-1) or 
                   (row == size+calc-1 and col == size+calc-1) or
                   (row == calc and col == size-1) or 
                   (row == calc and col == calc)):
                    self.board[col,row] = EDGE
                else:
                    self.board[col,row] = BLANK
    
    # check if the game has ended
    def isGameover(self,state):
        if(len(self.currWhitePos) > 0 and len(self.currWhitePos) > 0):
            return False
        self.winner = 'O' if len(currBlackPos) == 0 else  self.winner = '@'
        return True
    
    # assumes that pos is valid, position is within bound and piece is correct
    # adds a piece, during placing phase
    def addPiece(self,pos, piece):
        self.board[pos[0],pos[1]] = piece
        self.currWhitePos.append(piece) if piece == 'O' else self.currBlackPos.append(piece)
        
    # removes a piece, if a piece destroys another piece
    def removePiece(self,pos):
        piece = self.board[pos[0],pos[1]]
        self.board[pos[0],pos[1]] = BLANK
        self.currWhitePos.remove(piece) if piece == 'O' else self.currBlackPos.remove(piece)
        
    # move a piece to a new direction, during moving phase
    def movePiece(self,oldPos,newPos):
        # get the icon of the piece
        icon = self.board[oldPos[0],oldPos[1]]
        self.board[newPos[0],newPos[1]] = icon
        self.board[oldPos[0],oldPos[1]] = BLANK
    
    # get available moves each piece has in moving phase
    def availableMoves(self):
        moves = []
        currPos = self.currWhitePos if self.movingPlayer else self.currBlackPos
        self.movingPlayer = not self.movingPlayer
        
        for piece in currPos:
            for direction in DIRECTIONS:
                # a normal move to an adjacent square
                makeMove = (piece[0]+direction[0],piece[1]+direction[1])
                if(makeMove in self.board and self.board[makeMove] == BLANK):
                    moves.append((piece,makeMove))
                    continue # a jump move is not possible in this direction
        
                # if not, jump another square ahead
                makeMove = (piece[0]+2*direction[0],piece[1]+2*direction[1])
                if(makeMove in self.board and self.board[makeMove] == BLANK):
                    moves.append((piece,makeMove))
        return moves
    
    def getWinner(self):
        return self.winner