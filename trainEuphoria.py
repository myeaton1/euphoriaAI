from scipy import * #@UnusedWildImport
import pylab
import random

from euphoria import EuphoriaGame
from euphoriatask import EuphoriaTask
from euavnetwork import euActionValueNetwork
from eulearning import EuphoriaLearningAgent
from euphoriarandplayer import EuphoriaRandomPlayer
from pybrain.rl.learners import Q, SARSA #@UnusedImport
from eunfq import NFQ
from pybrain.rl.experiments.episodic import EpisodicExperiment

import timeit

environment 	= 	EuphoriaGame()

controller 		= 	euActionValueNetwork(582,113)

learner 		= 	NFQ()

agent 			= 	EuphoriaLearningAgent(controller,learner)

agentOp 		= 	EuphoriaRandomPlayer(environment)

task 			= 	EuphoriaTask(agentOp)

experiment 		= 	EpisodicExperiment(task, agent)

i = 0
reward = []
while i<1:
	tic=timeit.default_timer()

	r = experiment.doEpisodes(1)
	for ri in r:
		reward.append(ri[-1])

	# print reward
	# agent.learn()
	# agent.reset()

	toc=timeit.default_timer()
	print toc - tic #elapsed time in seconds

	i+=1

    # print i, reward

