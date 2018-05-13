"""
Board class for project B: Artificial Intelligence
@authors: Axel Bachtiar and Robby Ilman
"""
import Piece


class Board:

    def __init__(self):
        self.board = [[Piece.Piece("-", (col, row)) for row in range(8)] for col in range(8)]
        for square in [(0, 0), (7, 0), (7, 7), (0, 7)]:
            col, row = square
            self.board[col][row] = Piece.Piece("X", square)
        self.n_shrinks = 0

    def add_shrink(self):
        """
        Add the number of shrinks that has occurred
        """
        self.n_shrinks += 1

    def get_n_shrinks(self):
        return self.n_shrinks

    def within_board(self, col, row):
        """
        Check if a given pair of coordinates is 'on the board'.
        :param col: column value
        :param row: row value
        :return: True if the coordinate is on the board
        """
        for coord in [col, row]:
            if coord < self.n_shrinks or coord > 7 - self.n_shrinks:
                return False
        if self.get_board()[col][row].get_type() == ' ':
            return False
        return True

    def add_piece(self, piece):
        self.board[piece.get_coord()[0]][piece.get_coord()[1]] = piece

    def get_board(self):
        return self.board

    def get_piece_at(self, coord):
        return self.board[coord[0]][coord[1]]

    def shrink_board(self, my_pieces, pieces, my_char, enemy_char, enemy_pieces):
        """
        Shrink the board, eliminating all pieces along the outermost layer,
        and replacing the corners.
        This method can be called up to two times only.
        Taken from the referee.py module with minor modifications.
        """
        s = self.n_shrinks # number of shrinks so far, or 's' for short
        # Remove edges
        for i in range(s, 8 - s):
            for square in [(i, s), (s, i), (i, 7 - s), (7 - s, i)]:
                y, x = square
                piece = self.board[y][x]
                if piece.get_type() in pieces:
                    pieces[piece.get_type()] -= 1
                    if piece.get_type() == my_char:
                        my_pieces.pop(piece.coord)
                self.board[y][x] = Piece.Piece(" ", (y, x))

        # we have now shrunk the board once more!
        self.add_shrink()
        s = self.n_shrinks

        # replace the corners (and perform corner elimination)
        for corner in [(s, s), (s, 7 - s), (7 - s, 7 - s), (7 - s, s)]:
            y, x = corner
            piece = self.board[y][x]
            if piece.get_type() in pieces:
                pieces[piece.get_type()] -= 1
                if piece.get_type() == my_char:
                    my_pieces.pop(piece.coord)
            self.board[y][x] = Piece.Piece('X', (y, x))
            self.eliminate_about(corner, my_pieces, pieces, my_char, enemy_char, enemy_pieces)

    def eliminate_about(self, square, my_pieces, pieces, my_char, enemy_char, enemy_pieces):
        """
        A piece has entered this square: look around to eliminate adjacent
        (surrounded) enemy pieces, then possibly eliminate this piece too.
        Taken from the referee.py module with minor modifications

        :param square: the square to look around
        :param my_pieces: The dict of our remaining pieces
        :param pieces: The dict of the number of remaining pieces from both sides
        :param my_char: My character representation (either 'O' or '@')
        :param enemy_char: Enemy's character representation
        :param enemy_pieces: Dict of the remaining opposing pieces
        """
        col, row = square
        piece_type = self.get_board()[col][row].get_type()
        targets = self.targets(piece_type)

        # Check if piece in square eliminates other pieces
        for dcol, drow in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_col, target_row = col + dcol, row + drow
            targetval = None
            if self.within_board(target_col, target_row):
                targetval = self.get_board()[target_col][target_row].get_type()
            if targetval in targets:
                if self._surrounded(target_col, target_row, -dcol, -drow):
                    # If it is our piece, we remove from the dict of our pieces
                    if (target_col, target_row) in my_pieces.keys():
                        my_pieces.pop((target_col, target_row))
                    # If it is the opponent's piece, we remove from the dict of enemy pieces
                    elif piece_type == enemy_char:
                        enemy_pieces.pop((target_col, target_row))
                    self.get_board()[target_col][target_row] = Piece.Piece("-", (col, row))
                    pieces[targetval] -= 1

        # Check if the current piece is surrounded and should be eliminated
        if piece_type in pieces:
            if self._surrounded(col, row, 1, 0) or self._surrounded(col, row, 0, 1):
                # If it is our piece, we remove from the dict of our pieces
                if piece_type == my_char:
                    my_pieces.pop((col, row))
                # If it is the opponent's piece, we remove from the dict of enemy pieces
                elif piece_type == enemy_char:
                    enemy_pieces.pop((col, row))
                self.get_board()[col][row] = Piece.Piece("-", (col, row))
                pieces[piece_type] -= 1

    def _surrounded(self, col, row, dcol, drow):
        """
        Check if piece on (col, row) is surrounded on (col + dcol, row + drow) and
        (col - dcol, row - drow).
        Taken from the referee.py module.

        :param col: column of the square to be checked
        :param row: row of the square to be checked
        :param dcol: 1 if adjacent cols are to be checked (drow should be 0)
        :param drow: 1 if adjacent rows are to be checked (dcol should be 0)
        :return: True if the square is surrounded
        """
        cola, rowa = col + dcol, row + drow
        firstval = None
        if self.within_board(cola, rowa):
            firstval = self.get_board()[cola][rowa].get_type()

        colb, rowb = col - dcol, row - drow
        secondval = None
        if self.within_board(colb, rowb):
            secondval = self.get_board()[colb][rowb].get_type()

        # If both adjacent squares have enemies then this piece is surrounded!
        enemies = self._enemies(self.get_board()[col][row].get_type())
        return firstval in enemies and secondval in enemies

    @staticmethod
    def _enemies(piece_type):
        """
        Which pieces can eliminate a piece of this type?
        Taken from the referee.py module

        :param piece_type: the type of piece ('@', 'O', or 'X')
        :return: set of piece types that can eliminate a piece of this type
        """
        if piece_type == '@':
            return {'O', 'X'}
        elif piece_type == 'O':
            return {'@', 'X'}
        return set()

    def is_enemy(self, piece_type, coord):
        """
        Boolean for if the given coordinate is occupied by an opposing piece
        :param piece_type:
        :param coord:
        :return: True if the coordinate is occupied by an opposing piece
        """
        enemies = self._enemies(piece_type)
        return self.get_piece_at(coord).get_type() in enemies

    def targets(self, piece):
        """
        Which pieces can a piece of this type eliminate?

        :param piece: the type of piece ('@', 'O', or 'X')
        :return: the set of piece types that a piece of this type can eliminate
        """
        if piece == '@':
            return {'O'}
        elif piece == 'O':
            return {'@'}
        elif piece == 'X':
            return {'@', 'O'}
        return set()

    def next_to_opponent(self, col, row, dcol, drow):
        """
        Check to see if the piece is next to an opposing piece (but not surrounded).
        Overall method of doing this is taken from referee.py module
        :param col: column
        :param row: row
        :param dcol: To get an adjacent square
        :param drow: To get an adjacent square
        :return: True if the piece is next to an opponent
        """
        cola, rowa = col + dcol, row + drow
        firstval = None
        if self.within_board(cola, rowa):
            firstval = self.get_board()[cola][rowa].get_type()

        colb, rowb = col - dcol, row - drow
        secondval = None
        if self.within_board(colb, rowb):
            secondval = self.get_board()[colb][rowb].get_type()

        # If both adjacent squares have enemies then this piece is surrounded!
        enemies = self._enemies(self.get_board()[col][row].get_type())
        return firstval in enemies or secondval in enemies

    def target_square_to_kill_or_protect(self, col, row, min_row, max_row):
        """
        This is used in the placing phase. We have identified a target square that could either kill an enemy or save
        our ally. Now we can place a piece there to save our ally.
        :param col: column
        :param row: row
        :param min_row: minimum row depending on which side we are on
        :param max_row: maximum row depending on which side we are on
        :return: coordinates
        """
        piece_type = self.get_board()[col][row].get_type()
        enemies = self._enemies(piece_type)

        for dcol, drow in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_col, target_row = col + dcol, row + drow
            target_val = None
            if self.within_board(target_col, target_row):
                target_val = self.get_board()[target_col][target_row].get_type()
            if target_val in enemies:
                if self.within_board(col + (-1 * dcol), row + (-1 * drow)) and min_row <= row + (-1 * drow) <= max_row \
                        and self.get_board()[col + (-1 * dcol)][row + (-1 * drow)].get_type() == "-":

                    return col + (-1 * dcol), row + (-1 * drow)
        return None, None

    def can_move_for_kill_protect(self, target_coord, pieces):
        """
        To be used during the moving phase. We have identified a target square that would either kill an opposing piece
        or save our ally.
        :param target_coord: Target square to be occupied
        :param pieces: Our dict of remaining pieces
        :return: Our piece that should move to the target square or None if ther aren't any
        """
        for piece in pieces.values():
            # Iterate through all the possibe moves until we find or we get to the end and return none
            for coords in piece.moves(self):
                if coords == target_coord:
                    return piece.coord
        return None

    def non_vulnerable_adjacent(self, piece_type, col, row):
        """
        Finds any free space adjacent to the given coordinates which are not being attacked/targetted by the opponent
        pieces
        :param piece_type: Our character team representation
        :param col: column
        :param row: row
        :return: The list of free spaces adjacent to our allies that are safe
        """
        empty_safe_squares = []

        for dcol, drow in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            # Check if the adjacent squares are occupied by an enemy, if yes, check if the opposite side of the occupied
            # square is also occupied or not
            if self.within_board(col + dcol, row + drow):
                if self.get_piece_at((col + dcol, row + drow)).get_type() == "-" and not \
                        self.will_be_vulnerable_placing(piece_type, col + dcol, row + drow):
                    empty_safe_squares.append((col + dcol, row + drow))
        return empty_safe_squares

    def will_be_vulnerable_placing(self, piece_type, col, row):
        """
        Check if placing a piece in the coordinates will endanger our piece (could be killed instantly or in the
        upcoming turn)
        :param piece_type:
        :param col:
        :param row:
        :return:True if the square is vulnerable
        """
        enemies = self._enemies(piece_type)

        # Check all adjacent squares
        for dcol, drow in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            # Check if the adjacent squares are occupied by an enemy, if yes, check if the opposite side of the occupied
            # square is also occupied or not
            if self.within_board(col + dcol, row + drow):
                if self.get_piece_at((col + dcol, row + drow)).get_type() in enemies:
                    if self.within_board(col + (-1 * dcol), row + (-1 * drow)):
                        return self.get_piece_at((col + (-1 * dcol), row + (-1 * drow))).get_type() == "-" or \
                               self.get_piece_at((col + (-1 * dcol), row + (-1 * drow))).get_type() in enemies
        return False

    def will_be_vulnerable_moving(self, piece_type, col, row, enemy_pieces):
        """
        Check if moving a piece in the coordinates will endanger our piece (could be killed instantly or in the
        upcoming turn)
        :param piece_type:
        :param col:
        :param row:
        :param enemy_pieces:
        :return: True if our piece could be killed either instantly or in the upcoming turn
        """
        enemies = self._enemies(piece_type)

        for dcol, drow in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            # Check if the adjacent squares are occupied by an enemy
            if self.within_board(col + dcol, row + drow):
                # If it is, check if the opposite side of the occupied square is either an enemy or a square that is
                # accessible to an enemy in the next turn
                if self.get_piece_at((col + dcol, row + drow)).get_type() in enemies:
                    if self.within_board(col + (-1 * dcol), row + (-1 * drow)):
                        if self.get_piece_at((col + dcol, row + drow)).get_type() == "-":
                            # Checking if any of the enemy's possible moves next turn is this square
                            for enemy_piece in enemy_pieces:
                                for potential_coord in enemy_piece.moves(self):
                                    if potential_coord == (col + dcol, row + drow):
                                        return True
                            return False
                        elif self.get_piece_at((col + dcol, row + drow)).get_type() in enemies:
                            return True
        return False

    def eliminated_by_shrink(self, col, row):
        """
        Check if the piece in the coordinate  is going to be killed when the board shrinks
        :param col: column value
        :param row: row value
        :return: True if our piece is in the coordinate
        """
        # If the coord is on the edges
        for coord in [col, row]:
            if coord < self.n_shrinks + 1 or coord > 7 - self.n_shrinks + 1:
                return True
        # If the coord is where the new corner will be
        if (col, row) in [(self.n_shrinks, self.n_shrinks), (7 - self.n_shrinks, 7 - self.n_shrinks),
                          (self.n_shrinks, 7 - self.n_shrinks), (7 - self.n_shrinks, self.n_shrinks)]:
            return True
        if self.get_board()[col][row].get_type() == ' ':
            return True
        return False

    def will_eliminate(self, piece_type, col, row):
        """
        Check(without modifying our internal board) the exact pieces that die as a result of the action
        :param piece_type:
        :param col:
        :param row:
        :return:the list of eliminated opponent (can return an empty list
        """
        eliminates = []
        targets = self.targets(piece_type)
        # Check if piece in square eliminates other pieces
        for dcol, drow in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_col, target_row = col + dcol, row + drow
            targetval = None
            if self.within_board(target_col, target_row):
                targetval = self.get_board()[target_col][target_row].get_type()
            # Check if the square next to our potential destination is an enemy
            if targetval in targets:
                # If it is an enemy, check the square immediately after the enemy piece, if it is our piece, we will
                # eliminate the enemy piece
                if self.within_board(target_col + dcol, target_row + drow):
                    if self.get_board()[target_col + dcol][target_row + drow].get_type() == piece_type:
                        eliminates.append((target_col, target_row))
        return eliminates

    def is_invulnerable(self, piece_type, col, row):
        """
        Check if the piece is invulnerable (i.e. it is unkillable by the opponent pieces). This is true if both
        methods in which the piece would get surrounded from are occupied by non-enemy pieces
        :param piece_type:
        :param col:
        :param row:
        :return:  True if the piece is unkillable
        """
        for dcol, drow in [(1, 0), (0, 1)]:
            target_col, target_row = col + dcol, row + drow
            if not self.within_board(target_col, target_row):
                if not self.within_board(col + (-1 * dcol), row + (-1 * drow)):
                    return True
                elif self.get_board()[col + (-1 * dcol)][row + (-1 * drow)] == piece_type:
                    return True
            if self.get_board()[col][row] == piece_type:
                if not self.within_board(col + (-1 * dcol, row) + (-1 * drow)):
                    return True
                elif self.get_board()[col + (-1 * dcol)][row + (-1 * drow)] == piece_type:
                    return True
        return False

    def friendly_pieces_adjacent(self, col, row, piece_type):
        """
        Find the list of possible coordinates that are next to the friendly unit and will not result in death
        :param col:
        :param row:
        :param piece_type:
        :return: List of the safe, close squares
        """
        output = 0
        # Check if piece in square eliminates other pieces
        for dcol, drow in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_col, target_row = col + dcol, row + drow
            if self.within_board(target_col, target_row):
                if self.get_piece_at((target_col, target_row)) == piece_type:
                    output += 1
        return output
