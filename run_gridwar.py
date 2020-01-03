#!/usr/bin/env python3

"""
This program runs simulations of the popular Battleships board game. Allowing for each player
to select specific board layouts and styles of play as means of seeing which one is likely
to have a higher chance of success.
"""

import argparse
import json

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
    parser.add_argument('--config', help="Configuration file defining game settings", dest="config",
                        type=str, default="config.json")
    parser.add_argument('--list-layouts', help="List the available board layouts",
                        action='store_true')
    parser.add_argument('--list-plays', help="List the available play strategies",
                        action='store_true')
    parser.add_argument('--verbose', help="Enable verbose output whilst running simulation",
                        action='store_true')
    args = parser.parse_args()

    with open(args.config, 'r') as myfile:
        config = json.load(myfile)

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
            for i, piece in enumerate(config["pieces"].split(",")):
                pieces[chr(i+65)] = int(piece)

            game = Game(config["width"], config["height"], config["num_games"], pieces,
                        config["layout"]["p1"], config["play"]["p1"],
                        config["layout"]["p2"], config["play"]["p2"], args.verbose)
            game.play()
            game.display_stats()
    except GameError as err:
        print("Simulation failed with the error:\n\t{}".format(err.msg))

if __name__ == "__main__":
    main()
