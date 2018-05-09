WHITE, BLACK = '-','X','O','@'

class Player:
    
    def __init__(self, colour):
        # suppose to store all current positions of player and enemy's pieces
        self.currPiecePos = []
        self.enemyPiecePos = []
        # timer to indicate how close will the board shrink
        self.timer = 0
        # Y range is (0-5) for white, else (2-7)
        self.minY = 0 if colour == 'white' else 2
        self.icon = WHITE if colour == 'white' else BLACK
        self.enemy = BLACK if self.icon == WHITE else WHITE
        # initate empty game state
        self.gameState = Gamestate(8)
        