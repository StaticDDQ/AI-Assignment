from board import Board
from constants import *
from strategies import *

# Player Class
class Player:
    
	# Initialize player with black or white
    def __init__(self, colour):
        
        # timer to indicate how close will the grid shrink
        self.timer = 0
        # Y range is (0-5) for white, else (2-7)
        self.minY = WHITE_MIN_Y if colour == 'white' else BLACK_MIN_Y
        self.colour = WHITE if colour == 'white' else BLACK
        self.enemy = BLACK if colour == 'white' else WHITE
        # Initialize empty game board
        self.board = Board(INIT_SIZE)
    
	# Returns either tile to place piece or move to make
    def action(self, turns):
        
        # Update board shrinking has priority
        if(self.timer == FIRST_SHRINK_TIME):
            self.board.updateGridSize(FIRST_SHRINK_SIZE)
        elif(self.timer == SECOND_SHRINK_TIME):
            self.board.updateGridSize(SECOND_SHRINK_SIZE)
			
        # During placement phase
        if self.timer < MOVEMENT_TIME:
            move = minimax(self.colour, self.colour, self.board, self.board.size, LAYERS, self.timer, True)[1]
            self.board.addPiece(move, self.colour)
        # During movement phase
        else:
            move = minimax(self.colour, self.colour, self.board, self.board.size, LAYERS, self.timer, False)[1]
            if move is not None:
                self.board.movePiece(move[0], move[1])
        
        self.timer += 1
        self.board.updateKills(self.enemy)
        self.board.updateKills(self.colour)
        return move
    
	# Takes opponent's action and updates board
    def update(self, action):
        
        # Update board shrinking has priority
        if(self.timer == FIRST_SHRINK_TIME):
            self.board.updateGridSize(FIRST_SHRINK_SIZE)
        elif(self.timer == SECOND_SHRINK_TIME):
            self.board.updateGridSize(SECOND_SHRINK_SIZE)
        
        # During placement phase
        if self.timer < MOVEMENT_TIME:
            self.board.addPiece(action, self.enemy)
        # During movement phase
        else:
            self.board.movePiece(action[0], action[1])
        
        self.timer += 1
        self.board.updateKills(self.colour)
        self.board.updateKills(self.enemy)