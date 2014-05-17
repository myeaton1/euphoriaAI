__author__ = 'Tom Schaul, tom@idsia.ch'


from inspect import isclass
from pybrain.utilities import  Named
from euphoria import EuphoriaGame
# from euphoriaplayers import RandomEuphoriaPlayer
# from pybrain.rl.environments.twoplayergames.gomokuplayers.gomokuplayer import GomokuPlayer
from pybrain.structure.modules.module import Module
from pybrain.rl.environments.episodic import EpisodicTask


class EuphoriaTask(EpisodicTask, Named):
    """ The task of winning the maximal number of Gomoku games against a fixed opponent. """

    # first game, opponent is black
    opponentStart = False

    # on subsequent games, starting players are alternating
    alternateStarting = False

    # numerical reward value attributed to winning
    winnerReward = 1.

    # coefficient determining the importance of long vs. short games w.r. to winning/losing
    numMovesCoeff = 0.

    # average over some games for evaluations
    averageOverGames = 10

    # noisy = True

    def __init__(self, opponent = None, **args):
        EpisodicTask.__init__(self, EuphoriaGame())
        self.setArgs(**args)
        if opponent == None:
            opponent = RandomEuphoriaPlayer(self.env)
        elif isclass(opponent):
            # assume the agent can be initialized without arguments then.
            opponent = opponent(self.env)
        if not self.opponentStart:
            opponent.color = EuphoriaGame.WHITE
        self.opponent = opponent
        # self.minmoves = 9
        # self.maxmoves = self.env.size[0] * self.env.size[1]
        self.reset()

    def reset(self):
        self.switched = False
        EpisodicTask.reset(self)
        if self.opponent.color == EuphoriaGame.BLACK:
            # first move by opponent
            self.opponent.game = self.env
            EpisodicTask.performAction(self, (EuphoriaGame.BLACK,self.opponent.getAction()))

    def isFinished(self):
        res = self.env.gameOver()
        if res and self.alternateStarting and not self.switched:
            # alternate starting player
            self.opponent.color = (self.opponent.color + 1)%2
            self.switched = True
        return res

    def getReward(self):
        """ Final positive reward for winner, negative for loser. """
        if self.isFinished():
            if self.env.winner == self.env.DRAW:
                return 0
            win = (self.env.winner != self.opponent.color)
            # moves = self.env.movesDone
            res = self.winnerReward
            if not win:
                res *= -1
            if self.alternateStarting and self.switched:
                # opponent color has been inverted after the game!
                res *= -1
            return res
        else:
            return 0

    def performAction(self, action):
        # agent.game = self.env
        if self.opponentStart:
            EpisodicTask.performAction(self, (EuphoriaGame.WHITE, action))
        else:
            EpisodicTask.performAction(self, (EuphoriaGame.BLACK, action))
        if not self.isFinished():
            self.opponent.game = self.env
            if self.opponentStart:
                EpisodicTask.performAction(self, (EuphoriaGame.BLACK,self.opponent.getAction()))
            else:
                EpisodicTask.performAction(self, (EuphoriaGame.WHITE,self.opponent.getAction()))

    def f(self, x):
        """ If a module is given, wrap it into a ModuleDecidingAgent before evaluating it.
        Also, if applicable, average the result over multiple games. """
        if isinstance(x, Module):
            agent = ModuleDecidingPlayer(x, self.env, greedySelection = True)
        elif isinstance(x, EuphoriaRandomPlayer):
            agent = x
        else:
            raise NotImplementedError('Missing implementation for '+x.__class__.__name__+' evaluation')
        res = 0
        agent.game = self.env
        self.opponent.game = self.env
        for dummy in range(self.averageOverGames):
            agent.color = -self.opponent.color
            res += EpisodicTask.f(self, agent)
        return res / float(self.averageOverGames)



