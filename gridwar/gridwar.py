#!/usr/bin/env python
import sys
import argparse
import random
from layouts import LayoutBase
from plays import PlayBase

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

    def set_attack_result(self, attack_pos, hit):
        self.play.result(attack_pos, hit)
        if hit:
            self.tracking_board.set(attack_pos, 1)
        else:
            self.tracking_board.set(attack_pos, -1)

    def is_hit(self, attack_pos):
        if self.board.get(attack_pos) is not 0:
            self.board.set(attack_pos, 0)
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
