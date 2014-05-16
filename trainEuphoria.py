from scipy import * #@UnusedWildImport
import pylab
import random

from euphoria import EuphoriaGame
from euphoriatask import EuphoriaTask
from euavnetwork import euActionValueNetwork
from eulearning import EuphoriaLearningAgent
from pybrain.rl.learners import Q, SARSA #@UnusedImport
from pybrain.rl.experiments import Experiment

environment 	= 	EuphoriaGame()

controller 		= 	euActionValueNetwork(582,113)

learner 		= 	Q()

agent 			= 	EuphoriaLearningAgent(controller, learner)

task 			= 	EuphoriaTask(agent)

experiment = Experiment(task, agent)
i = 0
while i<10:
    experiment.doInteractions(100)
    agent.learn()
    agent.reset()

    i+=1
