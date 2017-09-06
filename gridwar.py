#!/usr/bin/env python
import sys
import argparse

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

if __name__ == "__main__":
    main()
