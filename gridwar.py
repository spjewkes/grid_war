#!/usr/bin/env python
import sys
import argparse

class Game(object):
    """
    Defines the static variables of all games to be played when running the
    Grid War simulation.
    """
    __slots__ = ('width', 'height', 'num_games', 'layouts', 'plays', 'pieces', 'player_layout', 'player_play')

    def __init__(self, width, height, num_games, pieces, p1_layout, p1_play, p2_layout, p2_play):
        self.width = width
        self.height = height
        self.num_games = num_games
        self.player_layout = (p1_layout, p2_layout)
        self.player_play = (p1_play, p2_play)
        self.pieces = (x for x in pieces)

    def __str__(self):
        return ("Board size ({}x{})\n".format(self.width, self.height) +
            "Number of games is {}\n".format(self.num_games) +
            "Game pieces are: {}\n".format(','.join(map(str, self.pieces))) +
            "Player 1 board layout is '{}' and play strategy is '{}'\n".format(self.player_layout[0], self.player_play[0]) +
            "Player 2 board layout is '{}' and play strategy is '{}'\n".format(self.player_layout[1], self.player_play[1]))

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
    args = parser.parse_args()

    game = Game(args.width, args.height, args.num_games, args.pieces, args.p1_layout, args.p1_play, args.p2_layout, args.p2_play)
    print(game)

if __name__ == "__main__":
    main()
