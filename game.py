from player import *

class Game:
	def __init__(self):
		from random import shuffle, randint

		self.pNum = 2

		self.turn = 0

		# Deal out moral dilemmas
		dilemma = ['bat','book','bear','balloon','glasses','game']
		shuffle(dilemma)

		# Create players, deal out recruits
		self.p = [Player(dilemma[0],[randint(0,3),randint(0,3)]), 
			Player(dilemma[1],[randint(0,3),randint(0,3)])]

		# Initialize factions
		self.factions = []

		self.factions.append(dict(num=0,com='energy',
			resource='gold',isMine=True,mine=0,allegiance=0,
			starSlots=self.pNum,market1=False,market2=False,
			endMine=False,name='euphorian'))
		self.factions.append(dict(num=1,com='water',
			resource='stone',isMine=True,mine=0,allegiance=0,
			starSlots=self.pNum,market1=False,market2=False,
			endMine=False,name='subterran'))
		self.factions.append(dict(num=2,com='food',
			resource='brick',isMine=True,mine=0,allegiance=0,
			starSlots=self.pNum,market1=False,market2=False,
			endMine=False,name='wastelander'))
		self.factions.append(dict(num=3,com='bliss',
			resource=None,isMine=False,mine=0,allegiance=0,
			starSlots=self.pNum,name='icarite'))

		# Initialize Locations, randomize markets
		self.initLoc()

		# Build, shuffle artifact deck
		self.buildArtifactDeck()


	def useMultiUse(self,faction,workerVal):

		self.workerDrop(faction,0,workerVal)							# add new worker die

		if sum(self.location[faction['num']][0]) <= 4:
			# 1 commodity + allegiance track +1
			self.p[self.turn].resources[faction['com']] += (1 + self.comAllegianceBonus(faction))

			self.factions[faction['num']]['allegiance']+=1

		if (sum(self.location[faction['num']][0]) >= 5 and sum(self.location[faction['num']][0]) <= 8):
			#
			self.p[self.turn].resources[faction['com']] += (1 + self.comAllegianceBonus(faction))

			self.p[self.turn].resources['knowledge']-=1
			if self.p[self.turn].resources['knowledge']<=0:
				self.p[self.turn].resources['knowledge'] = 1

		if sum(self.location[faction['num']][0]) >= 9:
			self.p[self.turn].resources[faction['com']] += (2 + self.comAllegianceBonus(faction))

			self.p[self.turn].resources['knowledge']+=1
			if self.p[self.turn].resources['knowledge']>=7:
				self.p[self.turn].resources['knowledge'] = 6

	def comAllegianceBonus(self,faction):
		if ((self.p[self.turn].recruits[0] == faction['num']) or
			((self.p[self.turn].recruits[0] == faction['num']) and
				(self.p[self.turn].resources['recruit2Active']))):

			if ((faction['allegiance'] >= 2) and (spaceType == 'com')):
				return 1

			else:
				return 0	
		else:
			return 0

		


	def useTemp(self,faction,locationN,workerVal,cost=None,reward=None):

		if len(self.location[faction['num']][locationN]) == 1:			# if we need to bump, then:
			facPair = [faction['num'],locationN]					# list of [ faction #, location key #]
			dieN = self.location[faction['num']][locationN][0]		# list of number of die in that location
			pN = self.locationP[faction['num']][locationN][0]		# list of player #s

			self.retrieve([facPair], [dieN], [pN])

		self.workerDrop(faction,locationN,workerVal)					# add new worker die

		if cost:
			for i in range(len(cost)):
				self.p[self.turn].resources[cost[i][0]]-=cost[i][1]

		if reward:
			# Check maintenance heavy rewards
			#	(allegiance,stars,worker,artifact)
			for i in range(len(cost)):
				if reward[i][0] == 'allegiance':
					self.factions[faction['num']]['allegiance']+=1
				elif reward[i][0] == 'star':
					self.factions[faction['num']]['starSlots']-=1
					self.p[self.turn].resources[reward[i][0]]-=reward[i][1]
				elif reward[i][0] == 'worker':
					self.p[self.turn].retrieveWorkers(1)
					self.p[self.turn].totalWorkers+=1
				elif reward[i][0] == 'artifact':
					for j in range(reward[i][1]):
						if not self.artifact:
							self.buildArtifactDeck()
						dealArt = self.artifact.pop()

						self.p[self.turn].resources[dealArt]+=1

				else:
					self.p[self.turn].resources[reward[i][0]]+=reward[i][1]

				# Make sure knowledge/morale not out of whack
				self.verifyMoraleKnowledgeRange()

	def useExclusive(self,faction,locationN,workerVal,cost=None):

		self.workerDrop(faction,locationN,workerVal)					# add new worker die

		if cost:
			for i in range(len(cost)):
				self.p[self.turn].resources[cost[i][0]]-=cost[i][1]

		if locationN in [1,2,3,4]:
			exRange = [1,2,3,4]
			marketLoc = 9
			marketN = 'market1'

		if locationN in [5,6,7,8]:
			exRange = [5,6,7,8]
			marketLoc = 10
			marketN='market2'

		# Check if market has been built
		totOcc = 0
		for i in exRange:
			totOcc+=len(self.location[faction['num']][i])

		# Check to see who helped, assign rewards, build market
		checkHelped = [False] * self.pNum
		if totOcc >= self.pNum:
			for i in exRange:
				if self.location[faction['num']][i]:
					facPair = [faction['num'],i]					# list of [ faction #, location key #]
					dieN = self.location[faction['num']][i][0]	# list of number of die in that location
					pN = self.locationP[faction['num']][i][0]		# list of player #s

					self.retrieve([facPair], [dieN], [pN])

					checkHelped[pN] = True

			for i in range(len(checkHelped)):
				if checkHelped[i]:
					self.p[i].resources['stars']-=1

					self.locationStars[faction['num']][marketLoc].append(i)	# record that player i has put a star here

			# Turn on market space
			self.factions[faction['num']][]

	def retrieve(self,locations,workerVal,pN,cost=None):

		for i in range(len(locations)):
			facN = locations[i][0]

			locN = locations[i][1]

			self.location[facN][locN].remove(workerVal[i])
			self.locationP[facN][locN].remove(pN[i])

		self.p[self.turn].retrieveWorkers(len(workerVal),cost)

	def workerDrop(self,faction,locationN,workerVal):

		self.location[faction['num']][locationN].append(workerVal)

		self.locationP[faction['num']][locationN].append(self.turn)

		self.p[self.turn].workers.remove(workerVal)

	def initLoc(self):
		from itertools import combinations_with_replacement

		self.buildMarketDeck()

		self.location = []
		self.locationP = []
		self.locationStars = []
		self.locationCR = []
		for i in range(4):
			self.location.append([])								# dice values 
			self.locationP.append([])
			self.locationStars.append([])
			self.locationCR.append([])
			for j in range(14):
				self.location[i].append([])
				self.locationP[i].append([])
				self.locationStars[i].append([])
				self.locationCR[i].append([])

		# Extra spaces for worker generation
		self.location.append([[],[]])
		self.locationP.append([[],[]])
		self.locationCR.append([[],[]])

		# # Label cost/rewards
		for i in range(3):
			facC = self.factions[i]['com']
			facR = self.factions[i]['resource']

			#Exclusive spaces, faction resources
			for j in [2,3,4,6,7,8]:
				self.locationCR[i][j] = [[[[facR,1]]],[[[]]]]
			# Exclusive spaces, non faction resources
			nonFac = range(3)
			nonFac.remove(i)
			for j in [1,5]:
				for f in nonFac:
					nonFacR = self.factions[f]['resource']
					self.locationCR[i][j] = [[[[nonFacR,1]]],[[[]]]]

			# Random market costs, fixed rewards
			for j in [9,10]:
				self.locationCR[i][j] = [self.market.pop(),
					[[['star',1],['allegiance',1]]]]

			# Mines
			self.locationCR[i][12] = [[[[facC,1]]],[[[facR,1]],[['artifact',1]]]]

		# Artifact markets
		for i in range(4):
			self.locationCR[i][11] = [[[['artifact',3]]],[[['star',1],['allegiance',1]]]]

		# Icarite Markets
		# Nimbus Loft
		anyThreeR = list(combinations_with_replacement([['gold',1],['stone',1],['brick',1]],3))
		self.locationCR[3][9] = [anyThreeR,[[['star',1],['allegiance',1]]]]
		# Breeze Bar
		anyComBliss = [[['bliss',1],['energy',1]],
			[['bliss',1],['water',1]],[['bliss',1],['food',1]]]
		self.locationCR[3][10] = [anyComBliss,[[['artifact',2]]]]
		# Sky Lounge
		anyTwoR = list(combinations_with_replacement([['gold',1],['stone',1],['brick',1]],2))
		self.locationCR[3][12] = [anyComBliss,anyTwoR]

		# Worker generation spaces
		self.locationCR[4][0] = [[[['energy',3]]],
			[[['worker',1],['knowledge',-2]]]]
		self.locationCR[4][0] = [[[['water',3]]],
			[[['worker',1],['morale',2]]]]



	def buildArtifactDeck(self):
		from random import shuffle

		self.artifact = []
		artType = ['bat','book','bear','balloon','glasses','game']
		for i in artType:
			for j in range(6):
				self.artifact.append(i)

		shuffle(self.artifact)

	def buildMarketDeck(self):
		from random import shuffle
		from itertools import combinations

		self.market = []
		# Particular Artifact + Commodity
		artType = ['bat','book','bear','balloon','glasses','game']
		for i in artType:
			anyComArt = [[[i,1],['energy',1]],
				[[i,1],['water',1]],[[i,1],['food',1]],
				[[i,1],['bliss',1]]]
			self.market.append(anyComArt)

		# 4 Commodity + Artifact
		comType = ['energy','water','food','bliss']
		for i in comType:
			anyArtCom = [[[i,4],['bat',1]],
				[[i,4],['book',1]],[[i,4],['bear',1]],
				[[i,4],['balloon',1]],[[i,4],['glasses',1]],
				[[i,4],['game',1]]]
			self.market.append(anyArtCom)


		# 4 Commodity + Resource
		resType = ['gold','stone','brick']
		comType.remove('bliss')
		for i in comType:
			for j in resType:
				self.market.append([[[i,4],[j,1]]])

		resCom = zip(comType,resType)
		for i in resCom:
			self.market.remove([[[i[0],4],[i[1],1]]])

		# Extraneous Markets
		anyResBliss = [[['bliss',4],['gold',1]],
				[['bliss',4],['stone',1]],[['bliss',4],['brick',1]]]
		self.market.append(anyResBliss)

		anyArtRes = list(combinations([['gold',1],['stone',1],['brick',1],
			['bat',1],['book',1],['bear',1],
			['balloon',1],['glasses',1],['game',1]],2))
		anyTwoRes = list(combinations([['gold',1],['stone',1],['brick',1]],2))
		for i in anyTwoRes:
			anyArtRes.remove(i)
		anyTwoArt = list(combinations([['bat',1],['book',1],['bear',1],
			['balloon',1],['glasses',1],['game',1]],2))
		for i in anyTwoArt:
			anyArtRes.remove(i)
		self.market.append(anyArtRes)

		shuffle(self.market)

		self.market = self.market[:6]

	def verifyMoraleKnowledgeRange(self):

		# Verify morale range
		if self.p[self.turn].resources['morale'] <= 0:
			self.p[self.turn].resources['morale'] = 1
		elif self.p[self.turn].resources['morale'] >= 7
			self.p[self.turn].resources['morale'] = 6

		# Verify knowledge range
		if self.p[self.turn].resources['knowledge'] <= 0:
			self.p[self.turn].resources['knowledge'] = 1
		elif self.p[self.turn].resources['knowledge'] >= 7
			self.p[self.turn].resources['knowledge'] = 6

	def adjustMineBonus(self):
		# use for move function to adjust mine space if allegiance high enough

	def checkRecruitFlip(self):
		# flip second recruit if mine or allegiance is far enough
		for i range(3):
			if self.factions[i]['allegiance'] >= 8 or self.factions[i]['mine'] >= 7:
				for j in range(self.pNum):
					if self.p[j].recruit[1] == i:
						self.p[j].resources['recruit2Active'=True]

	def checkRecruitStars(self):
		# put stars on recruits of given faction

		for i range(3):
			if self.factions[i]['allegiance'] >= 11:
				for j in range(self.pNum):
					for r in range(len(self.p[j].recruit))
						if self.p[j].recruit[r] == i and (not self.p[j].recruitStar[r]):
							self.p[j].resources['stars']-=1
							self.p[j].recruitStar[r] = True


	def isOver(self):
		# check if any player has placed all stars, if so declare winner (or tie)

		for i in self.p:
			if i.resources['stars'] <= 0:
				return True

	def existsWinner(self):
		# check if winner or a tie



	def winner(self):







	# def move(self,moveList):
	# 	# Turn move list into a move

	#def legalMoves(self):
	#	# Generate list of legal moves for the current player














		