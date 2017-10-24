from layouts import LayoutBase
from plays import PlayBase
from board import Board
from utils import GameError

class Player(object):
    """
    Defines the state of a player's board.
    """
    __slots__ = ('name', 'board', 'tracking_board', 'round', 'pieces', 'layout', 'play', 'unsunk', 'verbose')

    def __init__(self, name, width, height, pieces, layout, play, verbose):
        self.name = name
        self.board = Board(width, height)
        self.tracking_board = Board(width, height)
        self.round = 0
        self.pieces = pieces
        self.layout = LayoutBase.get_class(layout)(self)
        self.play = PlayBase.get_class(play)(self)
        self.unsunk = sum(self.pieces)
        self.verbose = verbose

        for p in pieces:
            if self.layout.place(p) is not True:
                raise GameError("Failed to place piece {} using layout '{}'".format(p, self.layout))

        if self.verbose: print(self)

    def __str__(self):
        return "Board for {} (using layout '{}' and play '{}'):\n{}".format(self.name, self.layout, self.play, self.board)

    def check_place_piece(self, piece, vertical, pos):
        if vertical is True:
            for pos_y in range(pos[1], pos[1]+piece):
                if pos[0] < 0 or pos_y < 0 or pos[0] >= self.board.width or pos_y >= self.board.height:
                    return False
                if self.board.get((pos[0], pos_y)) is not 0:
                    return False
        else:
            for pos_x in range(pos[0], pos[0]+piece):
                if pos_x < 0 or pos[1] < 0 or pos_x >= self.board.width or pos[1] >= self.board.height:
                    return False
                if self.board.get((pos_x, pos[1])) is not 0:
                    return False

        return True

    def place_piece(self, piece, vertical, pos):
        if self.check_place_piece(piece, vertical, pos) is False:
            raise GameError("Cannot place piece '{}' at {} {}".format(piece, pos, ("vertically" if vertical is True else "horizontally")))
        if piece not in self.pieces:
            raise GameError("Piece '{p}' does not exist when trying to set board with it".format(p))
        if vertical is True:
            for pos_y in range(pos[1], pos[1]+piece):
                self.board.set((pos[0], pos_y), piece)
        else:
            for pos_x in range(pos[0], pos[0]+piece):
                self.board.set((pos_x, pos[1]), piece)

    def get_next_attack(self):
        return self.play.play()

    def set_attack_result(self, attack_pos, hit):
        self.play.result(attack_pos, hit)
        if hit:
            self.tracking_board.set(attack_pos, 1)
        else:
            self.tracking_board.set(attack_pos, -1)

    def is_hit(self, attack_pos):
        if self.board.get(attack_pos) is not 0:
            self.board.set(attack_pos, 0)
            self.unsunk -= 1
            return True
        else:
            return False

    def is_player_dead(self):
        return True if self.unsunk is 0 else False
