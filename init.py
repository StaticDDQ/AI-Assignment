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
        # initiate empty board
        self.board = {}
        for row in range(8):
            for col in range(8):
                if((row == 7 and col == 7) or (row == 7 and col == 0) or
                   (row == 0 and col == 7) or (row == 0 and col == 0)):
                    self.board[row,col] = EDGE
                else:
                    self.board[row,col] = BLANK
        