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