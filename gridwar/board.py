#!/usr/bin/env python3

"""
Defines the board used to run each simulation of Gridwar.
"""

from gridwar.utils import GameError

class Board:
    """
    Defines an instance of a playing board. Each element is an integer and can be set to
    any value (depending on the context of how it is being used)
    """
    __slots__ = ('width', 'height', 'board')

    EMPTY = ' '
    MISS = '_'
    HIT = '!'

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [Board.EMPTY] * height * width

    def __str__(self):
        ret_str = ""
        for y in range(0, self.height):
            pos = self.width * y
            ret_str += ''.join(map(str, self.board[pos:pos+self.width]))
            ret_str += "\n"
        return ret_str.replace(" ", ".")

    def get(self, pos):
        """
        Get the status of the board at the defined (x,y) coordinate.
        """
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            raise GameError("Trying to read board at {} when board size is only ({},{})".
                            format(pos, self.width, self.height))
        return self.board[pos[0] + pos[1] * self.width]

    def set(self, pos, value):
        """
        Set the board status at position (x,y) coordinate.
        """
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            raise GameError("Trying to write to board at {} when board size is only ({},{})".
                            format(pos, self.width, self.height))
        self.board[pos[0] + pos[1] * self.width] = value
