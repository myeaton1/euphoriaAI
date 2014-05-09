from numpy import *

class tempSpace:

	def __init__(self,cost,reward,isOptionalCost=False,
				optionalCost=None,isOptionalReward=False,
				optionalReward=None):

		self.cost = cost
		self.reward = reward

		if isOptionalCost:
			self.optionalCost = optionalCost

		if isOptionalReward:
			self.optionalReward = optionalReward

		occupant = None

	def use(self,player):

		player.resource[self.cost]-=



