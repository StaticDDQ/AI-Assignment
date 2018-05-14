"""
Strategy class for project B: Artificial Intelligence
@authors: Axel Bachtiar and Robby Ilman
"""

from random import randint
import Piece
import copy


class RandomStrategy:
    """
    Class that implements our random strategy. Our most basic strategy
    """

    @staticmethod
    def choose_placing(board, min_row, max_row):
        """
        Choose a square to place depending on RNG
        :param board:
        :param min_row:
        :param max_row:
        :return: square to place our piece
        """
        while True:
            col = randint(0, 7)
            row = randint(min_row, max_row)
            if board.get_board()[col][row].get_type() == "-":
                break
        return col, row

    @staticmethod
    def choose_move(total_available_moves, board, my_pieces):
        """
        Choose a move using RNG
        :param total_available_moves:
        :param board:
        :param my_pieces:
        :return: Action to be made
        """
        if total_available_moves > 0:
            piece_to_move = randint(0, len(my_pieces) - 1)
            counter = 0
            got_a_move = False
            while True:
                for col, row in my_pieces:
                    initial_coordinate = (col, row)
                    if counter == piece_to_move:
                        if len(my_pieces[initial_coordinate].moves(board)) == 0:
                            counter = 0
                            piece_to_move = (piece_to_move + 1) % len(my_pieces)
                        else:
                            piece = my_pieces[initial_coordinate]
                            got_a_move = True
                            break
                    counter = (counter + 1) % len(my_pieces)
                if got_a_move:
                    move_direction = randint(0, len(piece.moves(board)) - 1)
                    new_coordinate = piece.moves(board)[move_direction]
                    return initial_coordinate, new_coordinate
                else:
                    counter = 0
                    piece_to_move = 0
        else:
            return None, None


