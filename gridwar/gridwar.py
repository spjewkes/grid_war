from board import Board
from player import Player
from utils import GameError

class Game(object):
    """
    Manages the playing of all the games between the two players.
    """
    __slots__ = ('width', 'height', 'num_games', 'layouts', 'plays', 'pieces', 'wins', 'verbose')

    def __init__(self, width, height, num_games, pieces, p1_layout, p1_play, p2_layout, p2_play, verbose):
        # Do some validation of playing pieces
        for k,p in pieces.items():
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
        self.pieces = pieces
        self.wins = [0, 0]
        self.verbose = verbose

        if self.verbose: print(self)

    def __str__(self):
        return ("Board size ({}x{})\n".format(self.width, self.height) +
            "Number of games is {}\n".format(self.num_games) +
            "Game pieces are: {}\n".format(self.pieces))

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

                    attack_pos = player.get_next_attack()
                    player.set_attack_result(attack_pos, opponent.is_hit(attack_pos))

                    if opponent.is_player_dead() is True:
                        self.wins[i] += 1
                        finished = True
                        if self.verbose: print("Player {} won the game\n".format(i+1))
                        break

    def display_stats(self):
        for i,win in enumerate(self.wins):
            print("Player {} wins: {}".format(i+1, win))
