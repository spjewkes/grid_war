#!/usr/bin/env python
import sys
import argparse
import random

class GameError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class Game(object):
    """
    Defines the static variables of all games to be played when running the
    Grid War simulation and manages the running of all requested iterations of
    play.
    """
    __slots__ = ('width', 'height', 'num_games', 'layouts', 'plays', 'pieces', 'boards', 'verbose')

    def __init__(self, width, height, num_games, pieces, p1_layout, p1_play, p2_layout, p2_play, verbose):
        # Do some validation of playing pieces
        for p in pieces:
            if p < 1:
                raise GameError("Piece '{}' must be size 1 or greater".format(p))
            if width < p:
                raise GameError("Piece '{}' does not fit board width of {}".format(p, width))
            if height < p:
                raise GameError("Piece '{}' does not fit board height of {}".format(p, height))

        self.width = width
        self.height = height
        self.num_games = num_games
        self.pieces = tuple(pieces)
        self.boards = (Board("Player 1", self.width, self.height, self.pieces, p1_layout, p1_play, verbose),
            Board("Player 2", self.width, self.height, self.pieces, p2_layout, p2_play, verbose))
        self.verbose = verbose

        if self.verbose: print(self)

    def __str__(self):
        return ("Board size ({}x{})\n".format(self.width, self.height) +
            "Number of games is {}\n".format(self.num_games) +
            "Game pieces are: {}\n".format(','.join(map(str, self.pieces))))

class LayoutBase(object):
    _layouts = []

    @classmethod
    def register(cls, layout_class):
        cls._layouts.append(layout_class)

    @classmethod
    def list_layouts(cls):
        for i, c in enumerate(cls._layouts):
            print("{} - '{}'".format(i+1, c.name()))

    @classmethod
    def is_valid(cls, layout_name):
        for c in cls._layouts:
            if layout_name == c.name():
                return True
        return False

    @classmethod
    def get_class(cls, layout_name):
        if cls.is_valid(layout_name) is not True:
            raise GameError("Layout name '{}' has not been registered".format(layout_name))
        for c in cls._layouts:
            if layout_name == c.name():
                return c
        return None

    @staticmethod
    def name(cls):
        return "Base"

    def __str__(self):
        return LayoutBase.name()

    def __init__(self, board):
        self.board = board

    def place(self, piece):
        """
        Place piece at desired position on board. Returning true if successful,
        otherwise returns false.
        """
        return False

