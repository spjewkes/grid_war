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
    Manages the playing of all the games between the two players.
    """
    __slots__ = ('width', 'height', 'num_games', 'layouts', 'plays', 'pieces', 'wins', 'verbose')

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
        self.layouts = (p1_layout, p2_layout)
        self.plays = (p1_play, p2_play)
        self.pieces = tuple(pieces)
        self.wins = [0, 0]
        self.verbose = verbose

        if self.verbose: print(self)

    def __str__(self):
        return ("Board size ({}x{})\n".format(self.width, self.height) +
            "Number of games is {}\n".format(self.num_games) +
            "Game pieces are: {}\n".format(','.join(map(str, self.pieces))))

    def play(self):
        for game in range(self.num_games):
            if self.verbose: print("Playing game {}:".format(game))
            players = (Player("Player 1", self.width, self.height, self.pieces, self.layouts[0], self.plays[0], self.verbose),
                Player("Player 2", self.width, self.height, self.pieces, self.layouts[1], self.plays[1], self.verbose))

            finished = False

            while not finished:
                for i in range(2):
                    player = players[i]
                    opponent = players[0] if i is 1 else players[1]

                    attack = player.get_next_attack()
                    player.set_attack_result(attack, opponent.is_hit(attack))

                    if opponent.is_player_dead() is True:
                        self.wins[i] += 1
                        finished = True
                        if self.verbose: print("Player {} won the game\n".format(i+1))
                        break

    def display_stats(self):
        for i,win in enumerate(self.wins):
            print("Player {} wins: {}".format(i+1, win))

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

    def __init__(self, player):
        self.player = player

    def place(self, piece):
        """
        Place piece at desired position on a player's board. Returning true if successful,
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

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return PlayBase.name()

    def play(self):
        return (-1, -1)

class PlayRandom(PlayBase):
    @staticmethod
    def name():
        return "Random"

    def __str__(self):
        return PlayRandom.name()

    def __init__(self, player):
        super(PlayRandom, self).__init__(player)
        self.plays = [ (x, y) for x in range(player.board.width) for y in range(player.board.height) ]
        random.shuffle(self.plays)

    def play(self):
        return self.plays.pop()

PlayBase.register(PlayRandom)

class PlayScan(PlayBase):
    @staticmethod
    def name():
        return "Scan"

    def __str__(self):
        return PlayScan.name()

    def __init__(self, player):
        super(PlayScan, self).__init__(player)
        self.plays = [ (x,y) for x in range(player.board.width) for y in range(player.board.height) ]

    def play(self):
        return self.plays.pop()

PlayBase.register(PlayScan)

class Hunt(object):
    def __init__(self, init_hit, plays):
        self.init_hit = hit
        self.plays = plays
        self.is_horz = False
        self.is_vert = False

    def play(self):
        None

    def result(self, hit):
        None

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

    def set_attack_result(self, attack, hit):
        if hit:
            self.tracking_board.set(attack, 1)
        else:
            self.tracking_board.set(attack, -1)

    def is_hit(self, attack):
        if self.board.get(attack) is not 0:
            self.board.set(attack, 0)
            self.unsunk -= 1
            return True
        else:
            return False

    def is_player_dead(self):
        return True if self.unsunk is 0 else False

class Board(object):
    """
    Defines an instance of a playing board. Each element is an integer and can be set to
    any value (depending on the context of how it is being used)
    """
    __slots__ = ('width', 'height', 'board')

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [0] * height * width

    def __str__(self):
        ret_str = ""
        board = "".join(map(str, self.board))
        for y in range(0, self.height):
            pos = self.width * y
            ret_str += board[pos:pos+self.width]
            ret_str += "\n"
        return ret_str

    def get(self, pos):
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            raise GameError("Trying to read board at {} when board size is only ({},{})".format(pos, self.width, self.height))
        return self.board[pos[0] + pos[1] * self.width]

    def set(self, pos, value):
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            raise GameError("Trying to write to board at {} when board size is only ({},{})".format(pos, self.width, self.height))
        self.board[pos[0] + pos[1] * self.width] = value

def main():
    parser = argparse.ArgumentParser(description="Iteratively runs Battleship games automatically and display results",
        epilog="Layouts add pieces in the order they are defined at the command line. Player one always starts first.")
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
            game.play()
            game.display_stats()
    except GameError as e:
        print("Simulation failed with the error:\n\t{}".format(e.msg))

if __name__ == "__main__":
    main()
