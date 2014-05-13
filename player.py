from random import randint

class Player:

	def __init__(self,dilemma=None,recruits=None):

		# Initialize starting goods/attributes
		self.resources = dict(energy=0,water=0,food=0,bliss=0,
			gold=0,stone=0,brick=0,morale=1,knowledge=3,stars=10,
			bat=0,book=0,bear=0,balloon=0,glasses=0,game=0,
			recruit2Active=False)

		self.dilemma = dilemma

		self.recruits = recruits
		self.recruitStar = [False,False]

		# Workers

		self.totalWorkers = 2
		self.nActiveWorkers = 0
		self.nLatentWorkers = 0

		self.workers = []

		self.retrieveWorkers(self.totalWorkers,'morale')

	def retrieveWorkers(self,n,cost=None):

		if cost:
			self.resources[cost]-=1

			if self.resources['morale'] == 0:
				self.resources['morale'] = 1

		while n > 0:
			self.workers.append(randint(1,6))
			n-=1

		self.checkKnowledge()

		self.nActiveWorkers = len(self.workers)


	def checkKnowledge(self):

		knowCap = 16
		currentKnow = sum(self.workers) + self.resources['knowledge']

		if currentKnow >= knowCap:
			self.workers.sort()
			self.workers.pop()

			self.totalWorkers -= 1











