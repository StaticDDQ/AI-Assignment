"""
Piece class for project B: Artificial Intelligence
@authors: Axel Bachtiar and Robby Ilman
"""
DIRECTIONS = UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)


class Piece:

    def __init__(self, type, coord):
        self.type = type
        self.coord = coord

    def get_type(self):
        return self.type

    def get_coord(self):
        return self.coord

    def moves(self, board):
        """
        Compute and return a list of the available moves for this piece based
        on the current board state.

        Do not call with method on pieces with `alive = False`.
        """

        possible_moves = []
        for direction in DIRECTIONS:
            # a normal move to an adjacent square?
            adjacent_square = self.step(self.coord, direction)
            if board.within_board(adjacent_square[0], adjacent_square[1]):
                if board.get_board()[adjacent_square[0]][adjacent_square[1]].get_type() == "-":
                    possible_moves.append(adjacent_square)
                    continue # a jump move is not possible in this direction

            # if not, how about a jump move to the opposite square?
            opposite_square = self.step(adjacent_square, direction)
            if board.within_board(opposite_square[0], opposite_square[1]):
                if board.get_board()[opposite_square[0]][opposite_square[1]].get_type() == "-":
                    possible_moves.append(opposite_square)
        return possible_moves

    def step(self, position, direction):
        """
        Take an (x, y) tuple `position` and a `direction` (UP, DOWN, LEFT or RIGHT)
        and combine to produce a new tuple representing a position one 'step' in
        that direction from the original position.
        """
        px, py = position
        dx, dy = direction
        return (px + dx, py + dy)