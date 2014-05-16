from scipy import * #@UnusedWildImport
import pylab
import random

from euphoria import EuphoriaGame
from euphoriatask import EuphoriaTask
from euavnetwork import euActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q, SARSA #@UnusedImport
from pybrain.rl.experiments import Experiment

g = EuphoriaGame()

win = []
lMoves = []
for i in range(10):
	g = EuphoriaGame()

	over = False
	while not over:

		m = random.choice(g.legalMoves(g.turn))
		# print 'm = ', m, ' turn = ', g.turn, ' turn # = ', g.turnCounter
		g.doMove(g.turn,m)

		over = g.over

	if g.winner() in [0,1]:
		win.append(g.winner())

print sum(win)/float(len(win))


# g.move([0,4,0,0,0,g.p[0].workers[0]])

# g.move([0,0,0,0,0,g.p[0].workers[0]])

# g.move([0,1,0,0,0,g.p[0].workers[0]])

# g.legalMoves()