class TurtleStrategy:
    """
    Class that implements the strategy we chose to use. Our strategy revolves around playing safe and trying to take
    control of the 4 squares in the middle of the game board
    """

    @staticmethod
    def choose_placing(board, my_pieces, enemy_pieces, min_row, max_row, my_char):
        """
        Choose a square to place. Try to place in the middle if it won't lead to our piece's death, or else, just make
        sure to place in a square that won't endanger our piece and next to our ally pieces if possible
        :param board:
        :param my_pieces:
        :param enemy_pieces:
        :param min_row:
        :param max_row:
        :param my_char:
        :return: The action to be made
        """
        # List for the coordinates of the middle squares
        _middle_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]

        # Check if we are able to kill an opponent straight away, if we can, we do so
        for coord in enemy_pieces:
            if board.next_to_opponent(coord[0], coord[1], 0, 1) or board.next_to_opponent(coord[0], coord[1], 1, 0):
                target_coord = board.target_square_to_kill_or_protect(coord[0], coord[1], min_row, max_row)
                if target_coord[0] is not None:
                    return target_coord

        # Check if our piece is about to be killed by the opponent and try to protect by placing our piece
        # on the opposite square
        for coord in my_pieces:
            if board.next_to_opponent(coord[0], coord[1], 0, 1) or board.next_to_opponent(coord[0], coord[1], 1, 0):
                target_coord = board.target_square_to_kill_or_protect(coord[0], coord[1], min_row, max_row)
                if target_coord[0] is not None:
                    return target_coord

        # We know we will always get a square during the placing stage
        while True:
            got_a_place = False
            enemy_in_middle_4 = 0
            my_piece_in_middle_4 = 0

            # Check if there are enemy pieces in the middle of the board
            for coord in _middle_squares:
                if board.is_enemy(my_char, coord):
                    enemy_in_middle_4 += 1
                elif board.get_piece_at(coord).get_type() == my_char:
                    my_piece_in_middle_4 += 1

            # Check if we have full control of the 4 middle squares
            if my_piece_in_middle_4 == 4:
                middle_control = True
            else:
                middle_control = False

            # Try to take control of the middle of the board if there are no enemy pieces there
            if enemy_in_middle_4 == 0 or my_piece_in_middle_4 > 0:
                for col_test, row_test in _middle_squares:
                    if board.get_board()[col_test][row_test].get_type() == "-":
                        if not board.will_be_vulnerable_placing(my_char, col_test, row_test):
                            got_a_place = True
                            col = col_test
                            row = row_test
                            break

            # If there are no enemy pieces to kill, we always place next to our existing pieces and make sure it will
            # not die this turn or the upcoming turn
            if not got_a_place:
                # If we have control of the middle squares, we try to place our pieces around it
                if middle_control:
                    for coord in my_pieces:
                        if coord in _middle_squares:
                            safe_squares = board.non_vulnerable_adjacent(my_char, coord[0], coord[1])
                            if len(safe_squares) > 0:
                                return safe_squares[0]
                for coord in my_pieces:
                    safe_squares = board.non_vulnerable_adjacent(my_char, coord[0], coord[1])
                    for square in safe_squares:
                        if min_row <= square[1] <= max_row:
                            return square

                # If there are no safe squares around our pieces, then we randomly choose a square, but making sure
                # our piece will not instantly die or get killed in the upcoming turn
                col = randint(0, 7)
                row = randint(min_row, max_row)
                if board.get_board()[col][row].get_type() == "-" and \
                        not board.will_be_vulnerable_placing(my_char, col, row):
                    break
            if got_a_place:
                break
        return col, row

    @staticmethod
    def choose_move(total_available_moves, board, my_pieces, my_char, enemy_pieces, min_row, max_row, next_shrink):
        """
        Choose a move to be made depending on the current state of the board. Mainly revolves around playing safe and
        try to win by taking control of the middle of the board
        :param total_available_moves:
        :param board:
        :param my_pieces:dict of our pieces (and coordinates for it)
        :param my_char:
        :param enemy_pieces: dict of enemy pieces (and coordinates for it)
        :param min_row:
        :param max_row:
        :param next_shrink: Turns to next shrink
        :return: The action to be made
        """

        # The 4 middle squares
        _middle_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        middle_control = True
        pieces_vulnerable_to_shrink = []

        if total_available_moves > 0:
            # Check if we are able to kill an opponent straight away, if we can, we do so
            for coord in enemy_pieces:
                if board.next_to_opponent(coord[0], coord[1], 0, 1) or board.next_to_opponent(coord[0], coord[1], 1, 0):
                    target_coord = board.target_square_to_kill_or_protect(coord[0], coord[1], min_row, max_row)
                    if target_coord[0] is not None:
                        initial_coordinate = board.can_move_for_kill_protect(target_coord, my_pieces)
                        if initial_coordinate is not None:
                            return initial_coordinate, target_coord

            # Count the number of pieces that are on the edge of the board (or in the potential new corners), if the
            # number of piece in the edge is greater than or equal to the number of turns until the next shrink of the
            # board, we try to move it to safety, if it is going to be killed anyway when it moves, then we just ignore
            for col, row in my_pieces:
                if board.eliminated_by_shrink(col, row):
                    pieces_vulnerable_to_shrink.append((col, row))
            if len(pieces_vulnerable_to_shrink) >= next_shrink:
                moves_to_safety = []
                for coord in pieces_vulnerable_to_shrink:
                    possible_moves = my_pieces[coord].moves(board)
                    for possible_move in possible_moves:
                        if not board.eliminated_by_shrink(possible_move[0], possible_move[1]):
                            moves_to_safety.append((coord, possible_move))
                for possible_action in moves_to_safety:
                    if not board.will_be_vulnerable_moving(my_char, possible_action[1][0], possible_action[1][0],
                                                           enemy_pieces):
                        return possible_action

            # Check if one of our pieces are vulnerable and we can still protect it with another piece that is 1 square
            # away
            for coord in my_pieces:
                if board.next_to_opponent(coord[0], coord[1], 0, 1) or board.next_to_opponent(coord[0], coord[1], 1, 0):
                    target_coord = board.target_square_to_kill_or_protect(coord[0], coord[1], min_row, max_row)
                    if target_coord[0] is not None:
                        initial_coordinate = board.can_move_for_kill_protect(target_coord, my_pieces)
                        if initial_coordinate is not None:
                            return initial_coordinate, target_coord
                    else:
                        for destination_coordinate in my_pieces[coord].moves(board):
                            if not board.will_be_vulnerable_moving(my_char, coord[0], coord[1], enemy_pieces):
                                return coord, destination_coordinate

            # Check if we have control of the middle of the board
            my_middle_pieces = 0
            enemy_middle_pieces = 0
            for coord in _middle_squares:
                if board.get_piece_at(coord).get_type() == my_char:
                    my_middle_pieces += 1
                elif board.get_piece_at(coord).get_type() == board.targets(my_char):
                    enemy_middle_pieces += 1
            if my_middle_pieces < enemy_middle_pieces:
                middle_control = False

            # If there is a piece that is right outside of the middle squares and can enter without being eliminated
            # either immediately or next turn, we do so
            if middle_control:
                for target_coord in _middle_squares:
                    if board.get_piece_at(target_coord).get_type() != my_char and \
                            board.will_be_vulnerable_moving(my_char, target_coord[0], target_coord[1], enemy_pieces):
                        for coord in my_pieces:
                            if coord not in _middle_squares:
                                piece = board.get_piece_at(coord)
                                for move in piece.moves(board):
                                    if move == target_coord:
                                        return piece.coord, target_coord

            piece_to_move = randint(0, len(my_pieces) - 1)
            initial_check = piece_to_move
            counter = 0
            got_a_move = False
            vulnerable_moves = 0
            middle_break_moves = 0
            # Keep iterating until we find a move, since we know that we have available moves we can safely loop until
            # we find one
            while True:
                if counter != 0 and initial_check == piece_to_move and middle_control:
                    middle_control = False

                for col, row in my_pieces:
                    initial_coordinate = (col, row)
                    if middle_control and initial_coordinate in _middle_squares and \
                            middle_break_moves + vulnerable_moves <= total_available_moves:
                        middle_break_moves += len(my_pieces[(col, row)].moves(board))
                        break
                    if counter == piece_to_move:
                        if len(my_pieces[initial_coordinate].moves(board)) == 0:
                            counter = 0
                            piece_to_move = (piece_to_move + 1) % len(my_pieces)
                        else:
                            if not board.will_be_vulnerable_moving(my_char, col, row, enemy_pieces) or \
                                    vulnerable_moves + middle_break_moves >= total_available_moves:
                                piece = my_pieces[initial_coordinate]
                                got_a_move = True
                                break
                            else:
                                vulnerable_moves += 1
                    counter = (counter + 1) % len(my_pieces)
                if got_a_move:
                    move_direction = randint(0, len(piece.moves(board)) - 1)
                    new_coordinate = piece.moves(board)[move_direction]
                    return initial_coordinate, new_coordinate
                else:
                    piece_to_move = (piece_to_move + 1) % len(my_pieces)
        else:
            return None, None


