#!/usr/bin/env python
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Iteratively runs Battleship games automatically and display results")
    parser.add_argument('--width', help="Width of game board", dest='width', type=int, default=10)
    parser.add_argument('--height', help="Height of game board", dest='height', type=int, default=10)
    parser.add_argument('--games', help="Number of games to play", dest='num_games', type=int, default=100)
    args = parser.parse_args()

if __name__ == "__main__":
    main()
