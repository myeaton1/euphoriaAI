from random import randint

class Player:

	def __init__(self,dilemma,recruits):

		# Initialize starting goods/attributes
		self.energy = 0
		self.water = 0
		self.food = 0
		self.bliss = 0

		self.gold = 0
		self.stone = 0
		self.clay = 0

		self.morale = 1
		self.knowledge = 3

		self.dilemma = dilemma

		self.recruits = recruits

		# Workers

		self.totalWorkers = 2
		self.activeWorkers = 0

		self.workers = []

		self.retrieveWorkers(totalWorkers)

	def retrieveWorkers(self,n):

		while n > 0:
			self.workers.append(randint(1,6))
			n-=1

		




