#!/usr/bin/env python
import sys
import argparse
import random

class LayoutBase(object):
    _layouts = []

    @classmethod
    def register(cls, layout_class):
        cls._layouts.append(layout_class)

    @classmethod
    def list_layouts(cls):
        for i, c in enumerate(cls._layouts):
            print("{} - '{}' ({})".format(i+1, c.__name__, c.desc()))

    @classmethod
    def is_valid(cls, layout_name):
        for c in cls._layouts:
            if layout_name == c.__name__:
                return True
        return False

    @classmethod
    def get_class(cls, layout_name):
        if cls.is_valid(layout_name) is not True:
            raise GameError("Layout name '{}' has not been registered".format(layout_name))
        for c in cls._layouts:
            if layout_name == c.__name__:
                return c
        return None

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return self.__class__.__name__

    def place(self, piece):
        """
        Place piece at desired position on a player's board. Returning true if successful,
        otherwise returns false.
        """
        return False

class LayoutRandom(LayoutBase):
    @classmethod
    def desc(cls):
        return "Positions boats randomly whilst avoiding overlap"

    def place(self, piece):
        if random.randint(0, 1) == 0:
            width, height = self.player.board.width, self.player.board.height - piece
            vertical = True
        else:
            width, height = self.player.board.width - piece, self.player.board.height
            vertical = False
        # It would be nice not to have to keep retrying until the piece fits
        # but this seems like a simple compromise for the time being
        for i in range(0, 100):
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if self.player.check_place_piece(piece, vertical, pos) is True:
                self.player.place_piece(piece, vertical, pos)
                return True
        return False

LayoutBase.register(LayoutRandom)
