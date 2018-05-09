

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
        self.availablePosition = getAllPositions(self.gameState.getBoard(),self.minY)
    
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
    
    # minimax algorithm for the moving phase
    def Minimax(self,state):
        moves = state.availableMoves(self.currPiecePos)
        bestMove = moves[0]
        bestScore = float('-inf')
        for move in moves:
            clone = # create a copy of the state where player moves
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
            clone = # create copy of an enemy moving a piece
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
            clone = # create copy of the player moving a piece
            score = self.min_play(clone)
            if score > best_score:
                best_score = score
        return best_score

    def evaluate(state):
        