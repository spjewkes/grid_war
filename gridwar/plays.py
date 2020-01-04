#!/usr/bin/env python3

"""
Manages the different play styles that a player can be set to.
"""

import random
from gridwar.utils import GameError
from gridwar.board import Board

class PlayBase:
    """
    Base class used to descibe all plays.
    """
    _plays = []

    @classmethod
    def register(cls, play_class):
        """
        Register a play (so it can be selected when running the game).
        """
        cls._plays.append(play_class)

    @classmethod
    def list_plays(cls):
        """
        List the registered plays.
        """
        for i, c in enumerate(cls._plays):
            print("{} - '{}' ({})".format(i+1, c.__name__, c.desc()))

    @classmethod
    def is_valid(cls, play_name):
        """
        Checks if a play name is valid.
        """
        for c in cls._plays:
            if play_name == c.__name__:
                return True
        return False

    @classmethod
    def get_class(cls, play_name):
        """
        Retrieve a specific play class.
        """
        if cls.is_valid(play_name) is not True:
            raise GameError("Play name '{}' has not been registered".format(play_name))
        for c in cls._plays:
            if play_name == c.__name__:
                return c
        return None

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return self.__class__.__name__

    def play(self):
        """
        Makes a move.
        """
        return (-1, -1)

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        None

class PlayRandom(PlayBase):
    """
    Randomly attack the board.
    """
    def __init__(self, player):
        super(PlayRandom, self).__init__(player)
        self.plays = [(x, y) for x in range(player.board.width) for y in range(player.board.height)]
        random.shuffle(self.plays)

    @classmethod
    def desc(cls):
        """
        String description of this play.
        """
        return "Randomly selects grid position"

    def play(self):
        """
        Makes a move.
        """
        return self.plays.pop()

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        None

PlayBase.register(PlayRandom)

class PlayScan(PlayBase):
    """
    Play by scaning the board from left to right, top to bottom.
    """
    def __init__(self, player):
        super(PlayScan, self).__init__(player)
        self.plays = [(x, y) for x in range(player.board.width) for y in range(player.board.height)]

    @classmethod
    def desc(cls):
        """
        String description of this play.
        """
        return "Scans every grid position starting from top left going to bottom right"

    def play(self):
        """
        Makes a move.
        """
        return self.plays.pop(0)

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        None

PlayBase.register(PlayScan)

class PlayScanAndHomeIn(PlayScan):
    """
    Play by scanning the board but homing in on a successful hit.
    """
    def __init__(self, player):
        super(PlayScanAndHomeIn, self).__init__(player)
        self.homing = None

    @classmethod
    def desc(cls):
        """
        String description of this play.
        """
        return "The same as scan but homes in on a hit"

    def play(self):
        """
        Makes a move.
        """
        if self.homing is not None:
            play = self.homing.play()
            if play is not None:
                if play in self.plays:
                    self.plays.remove(play)
                return play

            self.homing = None

        # If we reach here then just take a try off the play list
        return super(PlayScanAndHomeIn, self).play()

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        if is_hit:
            if sunk:
                self.homing = None
            elif not self.homing:
                self.homing = HomeIn(attack_pos, self.player)

        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit, sunk)

PlayBase.register(PlayScanAndHomeIn)

