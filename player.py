from random import randint

class Player:

	def __init__(self,dilemma=0,recruits=0):

		# Initialize starting goods/attributes
		self.resources = dict(energy=0,water=0,food=0,bliss=0,
			gold=0,stone=0,clay=0,morale=1,knowledge=3)

		self.dilemma = dilemma

		self.recruits = recruits

		# Workers

		self.totalWorkers = 2
		self.nActiveWorkers = 0
		self.nLatentWorkers = 0

		self.workers = []

		self.retrieveWorkers(self.totalWorkers,'morale')

	def retrieveWorkers(self,n,cost):

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

	# def placeWorker(self, workerN, location):











