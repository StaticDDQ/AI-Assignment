"""
Player class for project B: Artificial Intelligence
:authors: Axel Bachtiar and Robby Ilman
"""

from Strategy import TurtleStrategy, RandomStrategy, ScoreBasedStrategy
import Piece
import Board


class Player:

    def __init__(self, colour):
        self.pieces = {'O': 0, '@': 0}
        self.moving_phase = False
        self.board = Board.Board()
        self.my_pieces = {}
        self.enemy_pieces = {}
        self.enemy_moving_phase = False
        self.shrinks = 0
        self.already_shrunk = False
        self.already_shrunk_twice = False

        if colour == "white":
            self.max_placing_turns = 22
            self.max_moving_turns_1 = 128
            self.max_moving_turns_2 = 192
            self.my_char = "O"
            self.enemy_char = "@"
            self.max_row = 5
            self.min_row = 0
        else:
            self.max_placing_turns = 23
            self.max_moving_turns_1 = 127
            self.max_moving_turns_2 = 191
            self.my_char = "@"
            self.enemy_char = "O"
            self.max_row = 7
            self.min_row = 2

    def action(self, turns):
        """
        Choose a move to be made based on our strategy. Our output format depends on the state of the game, whether
        it is in the placing stage or in the moving stage
        :param turns:
        :return: The action to be made
        """

        # Check if we should shrink the board and do so if we should. The timing of the shrink for white is at the start
        # of action
        if self.my_char == 'O':
            if turns >= self.max_moving_turns_1 and not self.already_shrunk:
                self.board.shrink_board(self.my_pieces, self.pieces, self.my_char, self.enemy_char, self.enemy_pieces)

                self.already_shrunk = True
            if turns >= self.max_moving_turns_2 and not self.already_shrunk_twice:
                self.board.shrink_board(self.my_pieces, self.pieces, self.my_char, self.enemy_char, self.enemy_pieces)
                self.already_shrunk_twice = True

        # Count the number of turns until the next shrink
        if not self.already_shrunk:
            next_shrink = self.max_moving_turns_1 - turns
        elif not self.already_shrunk_twice:
            next_shrink = self.max_moving_turns_2 - turns
        # After the 2nd shrink we can just assign a huge number for this (since there won't be any more shrinks)
        else:
            next_shrink = 999

        # Placing phase
        if not self.moving_phase:

            # Turtle strategy for placing
            new_coordinate = TurtleStrategy.choose_placing(self.board, self.my_pieces, self.enemy_pieces, self.min_row,
                                                           self.max_row, self.my_char)

            # Update our internal board with our action
            new_piece = Piece.Piece(self.my_char, new_coordinate)
            self.board.add_piece(new_piece)
            self.pieces[self.my_char] += 1
            self.my_pieces[new_coordinate] = new_piece
            self.board.eliminate_about(new_coordinate, self.my_pieces, self.pieces, self.my_char, self.enemy_char,
                                       self.enemy_pieces)

            # Checking if it is the end of the placing stage
            if turns >= self.max_placing_turns:
                self.moving_phase = True

            return new_coordinate

        # Moving phase
        if self.moving_phase:

            # Turtle strategy for moving
            initial_coordinate, new_coordinate = TurtleStrategy.choose_move(self.total_available_moves(), self.board,
                                                                            self.my_pieces, self.my_char,
                                                                            self.enemy_pieces, self.min_row,
                                                                            self.max_row, next_shrink)
            # Update our internal board with our chosen action
            piece = self.my_pieces[initial_coordinate]
            self.my_pieces.pop(initial_coordinate)
            self.my_pieces[new_coordinate] = piece
            self.make_move(piece, new_coordinate)

            # The timing of the shrink for black happens after he has done his action
            if self.my_char == '@':
                if turns >= self.max_moving_turns_1 and not self.already_shrunk:
                    self.board.shrink_board(self.my_pieces, self.pieces, self.my_char, self.enemy_char,
                                            self.enemy_pieces)
                    self.already_shrunk = True
                if turns >= self.max_moving_turns_2 and not self.already_shrunk_twice:
                    self.board.shrink_board(self.my_pieces, self.pieces, self.my_char, self.enemy_char,
                                            self.enemy_pieces)
                    self.already_shrunk_twice = True

            if new_coordinate is None:
                return None
            else:
                return initial_coordinate, new_coordinate

    def update(self, action):
        """
        Update our internal board with our opponent's move
        :param action:
        """

        if self.my_char == "@":
            if self.moving_phase:
                self.enemy_moving_phase = True

        # placing phase
        if not self.enemy_moving_phase:
            new_piece = Piece.Piece(self.enemy_char, action)
            self.enemy_pieces[action] = new_piece
            self.board.add_piece(new_piece)
            self.pieces[self.enemy_char] += 1
            self.board.eliminate_about(action, self.my_pieces, self.pieces, self.my_char, self.enemy_char,
                                       self.enemy_pieces)

        # moving phase
        else:
            initial_coordinate, new_coordinate = action
            piece = self.enemy_pieces[initial_coordinate]
            self.enemy_pieces.pop(initial_coordinate)
            self.enemy_pieces[new_coordinate] = piece
            self.make_move(self.board.get_piece_at(initial_coordinate), new_coordinate)

        if self.my_char == "O":
            if self.moving_phase:
                self.enemy_moving_phase = True

    def make_move(self, piece, new_coord):
        """
        Update our internal board with a moving action (both the opponent's or our chosen action).
        :param piece:
        :param new_coord:
        """
        initial_coord = piece.coord
        piece.coord = new_coord
        self.board.add_piece(piece)
        self.board.add_piece(Piece.Piece("-", initial_coord))
        self.board.eliminate_about(new_coord, self.my_pieces, self.pieces, self.my_char, self.enemy_char,
                                   self.enemy_pieces)

    def total_available_moves(self):
        """
        Count the total number of available moves across all our remaining pieces
        :return: Number of moves
        """
        total = 0
        for col, row in self.my_pieces:
            total += len(self.board.get_piece_at((col, row)).moves(self.board))
        return total

    # for our own use to easily interpret the board state
    def __str__(self):
        output_board = [['' for _ in range(8)] for _ in range(8)]
        for col in range(8):
            for row in range(8):

                output_board[row][col] = self.board.get_board()[col][row].get_type()
        board = '\n'.join(' '.join(row) for row in output_board)
        return board
