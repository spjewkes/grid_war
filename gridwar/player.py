#!/usr/bin/env python3

"""
Manages code for a player.
"""

import copy
from gridwar.layouts import LayoutBase
from gridwar.plays import PlayBase
from gridwar.board import Board
from gridwar.utils import GameError

class Player:
    """
    Defines the state of a player's board.
    """
    __slots__ = ('name', 'board', 'tracking_board', 'pieces', 'opponent_pieces', 'layout', 'play', 'verbose')

    def __init__(self, name, width, height, pieces, layout, play, verbose):
        self.name = name
        self.board = Board(width, height)
        self.tracking_board = Board(width, height)
        self.pieces = copy.deepcopy(pieces)
        self.opponent_pieces = copy.deepcopy(pieces)
        self.layout = LayoutBase.get_class(layout)(self)
        self.play = PlayBase.get_class(play)(self)
        self.verbose = verbose

        for k, p in pieces.items():
            if self.layout.place(k, p) is not True:
                raise GameError("Failed to place piece ('{}': {}) using layout '{}' on board:\n{}".
                                format(k, p, self.layout, self.board))

        if self.verbose: print(self)

    def __str__(self):
        return "Board for {} (using layout '{}' and play '{}'):\n{}".format(self.name, self.layout, self.play, self.board)

    def check_place_piece(self, size, vertical, pos):
        """
        Check the play of a piece.
        """
        if vertical is True:
            for pos_y in range(pos[1], pos[1]+size):
                if pos[0] < 0 or pos_y < 0 or pos[0] >= self.board.width or pos_y >= self.board.height:
                    return False
                if self.board.get((pos[0], pos_y)) != Board.EMPTY:
                    return False
        else:
            for pos_x in range(pos[0], pos[0]+size):
                if pos_x < 0 or pos[1] < 0 or pos_x >= self.board.width or pos[1] >= self.board.height:
                    return False
                if self.board.get((pos_x, pos[1])) != Board.EMPTY:
                    return False

        return True

    def place_piece(self, key, size, vertical, pos):
        """
        Place a piece at a specific location.
        """
        if self.check_place_piece(size, vertical, pos) is False:
            raise GameError("Cannot place piece ('{}': {}) at {} {}".
                            format(key, size, pos, ("vertically" if vertical is True else "horizontally")))
        if key not in self.pieces:
            raise GameError("Piece '{}' does not exist when trying to set board with it".format(key))
        if vertical is True:
            for pos_y in range(pos[1], pos[1]+size):
                self.board.set((pos[0], pos_y), key)
        else:
            for pos_x in range(pos[0], pos[0]+size):
                self.board.set((pos_x, pos[1]), key)

    def get_next_attack(self):
        """
        Get player's next move.
        """
        return self.play.play()

    def set_attack_result(self, attack_pos, hit, sunk):
        """
        Note result of player's move.
        """
        self.play.result(attack_pos, hit, sunk)
        if hit:
            self.tracking_board.set(attack_pos, Board.HIT)
        else:
            self.tracking_board.set(attack_pos, Board.MISS)
        if sunk is not None:
            del self.opponent_pieces[sunk]

    def is_hit(self, attack_pos):
        """
        Return whether a move hits or not.
        """
        hit = self.board.get(attack_pos)
        if hit not in (Board.EMPTY, Board.HIT):
            self.board.set(attack_pos, Board.HIT)
            self.pieces[hit] -= 1
            if self.pieces[hit] == 0:
                return True, hit
            return True, None
        elif hit != Board.EMPTY:
            raise GameError("Player tried to hit the same location twice at {} of board {}".format(hit, self.board))
        return False, None

    def is_player_dead(self):
        """
        Informs if a player has lost all their pieces.
        """
        total = sum(list(self.pieces.values()))
        return bool(total == 0)