class PlaySkipScanAndHomeIn(PlayScan):
    """
    Play by scanning at just enough to hit the smallest remaining ship.
    """
    def __init__(self, player):
        super(PlaySkipScanAndHomeIn, self).__init__(player)
        self.homing = None
        self.skipped_plays = list()
        self._regenerate_scan()

    @classmethod
    def desc(cls):
        """
        String description of this play.
        """
        return "Scans in a pattern that will find the smallest remaining ship and then homes in"

    def play(self):
        """
        Makes a move.
        """
        if self.homing is not None:
            play = self.homing.play()
            if play is not None:
                if play in self.plays:
                    self.plays.remove(play)
                if play in self.skipped_plays:
                    self.skipped_plays.remove(play)
                return play

            self._regenerate_scan()
            self.homing = None

        if len(self.plays) == 0:
            # When original plays have been used up, return one of the discarded ones
            random.shuffle(self.skipped_plays)
            return self.skipped_plays.pop(0)
        
        return self.plays.pop(0)

    def _regenerate_scan(self):
        """
        Regenerates the plays based on the new stepping requirements. This starts by
        combining the remaining plays (and skipped plays) and resplitting them based
        on the new stepping.
        """
        smallest_ship = min(self.player.opponent_pieces.values())
        new_plays = list()
        new_skipped_plays = list()
        for play in [*self.plays, *self.skipped_plays]:
            if sum(play) % smallest_ship == 0:
                new_plays.append(play)
            else:
                new_skipped_plays.append(play)
        self.plays = new_plays
        self.skipped_plays = new_skipped_plays

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        if is_hit:
            if sunk:
                self.homing = None
            elif not self.homing:
                self.homing = HomeIn(attack_pos, self.player)

        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit, sunk)

PlayBase.register(PlaySkipScanAndHomeIn)

class PlayRandomAndHomeIn(PlayRandom):
    """
    Play randomly but home in on a successful hit.
    """
    def __init__(self, player):
        super(PlayRandomAndHomeIn, self).__init__(player)
        self.homing = None

    @classmethod
    def desc(cls):
        """
        String description of this play.
        """
        return "The same as random but homes in on a hit"

    def play(self):
        """
        Makes a move.
        """
        if self.homing is not None:
            play = self.homing.play()
            if play is not None:
                if play in self.plays:
                    self.plays.remove(play)
                return play

            self.homing = None

        # If we reach here then just take a try off the play list
        return super(PlayRandomAndHomeIn, self).play()

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        if is_hit:
            if sunk:
                self.homing = None
            elif not self.homing:
                self.homing = HomeIn(attack_pos, self.player)

        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit, sunk)

PlayBase.register(PlayRandomAndHomeIn)

class HomeIn:
    """
    Define a class for managing homing in strategy used by plays.
    """
    def __init__(self, init_hit, player):
        self.init_hit = init_hit
        self.player = player

        # Set up attempts. Do both horizontals first, followed by both verticals
        self.attempts = []
        sx, sy = init_hit
        tries = []
        for x in range(sx + 1, self.player.board.width, 1):
            pos = (x, sy)
            hit = player.tracking_board.get(pos)
            if hit == Board.EMPTY:
                tries.append(pos)
            elif hit == Board.MISS:
                break
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for x in range(sx - 1, -1, -1):
            pos = (x, sy)
            hit = player.tracking_board.get(pos)
            if hit == Board.EMPTY:
                tries.append(pos)
            elif hit == Board.MISS:
                break
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for y in range(sy + 1, self.player.board.height, 1):
            pos = (sx, y)
            hit = player.tracking_board.get(pos)
            if hit == Board.EMPTY:
                tries.append(pos)
            elif hit == Board.MISS:
                break
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for y in range(sy - 1, -1, -1):
            pos = (sx, y)
            hit = player.tracking_board.get(pos)
            if hit == Board.EMPTY:
                tries.append(pos)
            elif hit == Board.MISS:
                break
        if len(tries) > 0:
            self.attempts.append(tries)

    def play(self):
        """
        Makes a move.
        """
        if len(self.attempts) == 0:
            self.attempts = None
            return None

        while len(self.attempts[0]) == 0:
            self.attempts.pop(0)
            if len(self.attempts) == 0:
                self.attempts = None
                return None

        return self.attempts[0].pop(0)

    def result(self, attack_pos, is_hit, sunk):
        """
        Update state base on result of play.
        """
        if self.attempts is None:
            raise GameError("No attempts lists to handle the result")
        if len(self.attempts) == 0:
            raise GameError("Attempts list is empty")
        if is_hit is False:
            # Current attempts list resulted in a miss, so remove it
            del self.attempts[0]
