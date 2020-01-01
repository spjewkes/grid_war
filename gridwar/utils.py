#!/usr/bin/env python3

"""
Define utility function an classes for this application.
"""
class GameError(Exception):
    """
    Defines the exception used by the Gridwar program.
    """
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
