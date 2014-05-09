from player import *

class Game:
	def __init__(self):

		self.p = [Player(), Player()]

		self.turn = 0

		# Initialize markets

		# Deal out moral dilemmas

		# Deal out recruits

		# Initialize factions
		#Euphorians
		self.factions = dict(euphoran=None,subterran=None,
			wastelander=None,icarite=None)

		self.factions['euphorian'] = dict(num=0,com='energy',
			resource='gold',isMine=True,mine=0,allegiance=0,
			name='euphorian')
		self.factions['subterran'] = dict(num=1,com='water',
			resource='stone',isMine=True,mine=0,allegiance=0,
			name='subterran')
		self.factions['wastelander'] = dict(num=2,com='food',
			resource='brick',isMine=True,mine=0,allegiance=0,
			name='wastelander')
		self.factions['icarite'] = dict(num=3,com='bliss',
			resource=None,isMine=False,mine=0,allegiance=0,
			name='icarite')

		# Initialize Locations
		self.location = []
		for i in range(4):
			self.location.append([])
			for j in range(14):
				self.location[i].append([])

		# Initialize allegiance tracks


	def useMultiUse(self,faction,worker):

		self.location[faction['num']][0].append(worker)

		if sum(self.location[faction['num']][0]) <= 4:
			# 1 commodity + allegiance track +1
			self.p[self.turn].resources[faction['com']] += (
				1 + self.checkAllegianceBonus(faction,'com'))

			self.factions[faction['name']]['allegiance']+=1

		if (sum(self.location[faction['num']][0]) >= 5 & 
			sum(self.location[faction['num']][0]) <= 8):
			#
			self.p[self.turn].resources[faction['com']] += (
				1 + self.checkAllegianceBonus(faction,'com'))

			self.p[self.turn].resources['knowledge']-=1
			if self.p[self.turn].resources['knowledge']<=0:
				self.p[self.turn].resources['knowledge'] = 1

		if sum(self.location[faction['num']][0]) >= 9:
			self.p[self.turn].resources[faction['com']] += (
				2 + self.checkAllegianceBonus(faction,'com'))

			self.p[self.turn].resources['knowledge']+=1
			if self.p[self.turn].resources['knowledge']>=7:
				self.p[self.turn].resources['knowledge'] = 6



	def checkAllegianceBonus(self,faction,type):
		# if faction['allegiance'] >= 2:
		# 	#extra commodity

		# if faction['allegiance'] >= 5:
		# 	# mine bonus

		# if faction['allegiance'] == 8:
		# 	# flip recruits

		# if faction['allegiance'] == 11:
		# 	# place stars on recruits

		return 0






		