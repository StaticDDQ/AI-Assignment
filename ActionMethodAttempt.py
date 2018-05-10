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
    def nextState(state,move):
        # copy current state
        tempState = deepcopy(state)
        tempState.movePiece(move[0],move[1])
        return tempState
    
    # minimax algorithm for the moving phase
    def Minimax(self,state,size):
        # get all moves for each piece
        moves = state.availableMoves(self.currPiecePos)
        # set initial move as best move
        bestMove = moves[0]
        # set lowest possible score
        bestScore = float('-inf')
        # iterate through each move, apply each move to a state and get
        # the score, if score is the highest, return best move
        for move in moves:
            # apply move to a state, returns a copy
            clone = self.nextState(state,move)
            # use that copy to determine the score
            score = self.min_play(clone,size)
            if score < bestScore:
                bestMove = move
                bestScore = score
        return bestMove
        
    def min_play(self,state,size):
        if(state.is_gameover(state)):
            return self.evaluate(state)
        moves = self.availableMoves(state,self.enemyPiecePos)
        best_score = float('inf')
        for move in moves:
            clone = self.nextState(state,move)
            score = self.max_play(clone,size)
            if score < best_score:
                best_score = score
        return best_score
    
    def max_play(self,state,size):
        if(state.is_gameover(state)):
            return self.evaluate(state)
        moves = self.availableMoves(state,self.currPiecePos)
        best_score = float('-inf')
        for move in moves:
            clone = self.nextState(state,move)
            score = self.min_play(clone,size)
            if score > best_score:
                best_score = score
        return best_score

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
    def is_gameover(self,state):
        piece = ''
        for i in state:
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
        
    # removes a piece, if a piece destroys another piece
    def removePiece(self,pos):
        self.board[pos[0],pos[1]] = BLANK
        
    # move a piece to a new direction, during moving phase
    def movePiece(self,oldPos,newPos):
        # get the icon of the piece
        icon = self.board[oldPos[0],oldPos[1]]
        self.board[newPos[0],newPos[1]] = icon
        self.board[oldPos[0],oldPos[1]] = BLANK
    
    # get available moves each piece has in moving phase
    def availableMoves(self,currPos):
        moves = []
        for piece in currPos:
            for direction in DIRECTIONS:
                # a normal move to an adjacent square
                adjacent_square = (piece[0]+direction[0],piece[1]+direction[1])
                if(adjacent_square in self.board and self.board[adjacent_square] == BLANK):
                    moves.append((piece,adjacent_square))
                    continue # a jump move is not possible in this direction
        
                # if not, jump another square ahead
                opposite_square = (piece[0]+2*direction[0],piece[1]+2*direction[1])
                if(adjacent_square in self.board and self.board[adjacent_square] == BLANK):
                    moves.append((piece,opposite_square))
        return moves
    
    def getWinner(self):
        return self.winner
    