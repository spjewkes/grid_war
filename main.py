#!/usr/bin/env python3

"""
This program runs simulations of the popular Battleships board game. Allowing for each player
to select specific board layouts and styles of play as means of seeing which one is likely
to have a higher chance of success.
"""

import argparse
from gridwar.gridwar import Game
from gridwar.utils import GameError
from gridwar.layouts import LayoutBase
from gridwar.plays import PlayBase

def main():
    """ Main application entry-point for grid war simulation. """
    parser = argparse.ArgumentParser(
        description="Iteratively runs Battleship games automatically and display results",
        epilog="Layouts add pieces in the order they are defined at the command line. "
        "Player one always starts first.")
    parser.add_argument('--width', help="Width of game board", dest='width',
                        type=int, default=10)
    parser.add_argument('--height', help="Height of game board", dest='height',
                        type=int, default=10)
    parser.add_argument('--games', help="Number of games to play", dest='num_games',
                        type=int, default=100)
    parser.add_argument('--list-layouts', help="List the available board layouts",
                        action='store_true')
    parser.add_argument('--list-plays', help="List the available play strategies",
                        action='store_true')
    parser.add_argument('--pieces', help="List of pieces by size they each take up on the board "
                        "(e.g. 5,4,3,3,2)", dest='pieces', type=str, default="5,4,3,3,2")
    parser.add_argument('--p1-layout', help="The name of the board layout to be used by player 1",
                        dest='p1_layout', type=str, default="LayoutRandom")
    parser.add_argument('--p1-play', help="The play strategy to be used by player 1",
                        dest='p1_play', type=str, default="PlayRandom")
    parser.add_argument('--p2-layout', help="The name of the board layout to be used by player 2",
                        dest='p2_layout', type=str, default="LayoutRandom")
    parser.add_argument('--p2-play', help="The play strategy to be used by player 2",
                        dest='p2_play', type=str, default="PlayRandom")
    parser.add_argument('--verbose', help="Enable verbose output whilst running simulation",
                        action='store_true')
    args = parser.parse_args()

    try:
        if args.list_layouts:
            LayoutBase.list_layouts()
        elif args.list_plays:
            PlayBase.list_plays()
        else:
            # Need to convert pieces to a dict array as this will be used to track
            # when a particular pieces is sunk. Care should be taken not to use
            # values below 65 as the intention is that those characters may be used
            # to indicate special conditions on the board.
            pieces = dict()
            for i, piece in enumerate(args.pieces.split(",")):
                pieces[chr(i+65)] = int(piece)

            game = Game(args.width, args.height, args.num_games, pieces,
                        args.p1_layout, args.p1_play, args.p2_layout, args.p2_play, args.verbose)
            game.play()
            game.display_stats()
    except GameError as err:
        print("Simulation failed with the error:\n\t{}".format(err.msg))

if __name__ == "__main__":
    main()