class LayoutRandom(LayoutBase):
    @staticmethod
    def name():
        return "Random"

    def __str__(self):
        return LayoutRandom.name()

    def place(self, piece):
        if random.randint(0, 1) == 0:
            width, height = self.board.width, self.board.height - piece
            vertical = True
        else:
            width, height = self.board.width - piece, self.board.height
            vertical = False
        for i in range(0, 100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if self.board.check_place_piece(piece, vertical, x, y) is True:
                self.board.place_piece(piece, vertical, x, y)
                return True
        return False

LayoutBase.register(LayoutRandom)

class PlayBase(object):
    _plays = []

    @classmethod
    def register(cls, play_class):
        cls._plays.append(play_class)

    @classmethod
    def list_plays(cls):
        for i, c in enumerate(cls._plays):
            print("{} - '{}'".format(i+1, c.name()))

    @classmethod
    def is_valid(cls, play_name):
        for c in cls._plays:
            if play_name == c.name():
                return True
        return False

    @classmethod
    def get_class(cls, play_name):
        if cls.is_valid(play_name) is not True:
            raise GameError("Play name '{}' has not been registered".format(play_name))
        for c in cls._plays:
            if play_name == c.name():
                return c
        return None

    @staticmethod
    def name():
        return "Base"

    def __str__(self):
        return PlayBase.name()

class PlayRandom(PlayBase):
    @staticmethod
    def name():
        return "Random"

    def __str__(self):
        return PlayRandom.name()

PlayBase.register(PlayRandom)

class Board(object):
    """
    Defines the state of a player's board.
    """
    __slots__ = ('name', 'width', 'height', 'board', 'round', 'pieces', 'layout', 'play', 'verbose')

    def __init__(self, name, height, width, pieces, layout, play, verbose):
        self.name = name
        self.width = width
        self.height = height
        self.board = [0] * height * width
        self.round = 0
        self.pieces = pieces
        self.layout = LayoutBase.get_class(layout)(self)
        self.play = PlayBase.get_class(play)()
        self.verbose = verbose

        for p in pieces:
            if self.layout.place(p) is not True:
                raise GameError("Failed to place piece {} using layout '{}'".format(p, self.layout))

        if self.verbose: print(self)

    def __str__(self):
        ret_str = "Board for {} (using layout '{}' and play '{}'):\n".format(self.name, self.layout, self.play)
        board = "".join(map(str, self.board))
        for y in range(0, self.height):
            pos = self.width * y
            ret_str += board[pos:pos+self.width]
            ret_str += "\n"
        return ret_str

    def get(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise GameError("Trying to read board at ({},{}) when board size is only ({},{})".format(x, y, self.width, self.height))
        return self.board[x + y * self.width]

    def set(self, x, y, piece):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise GameError("Trying to write to board at ({},{}) when board size is only ({},{})".format(x, y, self.width, self.height))
        if piece not in self.pieces:
            raise GameError("Piece '{p}' does not exist when trying to set board with it".format(p))
        self.board[x + y * self.width] = piece

    def check_place_piece(self, piece, vertical, x, y):
        if vertical is True:
            for pos_y in range(0, y):
                if x < 0 or pos_y < 0 or x >= self.width or pos_y >= self.height:
                    return False
                if self.get(x, pos_y) is not 0:
                    return False
        else:
            for pos_x in range(0, x):
                if pos_x < 0 or y < 0 or pos_x >= self.width or y >= self.height:
                    return False
                if self.get(pos_x, y) is not 0:
                    return False

        return True

    def place_piece(self, piece, vertical, x, y):
        if self.check_place_piece(piece, vertical, x, y) is False:
            raise GameError("Cannot place piece '{}' at ({},{}) {}".format(piece, x, y, ("vertically" if vertical is True else "horizontally")))
        if vertical is True:
            for pos_y in range(0, y):
                self.set(x, pos_y, piece)
        else:
            for pos_x in range(0, x):
                self.set(pos_x, y, piece)

def main():
    parser = argparse.ArgumentParser(description="Iteratively runs Battleship games automatically and display results")
    parser.add_argument('--width', help="Width of game board", dest='width', type=int, default=10)
    parser.add_argument('--height', help="Height of game board", dest='height', type=int, default=10)
    parser.add_argument('--games', help="Number of games to play", dest='num_games', type=int, default=100)
    parser.add_argument('--list-layouts', help="List the available board layouts", action='store_true')
    parser.add_argument('--list-plays', help="List the available play strategies", action='store_true')
    parser.add_argument('--pieces', help="List of pieces by size they each take up on the board", dest='pieces', type=int, nargs='*', default=[5,4,3,3,2])
    parser.add_argument('--p1-layout', help="The name of the board layout to be used by player 1", dest='p1_layout', type=str, default="Random")
    parser.add_argument('--p1-play', help="The play strategy to be used by player 1", dest='p1_play', type=str, default="Random")
    parser.add_argument('--p2-layout', help="The name of the board layout to be used by player 2", dest='p2_layout', type=str, default="Random")
    parser.add_argument('--p2-play', help="The play strategy to be used by player 2", dest='p2_play', type=str, default="Random")
    parser.add_argument('--verbose', help="Enable verbose output whilst running simulation", action='store_true')
    args = parser.parse_args()

    try:
        if args.list_layouts:
            LayoutBase.list_layouts()
        elif args.list_plays:
            PlayBase.list_plays()
        else:
            game = Game(args.width, args.height, args.num_games, args.pieces, args.p1_layout, args.p1_play, args.p2_layout, args.p2_play, args.verbose)
    except GameError as e:
        print("Simulation failed with the error:\n\t{}".format(e.msg))

if __name__ == "__main__":
    main()
