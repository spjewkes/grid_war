#!/usr/bin/env python3

"""
Manage classes for handling overall game control of Gridwar.
"""

from gridwar.player import Player
from gridwar.utils import GameError

class Game:
    """
    Manages the playing of all the games between the two players.
    """
    __slots__ = ('size', 'num_games', 'layouts', 'plays', 'pieces', 'wins', 'tries', 'verbose')

    def __init__(self, width, height, num_games, pieces, p1_layout, p1_play, p2_layout, p2_play, verbose):
        # Do some validation of playing pieces
        for k, p in pieces.items():
            if p < 1:
                raise GameError("Piece '{}' must be size 1 or greater".format(p))
            if width < p:
                raise GameError("Piece '{}' does not fit board width of {}".format(p, width))
            if height < p:
                raise GameError("Piece '{}' does not fit board height of {}".format(p, height))

        self.size = (width, height)
        self.num_games = num_games
        self.layouts = (p1_layout, p2_layout)
        self.plays = (p1_play, p2_play)
        self.pieces = pieces
        self.wins = [0, 0]
        self.tries = [0, 0]
        self.verbose = verbose

        if self.verbose: print(self)

    def __str__(self):
        return ("Board size ({}x{})\n".format(self.size[0], self.size[1]) +
                "Number of games is {}\n".format(self.num_games) +
                "Game pieces are: {}\n".format(self.pieces))

    def play(self):
        """
        Plays a number of games (as set-up already in the class).
        """
        for game in range(self.num_games):
            if self.verbose: print("Playing game {}:".format(game))
            players = (Player("Player 1", self.size[0], self.size[1], self.pieces, self.layouts[0], self.plays[0], self.verbose),
                       Player("Player 2", self.size[0], self.size[1], self.pieces, self.layouts[1], self.plays[1], self.verbose))

            finished = False
            game_round = 0

            while not finished:
                game_round += 1
                for i in range(2):
                    player = players[i]
                    opponent = players[0] if i == 1 else players[1]

                    attack_pos = player.get_next_attack()
                    player.set_attack_result(attack_pos, *opponent.is_hit(attack_pos))

                    if opponent.is_player_dead() is True:
                        self.wins[i] += 1
                        self.tries[i] += game_round
                        finished = True
                        if self.verbose: print("Player {} won the game on round {}\n".format(i+1, game_round))
                        break

    def display_stats(self):
        """
        Print out the statistics of the games.
        """
        for i, win in enumerate(self.wins):
            print("Player {} wins: {} with (average number of rounds: {:.2f})".format(i+1, win, float(self.tries[i])/win))
