DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
BLANK, EDGE = '-','X'

class Gamestate:
    
    def __init__(self,size):
        self.currPiecePos = []
        self.enemyPiecePos = []
        self.board = self.declareBoard(8)
        
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
    
    def is_gameover(state):
        piece = ''
        for i in state:
            if(i=='O' or i=='@'):
                if(piece != i):
                    return False
                piece = i
        return True
    
    # get available positions to place a piece for placing phase
    def availablePosition(self,minY):
        availableMoves = []
        for row in range(minY,minY+5+1):
            for col in range(len(self.board[row])):
                if(self.board[row,col] == '-'):
                    availableMoves.append((row,col))
        return availableMoves
    
    # get available moves each piece has in moving phase
    def availableMoves(self,currPos):
        moves = []
        for piece in currPos:
            for direction in DIRECTIONS:
                # a normal move to an adjacent square?
                adjacent_square = (piece[0]+direction[0],piece[1]+direction[1])
                if(adjacent_square in self.board and self.board[adjacent_square] == BLANK):
                    moves.append((piece,adjacent_square))
                    continue # a jump move is not possible in this direction
        
                # if not, how about a jump move to the opposite square?
                opposite_square = (piece[0]+2*direction[0],piece[1]+2*direction[1])
                if(adjacent_square in self.board and self.board[adjacent_square] == BLANK):
                    moves.append((piece,opposite_square))
            
        return moves