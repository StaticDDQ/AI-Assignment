DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
BLANK, EDGE = '-','X'

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
        # initiate empty board
        self.board = {}
        for row in range(8):
            for col in range(8):
                if((row == 7 and col == 7) or (row == 7 and col == 0) or
                   (row == 0 and col == 7) or (row == 0 and col == 0)):
                    self.board[row,col] = EDGE
                else:
                    self.board[row,col] = BLANK
    
    def action(self, turns):
        # first turn for player
        if(turns == 0):
            return self.placeFirst()
        # during placing phase
        elif(0<turns<24):
            move = self.availablePosition(self.board,self.minY)
            self.timer+= 1
        # during moving phase
        else:
            move = self.Minimax(self.board)
            self.timer+= 1
            
        return move
    
    # method in cases where player moves first, called once
    def placeFirst(self):
        return 1
    
    # get available positions to place a piece for placing phase
    def availablePosition(board,minY):
        availableMoves = []
        for row in range(minY,minY+5+1):
            for col in range(len(board[row])):
                if(board[row,col] == '-'):
                    availableMoves.append((row,col))
        return availableMoves
    
    # get available moves each piece has in moving phase
    def availableMoves(board,currPos):
        moves = []
        for piece in currPos:
            for direction in DIRECTIONS:
                # a normal move to an adjacent square?
                adjacent_square = (piece[0]+direction[0],piece[1]+direction[1])
                if(adjacent_square in board and board[adjacent_square] == BLANK):
                    moves.append((piece,adjacent_square))
                    continue # a jump move is not possible in this direction
        
                # if not, how about a jump move to the opposite square?
                opposite_square = (piece[0]+2*direction[0],piece[1]+2*direction[1])
                if(adjacent_square in board and board[adjacent_square] == BLANK):
                    moves.append((piece,opposite_square))
            
        return moves
    
    # create a state where a piece is moved to a specific direction
    def applyMove(board,prevMove,newMove,piece):
        copy = board.copy();
        copy[prevMove] = BLANK
        copy[newMove] = piece
        return copy
    
    # minimax algorithm for the moving phase
    def Minimax(self,board):
        moves = self.availableMoves(board,self.currPiecePos)
        bestMove = moves[0]
        bestScore = float('-inf')
        for move in moves:
            clone = self.applyMove(board,move[0],move[1],self.icon)
            score = self.min_play(clone)
            if score < bestScore:
                bestMove = move
                bestScore = score
        return bestMove
        
    def min_play(self,state):
        if(self.is_gameover(state)):
            return evaluate(game_state)
        moves = self.availableMoves(state,self.enemyPiecePos)
        best_score = float('inf')
        for move in moves:
            clone = self.applyMove(state,move[0],move[1],self.enemys)
            score = self.max_play(clone)
            if score < best_score:
                best_score = score
        return best_score
    
    def max_play(self,state):
        if(self.is_gameover(state)):
            return evaluate(game_state)
        moves = self.availableMoves(state,self.currPiecePos)
        best_score = float('-inf')
        for move in moves:
            clone = self.applyMove(state,move[0],move[1],self.icon)
            score = self.min_play(clone)
            if score > best_score:
                best_score = score
        return best_score
    
    def is_gameover(state):
        piece = ''
        for i in state:
            if(i=='O' or i=='@'):
                if(piece != i):
                    return False
                piece = i
        return True
            