from copy import deepcopy
from constants import *

# Minimax algorithm for movement phase
def minimax(player, colour, board, size, layer, timer, isPlacing ,maximizer=True, alpha=float("-inf"), beta=float("inf")):
   
    # a-b pruning
    floor = alpha
    ceiling = beta
    
    # Get all moves for current player
    if(isPlacing):
        minY = WHITE_MIN_Y if colour == WHITE else BLACK_MIN_Y
        moves = board.getAllPositions(minY)
    else:
        moves = board.getAvailableMoves(colour)
    # Shrink grid if timer reaches certain value
    if(timer >= FIRST_SHRINK_TIME):
        size = FIRST_SHRINK_SIZE
    if(timer >= SECOND_SHRINK_TIME):
        size = SECOND_SHRINK_SIZE
    
    # If there are available moves
    if(len(moves) > 0):
        # If there is still a layer in the tree
        if(layer > 0):
            # If current player is a Maximiser
            if(maximizer):
                # Set to be as low as possible
                bestScore = float('-inf')
                bestMove = moves[0]
                for move in moves:
                    # Create next board
                    if(isPlacing):
                        nextBoard = createNextPlacementBoard(board, move, colour)
                    else:
                        nextBoard = createNextBoard(board, size, move, colour)
                    # Switch players
                    colour = WHITE if colour == BLACK else BLACK
                    
                    score = minimax(player, colour, nextBoard, size, layer-1, timer+1, isPlacing, not maximizer, floor, ceiling)[0]
                    if(score > bestScore):
                        bestScore = score
                        bestMove = move
                        
                    # a-b bookkeeping
                    if(bestScore > floor):
                        floor = bestScore
                    if(bestScore >= ceiling):
                        break
            else:
                # Set to be as high as possible
                bestScore = float('inf')
                bestMove = moves[0]
                for move in moves:
                    if(isPlacing):
                        nextBoard = createNextPlacementBoard(board, move, colour)
                    else:
                        nextBoard = createNextBoard(board,size,move,colour)
                    
                    colour = WHITE if colour == BLACK else BLACK
                    
                    score = minimax(player, colour, nextBoard, size, layer-1, timer+1, isPlacing, not maximizer, floor, ceiling)[0]
                    if(score < bestScore):
                        bestScore = score
                        bestMove = move
                        
                    if(bestScore < ceiling):
                        ceiling = bestScore
                    if(bestScore <= floor):
                        break
        else:
            bestScore = board.eval(player, timer)
            bestMove = None
    else:
        bestScore = board.eval(player, timer)
        bestMove = None
    
    return (bestScore, bestMove)
	
# Create next board for movement phase
def createNextBoard(board, size, move, colour):
    # Copy current board
    tempBoard = deepcopy(board)
    # move piece to appropriate location
    if move is not None:
        tempBoard.movePiece(move[0], move[1])
    tempBoard.updateKills(colour)
	# Check if the grid shrinks
    if(tempBoard.size != size):
        tempBoard.updateGridSize(size)
    return tempBoard
    
# Create next board for placement phase
def createNextPlacementBoard(board, pos, colour):
    # Copy current board and add a piece
    tempBoard = deepcopy(board)
    tempBoard.addPiece(pos, colour)
    enemy = WHITE if colour == BLACK else WHITE
    tempBoard.updateKills(enemy)
    tempBoard.updateKills(colour)
    return tempBoard