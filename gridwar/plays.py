import random
from utils import GameError

class PlayBase(object):
    _plays = []

    @classmethod
    def register(cls, play_class):
        cls._plays.append(play_class)

    @classmethod
    def list_plays(cls):
        for i, c in enumerate(cls._plays):
            print("{} - '{}' ({})".format(i+1, c.__name__, c.desc()))

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

    def result(self, attack_pos, is_hit, sunk):
        None

class PlayRandom(PlayBase):
    def __init__(self, player):
        super(PlayRandom, self).__init__(player)
        self.plays = [ (x, y) for x in range(player.board.width) for y in range(player.board.height) ]
        random.shuffle(self.plays)

    @classmethod
    def desc(cls):
        return "Randomly selects grid position"

    def play(self):
        return self.plays.pop()

    def result(self, attack_pos, is_hit, sunk):
        None

PlayBase.register(PlayRandom)

class PlayScan(PlayBase):
    def __init__(self, player):
        super(PlayScan, self).__init__(player)
        self.plays = [ (x,y) for x in range(player.board.width) for y in range(player.board.height) ]

    @classmethod
    def desc(cls):
        return "Scans every grid position starting from top left going to bottom right"

    def play(self):
        return self.plays.pop(0)

    def result(self, attack_pos, is_hit, sunk):
        None

PlayBase.register(PlayScan)

class PlayScanAndHomeIn(PlayScan):
    def __init__(self, player):
        super(PlayScanAndHomeIn, self).__init__(player)
        self.homing = None

    @classmethod
    def desc(cls):
        return "The same as scan but homes in on a hit"

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

    def result(self, attack_pos, is_hit, sunk):
        if is_hit is True and self.homing is None:
            self.homing = HomeIn(attack_pos, self.player)
        elif is_hit is True and sunk is not None and self.homing is not None:
            self.homeing = None
        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit, sunk)

PlayBase.register(PlayScanAndHomeIn)

class PlaySkipScanAndHomeIn(PlayScan):
    def __init__(self, player):
        super(PlaySkipScanAndHomeIn, self).__init__(player)
        self.homing = None

    @classmethod
    def desc(cls):
        return "Scans in a pattern that will find the smallest remaining ship and then homes in"

    def play(self):
        if self.homing is not None:
            play = self.homing.play()
            if play is not None:
                if play in self.plays:
                    self.plays.remove(play)
                return play
            else:
                self.homing = None

        # If we reach here then continue with pattern
        smallest_ship = min(self.player.opponent_pieces.itervalues())
        # DEBUG
        if len(self.plays) is 0:
            print self.player.tracking_board
        # DEBUG
        while sum(self.plays[0]) % smallest_ship is not 0:
            self.plays.pop(0)

        return self.plays.pop(0)

    def result(self, attack_pos, is_hit, sunk):
        if is_hit is True and self.homing is None:
            self.homing = HomeIn(attack_pos, self.player)
        elif is_hit is True and sunk is not None and self.homing is not None:
            self.homeing = None
        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit, sunk)

PlayBase.register(PlaySkipScanAndHomeIn)

class PlayRandomAndHomeIn(PlayRandom):
    def __init__(self, player):
        super(PlayRandomAndHomeIn, self).__init__(player)
        self.homing = None

    @classmethod
    def desc(cls):
        return "The same as random but homes in on a hit"

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

    def result(self, attack_pos, is_hit, sunk):
        if is_hit is True and self.homing is None:
            self.homing = HomeIn(attack_pos, self.player)
        elif is_hit is True and sunk is not None and self.homing is not None:
            self.homeing = None
        elif self.homing is not None:
            self.homing.result(attack_pos, is_hit, sunk)

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
            pos = (x,sy)
            hit = player.tracking_board.get(pos)
            if hit is ' ':
                tries.append(pos)
            if hit is '_':
                break
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for x in range(sx - 1, -1, -1):
            pos = (x,sy)
            hit = player.tracking_board.get(pos)
            if hit is ' ':
                tries.append(pos)
            if hit is '_':
                break
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for y in range(sy + 1, self.player.board.height, 1):
            pos = (sx, y)
            hit = player.tracking_board.get(pos)
            if hit is ' ':
                tries.append(pos)
            if hit is '_':
                break
        if len(tries) > 0:
            self.attempts.append(tries)
        tries = []
        for y in range(sy - 1, -1, -1):
            pos = (sx, y)
            hit = player.tracking_board.get(pos)
            if hit is ' ':
                tries.append(pos)
            if hit is '_':
                break
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

    def result(self, attack_pos, is_hit, sunk):
        if self.attempts is None:
            raise GameError("No attempts lists to handle the result")
        if len(self.attempts) == 0:
            raise GameError("Attempts list is empty")
        if is_hit is False:
            # Current attempts list resulted in a miss, so remove it
            del(self.attempts[0])
