WHITE, BLACK, BLANK, CORNER = 'O', '@', '-', 'X'
RIGHT, UP, LEFT, DOWN = (1, 0), (0, -1), (-1, 0), (0, 1)
DIRECTIONS = [RIGHT, UP, LEFT, DOWN]
INIT_Y_LEN = 6 # Maximum y-range for placement phase
WHITE_MIN_Y, BLACK_MIN_Y = 0, 2
INIT_SIZE, FIRST_SHRINK_SIZE, SECOND_SHRINK_SIZE = 8, 6, 4
MOVEMENT_TIME, FIRST_SHRINK_TIME, SECOND_SHRINK_TIME = 24, 24+128, 24+192
LAYERS = 2 # Layers for minimax to traverse
MAX_VULNERABILITY = 8