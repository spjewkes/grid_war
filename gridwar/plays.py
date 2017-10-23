#!/usr/bin/env python
import sys
import argparse
import random

class PlayBase(object):
    _plays = []

    @classmethod
    def register(cls, play_class):
        cls._plays.append(play_class)

    @classmethod
    def list_plays(cls):
        for i, c in enumerate(cls._plays):
            print("{} - '{}'".format(i+1, c.__name__))

    @classmethod
    def is_valid(cls, play_name):
        for c in cls._plays:
            if play_name == c.__name__:
                return True
        return False

    @classmethod
    def get_class(cls, play_name):
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
        return (-1, -1)

    def result(self, attack_pos, is_hit):
        None

class PlayRandom(PlayBase):
    def __init__(self, player):
        super(PlayRandom, self).__init__(player)
        self.plays = [ (x, y) for x in range(player.board.width) for y in range(player.board.height) ]
        random.shuffle(self.plays)

    def play(self):
        return self.plays.pop()

    def result(self, attack_pos, is_hit):
        None

PlayBase.register(PlayRandom)

class PlayScan(PlayBase):
    def __init__(self, player):
        super(PlayScan, self).__init__(player)
        self.plays = [ (x,y) for x in range(player.board.width) for y in range(player.board.height) ]

    def play(self):
        return self.plays.pop()

    def result(self, attack_pos, is_hit):
        None

PlayBase.register(PlayScan)

class PlayScanAndHomeIn(PlayScan):
    def __init__(self, player):
        super(PlayScanAndHomeIn, self).__init__(player)
        self.homing = None

    def play(self):
        if self.homing is not None:
            play = self.homing.play()
            if play is not None:
                if play in self.plays:
                    self.plays.remove(play)
                return play
            else:
                self.homing = None

        # If we reach here then just take a try off the play list
        return super(PlayScanAndHomeIn, self).play()

    def result(self, attack_pos, is_hit):
        if is_hit is True and self.homing is None:
            self.homing = HomeIn(attack_pos, self.player)
        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit)

PlayBase.register(PlayScanAndHomeIn)

class PlayRandomAndHomeIn(PlayRandom):
    def __init__(self, player):
        super(PlayRandomAndHomeIn, self).__init__(player)
        self.homing = None
    def play(self):
        if self.homing is not None:
            play = self.homing.play()
            if play is not None:
                if play in self.plays:
                    self.plays.remove(play)
                return play
            else:
                self.homing = None

        # If we reach here then just take a try off the play list
        return super(PlayRandomAndHomeIn, self).play()

    def result(self, attack_pos, is_hit):
        if is_hit is True and self.homing is None:
            self.homing = HomeIn(attack_pos, self.player)
        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit)

PlayBase.register(PlayRandomAndHomeIn)

class HomeIn(object):
    def __init__(self, init_hit, player):
        self.init_hit = init_hit
        self.player = player

        # Set up attempts. Do both horizontals first, followed by both verticals
        self.attempts = []
        max_size = max(self.player.pieces)
        sx, sy = init_hit
        tries = []
        for x in range(sx + 1, self.player.board.width, 1):
            tries.append((x,sy))
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for x in range(sx - 1, -1, -1):
            tries.append((x,sy))
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for y in range(sy + 1, self.player.board.height, 1):
            tries.append((sx, y))
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for y in range(sy - 1, -1, -1):
            tries.append((sx, y))
        if len(tries) > 0:
            self.attempts.append(tries)

    def play(self):
        if len(self.attempts) is 0:
            self.attempts = None
            return None
        else:
            while len(self.attempts[0]) is 0:
                self.attempts.pop(0)
                if len(self.attempts) is 0:
                    self.attempts = None
                    return None

        return self.attempts[0].pop(0)

    def result(self, attack_pos, is_hit):
        if self.attempts is None:
            raise GameError("No attempts lists to handle the result")
        if len(self.attempts) == 0:
            raise GameError("Attempts list is empty")
        if is_hit is False:
            # Current attempts list resulted in a miss, so remove it
            del(self.attempts[0])
