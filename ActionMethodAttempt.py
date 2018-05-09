

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
    
    def action(self, turns):
        # first turn for player
        if(turns == 0):
            return self.placeFirst()
        # during placing phase
        elif(0<turns<24):
            move = self.gameState.availablePosition(self.minY)
            self.timer+= 1
        # during moving phase
        else:
            move = self.Minimax(self.gameState)
            self.timer+= 1
            
        return move
    
    # method in cases where player moves first, called once
    def placeFirst(self):
        return 1
    
    # create a state where a piece is moved to a specific direction
    def applyMove(board,prevMove,newMove,piece):
        copy = board.copy();
        copy[prevMove] = BLANK
        copy[newMove] = piece
        return copy
    
    # minimax algorithm for the moving phase
    def Minimax(self,state):
        moves = state.availableMoves(self.currPiecePos)
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
