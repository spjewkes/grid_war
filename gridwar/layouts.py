import random
from gridwar.utils import GameError

class LayoutBase(object):
    _layouts = []

    @classmethod
    def register(cls, layout_class):
        cls._layouts.append(layout_class)

    @classmethod
    def list_layouts(cls):
        for i, c in enumerate(cls._layouts):
            print("{} - '{}' ({})".format(i+1, c.__name__, c.desc()))

    @classmethod
    def is_valid(cls, layout_name):
        for c in cls._layouts:
            if layout_name == c.__name__:
                return True
        return False

    @classmethod
    def get_class(cls, layout_name):
        if cls.is_valid(layout_name) is not True:
            raise GameError("Layout name '{}' has not been registered".format(layout_name))
        for c in cls._layouts:
            if layout_name == c.__name__:
                return c
        return None

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return self.__class__.__name__

    def place(self, piece):
        """
        Place piece at desired position on a player's board. Returning true if successful,
        otherwise returns false.
        """
        return False

class LayoutRandom(LayoutBase):
    @classmethod
    def desc(cls):
        return "Positions ships randomly, avoiding overlap"

    def place(self, key, size):
        if random.randint(0, 1) == 0:
            width, height = self.player.board.width, self.player.board.height - size
            vertical = True
        else:
            width, height = self.player.board.width - size, self.player.board.height
            vertical = False
        # It would be nice not to have to keep retrying until the piece fits
        # but this seems like a simple compromise for the time being
        for i in range(0, 100):
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if self.player.check_place_piece(size, vertical, pos) is True:
                self.player.place_piece(key, size, vertical, pos)
                return True
        return False

LayoutBase.register(LayoutRandom)

class LayoutRandomGap(LayoutBase):
    @classmethod
    def desc(cls):
        return "Positions ships randomly, avoiding overlap and keeping a buffer of one space around each"

    def place(self, key, size):
        offsets = ((1,1), (1, 0), (1, -1), (0, 1), (0, 0), (0, -1), (-1, 1), (-1, 0), (-1, -1))

        apply_offset = lambda x, y: (x[0]+y[0], x[1]+y[1])
        outside_board = lambda p: True if (p[0]<0 or p[0]>=self.player.board.width or p[1]<0 or p[1]>=self.player.board.height) else False
        # Not the cleverest way of doing this but try a 100 times to set the piece. Always
        # vary the orientation to increase the chance of success
        for i in range(0, 100):
            if random.randint(0, 1) == 0:
                width, height = self.player.board.width, self.player.board.height - size
                vertical = True
            else:
                width, height = self.player.board.width - size, self.player.board.height
                vertical = False
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            collide = False
            for o in offsets:
                test_offset = apply_offset(pos, o)
                if (self.player.check_place_piece(size, vertical, test_offset) is False and
                    outside_board(test_offset) is False):
                    collide = True
                    break

            if not collide:
                self.player.place_piece(key, size, vertical, pos)
                return True

        return False
        
LayoutBase.register(LayoutRandomGap)
