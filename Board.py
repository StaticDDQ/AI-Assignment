from constants import *

class Board:
    
    # Initialize board
    def __init__(self, size):
        self.size = size
        self.grid = self.gridInit(size)
    
    # Initialize grid with corners or blanks
    def gridInit(self, size):
        grid = {}
        origin = (int)((INIT_SIZE-size)/2) # In case grid has shrunk
        for col in range(origin, size+origin):
            for row in range(origin, size+origin):
                # Differentiating corners and blanks
                if((row == size+origin-1 and col == size+origin-1) or 
                   (row == size+origin-1 and col == origin) or
                   (row == origin and col == size+origin-1) or 
                   (row == origin and col == origin)):
                    grid[col, row] = CORNER
                else:
                    grid[col, row] = BLANK
        
        return grid
	
    # Shrink grid and make update pieces affected
    def updateGridSize(self, size):
        self.size = size
        origin = (int)((INIT_SIZE-size)/2)
        deletion = []
        
        for tile in self.grid:
            # Set new corners
            if (tile == (origin,origin+size-1) or tile == (origin+size-1,origin) or 
                tile == (origin+size-1,origin+size-1) or tile == (origin,origin)):
                self.grid[tile] = CORNER
            # Delete edge pieces
            elif not(origin+size-1 >= tile[0] >= origin and origin+size-1 >= tile[1] >= origin):
                deletion.append(tile)
        for tile in deletion:
            self.grid.pop(tile)
		
		# first updateKill call just for corner kills first, colour parameter not important
        self.updateKills(WHITE, True)
        self.updateKills(WHITE)
        self.updateKills(BLACK)
    
    # Adds piece to grid, during placing phase
    def addPiece(self, pos, piece):
        self.grid[pos] = piece
        
    # Removes piece
    def removePiece(self, pos):
        self.grid[pos] = BLANK
        
    # Move piece to new tile, during moving phase
    def movePiece(self, oldPos, newPos):
        # get the colour of the piece
        if(oldPos in self.grid and self.grid[oldPos] != BLANK):
            colour = self.grid[oldPos]
            self.grid[newPos] = colour
            self.grid[oldPos] = BLANK
    
    # Return list of all pieces's position; either white, black, or both
    def getPieces(self, colour = "Both"):
        pieces = []
        origin = (int)((INIT_SIZE-self.size)/2) # in case grid has shrunk
        for col in range(origin, origin+self.size):
            for row in range(origin, origin+self.size):
                # Check for both
                if colour == "Both":
                    if self.grid[col, row] == WHITE or self.grid[col, row] == BLACK:
                        pieces.append((col, row))
                # Otherwise check argument colour
                elif self.grid[col, row] == colour:
                    pieces.append((col, row))
        return pieces
		
    # Get all possible positions within appropriate range, for placing phase
    def getAllPositions(self, minY):
        availablePosition = []
        # Find all positions for player to place a piece during placing phase
        for pos in self.grid:
            if(minY <= pos[1] <= minY+INIT_Y_LEN-1 and self.grid[pos] == BLANK):
                availablePosition.append(pos)
        return availablePosition
    
    # Get available moves for a player during movement phase
    def getAvailableMoves(self, colour):
        pieces = self.getPieces(colour)
        moves = []
        for piece in pieces:
            for direction in DIRECTIONS:
                adjacent_square = self.sumTuples(zip(piece, direction))
                opposite_square = self.sumTuples(zip(piece, direction, direction))
				
                # Either single-tile movement...
                if adjacent_square in self.grid:
                    if self.grid[adjacent_square] == BLANK:
                        moves.append((piece,adjacent_square))
        
                # ...or jump over piece
                elif opposite_square in self.grid:
                    if self.grid[opposite_square] == BLANK and self.grid[adjacent_square] in [WHITE, BLACK]:
                        moves.append((piece,opposite_square))
        return moves
    
    # Check board for piece eliminations and remove those
    def updateKills(self, colour, shrink = False):

        totalPieces = self.getPieces(colour)
        enemy = BLACK if colour == WHITE else WHITE
        origin = (int)((INIT_SIZE-self.size)/2)
        
		# In case of shrinking, corner kills by counter-clockwise from top-left
        if shrink:
            for corner in [(origin, origin), (origin, origin+self.size-1), (origin+self.size-1, origin+self.size-1), (origin+self.size-1, origin)]:
                if corner[0] == origin:
                    adjacent = self.sumTuples(zip(corner, RIGHT))
                    opposite = self.sumTuples(zip(corner, RIGHT, RIGHT))
                else:
                    adjacent = self.sumTuples(zip(corner, LEFT))
                    opposite = self.sumTuples(zip(corner, LEFT, LEFT))
                if self.grid[adjacent] != self.grid[opposite]:
                    self.removePiece(adjacent)
                if corner[1] == origin:
                    adjacent = self.sumTuples(zip(corner, DOWN))
                    opposite = self.sumTuples(zip(corner, DOWN, DOWN))
                else:
                    adjacent = self.sumTuples(zip(corner, UP))
                    opposite = self.sumTuples(zip(corner, UP, UP))
                if self.grid[adjacent] != self.grid[opposite]:
                    self.removePiece(adjacent)
		
        else:
            for piece in totalPieces:
                # Checks x-axis, then y-axis
                for axis in range(0,2):
                    
                    # Killed by surrounding enemies
                    if origin < piece[axis] < origin+self.size-1:
                        posAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis]))]
                        negAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))]
                        if (posAxis == CORNER or posAxis == enemy) and (negAxis == CORNER or negAxis == enemy):
                            self.removePiece(piece)
                            break
                            
                    # Killed by grid shrinking
                    elif (piece[axis] < origin or piece[axis] > origin+self.size-1):
                        self.removePiece(piece)
                        break
                    elif (piece[(axis+1)%2] == origin or piece[(axis+1)%2] == origin+self.size-1):
                        self.removePiece(piece)
                        break
    
	# Sums up set of zipped tuples
    def sumTuples(self, zipped):
        return tuple([sum(x) for x in zipped])
    
    # Returns score for minimax evaluation of grid board
    def eval(self, colour, timer):
        enemy = BLACK if colour == WHITE else WHITE
        playerPieces = self.getPieces(colour)
        enemyPieces = self.getPieces(enemy)
        score = 0
        
        # Score = Player Defense - Enemy Defense
        # Defense = 8 - Weighted Vulnerability (8 = Max Weighted Vulnerability) (negative correlation)
        for piece in playerPieces:
            score += MAX_VULNERABILITY - self.calcVulnerability(piece, colour, enemy, timer)
        for piece in enemyPieces:
            score -= MAX_VULNERABILITY - self.calcVulnerability(piece, enemy, colour, timer)
            
        return score
    
    # Calculates vulnerability of certain piece
    def calcVulnerability(self, piece, colour, enemy, timer):
        vulnerableCount = 0;
        vulnerableSum = 0;
        origin = (int)((INIT_SIZE-self.size)/2) # In case grid has shrunk
        
        # Check vulnerability horizontally and vertically
        for axis in range(0,2):
        
            # Piece is safe in that axis if sticking to the edge
            if origin < piece[axis] < origin+self.size-1:
            
                # Tiles beside piece
                posAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis]))]
                negAxis = self.grid[self.sumTuples(zip(piece, DIRECTIONS[axis+2]))]
                
                # Piece is safe in that axis if at least one friendly piece beside, can't be surrounded
                if not (posAxis == colour or negAxis == colour):
                    vulnerableCount += 1
                    # Vulnerability = # of enemy pieces surrounding piece * 0.5
                    # Eg: 0 = no pieces, 0.5 = 1 enemy piece, 1 = killed
                    vulnerableSum += (int(posAxis == CORNER or posAxis == enemy) + int(negAxis == CORNER or negAxis == enemy))*0.5
                
        vulnerableAvg = vulnerableSum/vulnerableCount if vulnerableCount != 0 else 0
        
        # Border danger ranges from 0 to 1, applies only to edge pieces, maximum possible danger = maximum possible vulnerability
        borderDanger = 0
        if MOVEMENT_TIME <= timer < FIRST_SHRINK_TIME and (0 in piece or 7 in piece):
            borderDanger = (timer-MOVEMENT_TIME)/(FIRST_SHRINK_TIME-MOVEMENT_TIME)
        elif FIRST_SHRINK_TIME <= timer < SECOND_SHRINK_TIME and (1 in piece or 6 in piece):
            borderDanger = (timer-FIRST_SHRINK_TIME)/(SECOND_SHRINK_TIME-FIRST_SHRINK_TIME)
        
        # 1:3:4 ratio of priority
        vulnerableWeighted = vulnerableSum + 3*vulnerableAvg + 4*borderDanger
        return vulnerableWeighted