class ScoreBasedStrategy:
    """
    Class that implements the score based decision making robot. We assign points to outcomes to try to find the best
    moves
    """

    @staticmethod
    def choose_move(total_available_moves, board, my_pieces, my_char, enemy_pieces, all_pieces, enemy_char,
                    next_shrink):
        """
        Choose a move that has the greatest score
        :param total_available_moves:
        :param board:
        :param my_pieces:
        :param my_char:
        :param enemy_pieces:
        :param all_pieces:
        :param enemy_char:
        :param next_shrink:
        :return: The action to be made
        """
        all_moves_scores = {}
        if total_available_moves > 0:
            # Iterate through all our possible moves and assign a score for it depending on the outcome
            # Our criteria for the scores are in our comments.txt
            for coord in my_pieces:
                score = 0
                piece = board.get_piece_at(coord)
                for move in piece.moves(board):
                    # score +5 multiplied by how many we kill
                    eliminates = board.will_eliminate(my_char, move[0], move[1])
                    if len(eliminates) > 0:
                        score += 5 * len(eliminates)

                    # Create a hypothetical board state for if we make the move
                    new_piece = Piece.Piece(my_char, move)
                    potential_board_state = copy.deepcopy(board)
                    potential_board_state.add_piece(new_piece)
                    mock_pieces = copy.deepcopy(all_pieces)
                    mock_my_pieces = copy.deepcopy(my_pieces)
                    mock_enemy_pieces = copy.deepcopy(enemy_pieces)
                    mock_my_pieces.pop(coord)
                    mock_my_pieces[move] = new_piece
                    potential_board_state.get_board()[piece.coord[0]][piece.coord[1]] = \
                        Piece.Piece("-", (piece.coord[0], piece.coord[1]))
                    potential_board_state.eliminate_about(move, mock_my_pieces, mock_pieces, my_char, enemy_char,
                                                          mock_enemy_pieces)

                    # If our piece becomes invulnerable as a result of the chosen move
                    if potential_board_state.is_invulnerable(my_char, move[0], move[1]):
                        score += 3

                    # Add scores for the number of all pieces adjacent to that destination square
                    else:
                        score += potential_board_state.friendly_pieces_adjacent(move[0], move[1], my_char)

                    # If our piece will become vulnerable
                    if potential_board_state.will_be_vulnerable_moving(my_char, move[0], move[1], mock_enemy_pieces):
                        score -= 3

                    pieces_vulnerable_to_shrink = []

                    # List of all the pieces on the edge
                    for col, row in my_pieces:
                        if potential_board_state.eliminated_by_shrink(col, row):
                            pieces_vulnerable_to_shrink.append((col, row))

                    # If the board is about to shrink and the piece manges to move away
                    if len(pieces_vulnerable_to_shrink) >= next_shrink - 5 and \
                            board.eliminated_by_shrink(piece.coord[0], piece.coord[1]):
                        if not board.eliminated_by_shrink(move[0], move[1]):
                            score += 2

                    # Add the scores to a dictionary
                    all_moves_scores[(piece.coord, move)] = score
                    # Delete all the temporary data
                    del potential_board_state
                    del mock_pieces
                    del mock_enemy_pieces

            # Return the move that had the highest score
            return max(all_moves_scores, key=all_moves_scores.get)

        else:
            return None
