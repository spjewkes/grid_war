#!/usr/bin/env python
import sys
import argparse

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
    __slots__ = ('width', 'height', 'num_games', 'layouts', 'plays', 'pieces', 'player_layout', 'player_play', 'verbose')

    def __init__(self, width, height, num_games, pieces, p1_layout, p1_play, p2_layout, p2_play, verbose):
        self.width = width
        self.height = height
        self.num_games = num_games
        self.player_layout = (p1_layout, p2_layout)
        self.player_play = (p1_play, p2_play)
        self.pieces = (x for x in pieces)
        self.verbose = verbose

        # Do some validation
        for p in pieces:
            if p < 1:
                raise GameError("Piece '{}' must be size 1 or greater".format(p))
            if self.width < p:
                raise GameError("Piece '{}' does not fit board width of {}".format(p, self.width))
            if self.height < p:
                raise GameError("Piece '{}' does not fit board height of {}".format(p, self.height))

        for layout in self.player_layout:
            if LayoutBase.is_valid(layout) is not True:
                raise GameError("Layout '{}' is not valid".format(layout))

        for play in self.player_play:
            if PlayBase.is_valid(play) is not True:
                raise GameError("Play '{}' is not valid".format(play))

        if self.verbose: print(self)

    def __str__(self):
        return ("Board size ({}x{})\n".format(self.width, self.height) +
            "Number of games is {}\n".format(self.num_games) +
            "Game pieces are: {}\n".format(','.join(map(str, self.pieces))) +
            "Player 1 board layout is '{}' and play strategy is '{}'\n".format(self.player_layout[0], self.player_play[0]) +
            "Player 2 board layout is '{}' and play strategy is '{}'\n".format(self.player_layout[1], self.player_play[1]))

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
        for c in cls._layouts:
            if layout_name == c.name():
                return c
        return None

    @staticmethod
    def name(cls):
        return ""

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

    def place(self, piece):
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
        for c in cls._plays:
            if play_name == c.name():
                return c
        return None

    @staticmethod
    def name():
        return ""

class PlayRandom(PlayBase):
    @staticmethod
    def name():
        return "Random"

PlayBase.register(PlayRandom)

class Board(object):
    """
    Defines the state of a player's board.
    """
    __slots__ = ('width', 'height', 'board', 'round', 'layout', 'play', 'verbose')

    def __init__(self, height, width, pieces, layout, play):
        self.width = width
        self.height = height
        self.board = [0] * height * width
        self.round = 0
        self.layout = layout
        self.play = play
        self.verbose = verbose

        for p in pieces:
            # TODO call selected layout class's place method to set-up board
            None

        if self.verbose: print(self)

    def __str__(self):
        ret_str = ""
        board = map(str, self.board)
        for y in range(0, self.height):
            pos = self.width * y
            ret_str += board[pos:pos+self.width]
            ret_str += "\n"

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
