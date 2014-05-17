__author__ = 'Tom Schaul, tom@idsia.ch'


from pybrain.rl.agents.agent import Agent
from euphoria import EuphoriaGame
from random import choice
from numpy import array


class EuphoriaRandomPlayer(Agent):
    """ a class of agent that can play Euphoria, i.e. provides actions in the format:
    (playerid, position)
    playerid is self.color, by convention.
    It generally also has access to the game object. """
    def __init__(self, game, color = EuphoriaGame.BLACK, **args):
        self.game = game
        self.color = color
        self.setArgs(**args)

    def getAction(self):
    	randLegal = self.game.actionInterpreter(choice(self.game.legalMoves(self.color)))
    	# print '\n legal moves rand: ', self.game.legalMoves(self.color), '\n'
    	# print self.game.locationP
        return array([randLegal])

    def integrateObservation(self, obs = None):
        pass
