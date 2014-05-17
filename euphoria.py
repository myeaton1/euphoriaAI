from player import *
from pybrain.rl.environments.twoplayergames.twoplayergame import TwoPlayerGame

# # First import the embed function
# from IPython.terminal.embed import InteractiveShellEmbed

# # Now create the IPython shell instance. 
# ipshell = InteractiveShellEmbed()

# DEBUG = True

# # Wrap it in a function that gives me more context:
# def ipsh():
#     # frameinfo = getframeinfo(currentframe())
#     # msg = 'Stopped at: ' + frameinfo.filename + ' ' +  str(frameinfo.lineno)
#     if DEBUG == True:
#         frame = inspect.currentframe().f_back
#         msg = 'Stopped at {0.f_code.co_filename} at line {0.f_lineno}'.format(frame)

#         # Go back one level! 
#         # This is needed because the call to ipshell is inside the function ipsh()
#         ipshell(msg,stack_depth=2)

class EuphoriaGame(TwoPlayerGame):

	BLACK = 0
	WHITE = 1

	def __init__(self):

		self.pNum = 2

		self.reset()

	def reset(self):
		from random import shuffle, randint

		self.over = False

		self.turnCounter = 0

		self.winner = None

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
		self.factions.append(dict(num=4))

		# Initialize Locations, randomize markets
		self.initLoc()

		# Build, shuffle artifact deck
		self.buildArtifactDeck()


	def useMultiUse(self,player,faction,workerVal):

		self.workerDrop(player,faction,0,workerVal)							# add new worker die

		if sum(self.location[faction['num']][0]) <= 4:
			# 1 commodity + allegiance track +1
			self.p[player].resources[faction['com']] += (1 + self.comAllegianceBonus(player,faction))

			self.factions[faction['num']]['allegiance']+=1

		if (sum(self.location[faction['num']][0]) >= 5 and sum(self.location[faction['num']][0]) <= 8):
			#
			self.p[player].resources[faction['com']] += (1 + self.comAllegianceBonus(player,faction))

			self.p[player].resources['knowledge']-=1
			if self.p[player].resources['knowledge']<=0:
				self.p[player].resources['knowledge'] = 1

		if sum(self.location[faction['num']][0]) >= 9:
			self.p[player].resources[faction['com']] += (2 + self.comAllegianceBonus(player,faction))

			self.p[player].resources['knowledge']+=1
			if self.p[player].resources['knowledge']>=7:
				self.p[player].resources['knowledge'] = 6

	def comAllegianceBonus(self,player,faction):
		if ((self.p[player].recruits[0] == faction['num']) or
			((self.p[player].recruits[1] == faction['num']) and
				(self.p[player].resources['recruit2Active']))):

			if faction['allegiance'] >= 2:
				return 1	
		
		return 0

		


	def useTemp(self,player,faction,locationN,workerVal,cost=None,reward=None):

		# deal with upgraded mines 
		if locationN == 13:
			lN = 12
		else:
			lN = locationN

		self.workerDrop(player,faction,lN,workerVal)					# add new worker die

		if len(self.location[faction['num']][lN]) == 1:			# if we need to bump, then:
			facPair = [faction['num'],lN]						# list of [ faction #, location key #]
			dieN = self.location[faction['num']][lN][0]			# list of number of die in that location
			pN = self.locationP[faction['num']][lN][0]			# list of player #s

			self.retrieve(facPair, dieN, pN)

		if cost:
			for i in range(len(cost)):
				if not locationN == 11:
					self.p[player].resources[cost[i][0]]-=cost[i][1]

			if locationN == 11:
				# shrink action space by dealing with art. markets in a basic way
				artType = ['bat','book','bear','balloon','glasses','game']
				artNum = []
				for a in artType:
					artNum.append(self.p[player].resources[a])
				maxArt = artType[artNum.index(max(artNum))]
				if max(artNum) >= 2:
					self.p[player].resources[maxArt]-=2

				if max(artNum) < 2:
					count = 0
					for a in artType:
						if self.p[player].resources[a] > 0:
							self.p[player].resources[a]-=1
							count+=1
						if count == 3:
							break


		if reward:
			# Check maintenance heavy rewards
			#	(allegiance,stars,worker,artifact)
			for i in range(len(reward)):
				if reward[i][0] == 'allegiance':
					self.factions[faction['num']]['allegiance']+=1
				elif reward[i][0] == 'stars':
					self.factions[faction['num']]['starSlots']-=1
					self.p[player].resources[reward[i][0]]-=reward[i][1]
				elif reward[i][0] == 'worker':
					if len(self.p[player].workers)<=4:
						self.p[player].retrieveWorkers(1)
						self.p[player].totalWorkers+=1
				elif reward[i][0] == 'artifact':
					for j in range(reward[i][1]):
						if not self.artifact:
							self.buildArtifactDeck()
						dealArt = self.artifact.pop()

						self.p[player].resources[dealArt]+=1

						self.checkMoraleCap(player)


				else:
					self.p[player].resources[reward[i][0]]+=reward[i][1]

				# Make sure knowledge/morale not out of whack
				self.verifyMoraleKnowledgeRange(player)

	def checkMoraleCap(self,player):
		from random import choice
		# in case player has too many artifacts, discard down
		totArt = 0
		artType = ['bat','book','bear','balloon','glasses','game']
		for a in artType:
			totArt += self.p[player].resources[a]
		while totArt > self.p[player].resources['morale']:
			# if you have too many artifacts, you must discard one randomly
			self.p[player].resources[choice(artType)]-=1
			totArt = 0
			for a in artType:
				totArt += self.p[player].resources[a]


	def useExclusive(self,player,faction,locationN,workerVal,cost=None):

		self.workerDrop(player,faction,locationN,workerVal)					# add new worker die

		if cost:
			for i in range(len(cost)):
				self.p[player].resources[cost[i][0]]-=cost[i][1]

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

					self.retrieve(facPair, dieN, pN)

					checkHelped[pN] = True

			for i in range(len(checkHelped)):
				if checkHelped[i]:
					self.p[i].resources['stars']-=1

					self.locationStars[faction['num']][marketLoc].append(i)	# record that player i has put a star here

			# Turn on market space
			self.factions[faction['num']][marketN] = True

	def retrieve(self,locations,workerVal,pN,cost=None):
		# retrieve a worker from a space

		facN = locations[0]

		locN = locations[1]

		# print '\n locationP: ', self.locationP, '\n'

		self.location[facN][locN].remove(workerVal)
		self.locationP[facN][locN].remove(pN)

		self.p[pN].retrieveWorkers(1,cost)

	def workerDrop(self,player,faction,locationN,workerVal):

		self.location[faction['num']][locationN].append(workerVal)

		self.locationP[faction['num']][locationN].append(player)

		# print player, workerVal, faction['num'], locationN

		# print self.p[player].workers, self.p[(player + 1)%2].workers ,'\n', self.p[0].workers, self.p[1].workers
		self.p[player].workers.remove(workerVal)

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
					[[['stars',1],['allegiance',1]]]]

			# Mines
			self.locationCR[i][12] = [[[[facC,1]]],[[[facR,1]],[['artifact',1]]]]

			# Upgraded Mines
			self.locationCR[i][13] = [[[[facC,1]]],[[[facR,1],['artifact',1]]]]

		# Artifact markets
		for i in range(4):
			artType = ['bat','book','bear','balloon','glasses','game']
			anyThreeArt = list(combinations_with_replacement([['bat',1],['book',1],['bear',1],
				['balloon',1],['glasses',1],['game',1]],3))
			for a in artType:
				anyThreeArt.append([[a,2]])
			self.locationCR[i][11] = [anyThreeArt,[[['stars',1],['allegiance',1]]]]

		# Icarite Markets
		# Nimbus Loft
		anyThreeR = list(combinations_with_replacement([['gold',1],['stone',1],['brick',1]],3))
		self.locationCR[3][9] = [anyThreeR,[[['stars',1],['allegiance',1]]]]
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
		self.locationCR[4][1] = [[[['water',3]]],
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
		from itertools import combinations_with_replacement

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

		anyArtRes = list(combinations_with_replacement([['gold',1],['stone',1],['brick',1],
			['bat',1],['book',1],['bear',1],
			['balloon',1],['glasses',1],['game',1]],2))
		anyTwoRes = list(combinations_with_replacement([['gold',1],['stone',1],['brick',1]],2))
		for i in anyTwoRes:
			anyArtRes.remove(i)
		anyTwoArt = list(combinations_with_replacement([['bat',1],['book',1],['bear',1],
			['balloon',1],['glasses',1],['game',1]],2))
		for i in anyTwoArt:
			anyArtRes.remove(i)
		# self.market.append(anyArtRes)
		# ^^ this market has too many options embedded in it for right now

		shuffle(self.market)

		self.market = self.market[:6]

	def verifyMoraleKnowledgeRange(self,player):

		# Verify morale range
		if self.p[player].resources['morale'] <= 0:
			self.p[player].resources['morale'] = 1
		elif self.p[player].resources['morale'] >= 7:
			self.p[player].resources['morale'] = 6

		# Verify knowledge range
		if self.p[player].resources['knowledge'] <= 0:
			self.p[player].resources['knowledge'] = 1
		elif self.p[player].resources['knowledge'] >= 7:
			self.p[player].resources['knowledge'] = 6

	def checkRecruitFlip(self):
		# flip second recruit if mine or allegiance is far enough
		for i in range(3):
			if self.factions[i]['allegiance'] >= 8 or self.factions[i]['mine'] >= 7:
				for j in range(self.pNum):
					if self.p[j].recruits[1] == i:
						self.p[j].resources['recruit2Active']=True

	def checkRecruitStars(self):
		# put stars on recruits of given faction

		for i in range(3):
			if self.factions[i]['allegiance'] >= 11:
				for j in range(self.pNum):
					for r in range(len(self.p[j].recruits)):
						if self.p[j].recruits[r] == i and (not self.p[j].recruitStar[r]):
							self.p[j].resources['stars']-=1
							self.p[j].recruitStar[r] = True


	def isOver(self):
		# check if any player has placed all stars, if so declare winner (or tie)

		for i in self.p:
			if i.resources['stars'] <= 0:
				return True
		return False

	def existsWinner(self):
		# check if winner or a tie
		for i in self.p:
			if i.resources['stars'] > 0:
				return True
		return False

	def isWinner(self):
		# declare winner, not generalized.  Only for pNum == 2
		if self.p[0].resources['stars'] < self.p[1].resources['stars']:
			return 0
		if self.p[0].resources['stars'] > self.p[1].resources['stars']:
			return 1

	def doMove(self,player,action):
		import shlex
		# Turn action number into move list
		moveList = self.actionInterpreter(action)
		print player, self.p[player].workers, action, moveList

		# moveList = self.actionInterpreter(moveList)
		# ipsh()


		factionNum	= moveList[1]
		locationNum	= moveList[2]
		costOp		= moveList[3]
		rewardOp	= moveList[4]
		costNum 	= 0
		rewardNum 	= 1
		# workerNum	= moveList[5]

		if moveList[0] == 0:

			workerNum 	= min(self.p[player].workers)

			# place a worker
			if not locationNum == 0:
				cost = self.locationCR[factionNum][locationNum][costNum][costOp]
				reward = self.locationCR[factionNum][locationNum][rewardNum][rewardOp]

			if factionNum in [0,1,2,3]:
				# if normal (not worker gen) space
				if locationNum == 0:
					# use commodity market
					self.useMultiUse(player,self.factions[factionNum],workerNum)
				elif locationNum in [1,2,3,4,5,6,7,8]:
					# use exclusive spots (building markets)
					self.useExclusive(player,self.factions[factionNum],
						locationNum,workerNum,cost)
				else:
					# use another market
					self.useTemp(player,self.factions[factionNum],
						locationNum,workerNum,cost,reward)

					if locationNum == 12:
						self.factions[factionNum]['mine'] += 1
			
			elif factionNum == 4:
				# worker generation
				cost = self.locationCR[factionNum][locationNum][costNum][costOp]
				reward = self.locationCR[factionNum][locationNum][rewardNum][rewardOp]

				self.useTemp(player,self.factions[factionNum],
					locationNum,workerNum,cost,reward)

		elif moveList[0] == 1:
			# retrieve worker(s)
			# simplifying for now to shrink the action space

			if costOp == 0:
				cost = 'morale'
			elif costOp == 1:
				cost = 'food'
			elif costOp == 2:
				cost = 'bliss'

			# Alternate retrieve: when you retrieve, you must retrieve all workers
			# Find workers, then retrieve them

			paid = False
			for i in range(4):
				for j in range(14):
					spacesP	= self.locationP[i][j]
					spaces 	= self.location[i][j]
					if player in spacesP:
						for wN in reversed(range(len(spacesP))):
							if spacesP[wN] == player:
								if not paid:
									self.retrieve([i,j],spaces[wN],player,cost)
									paid = True
								else:
									self.retrieve([i,j],spaces[wN],player)

								

			i = 4
			for j in range(2):
				spacesP	= self.locationP[i][j]
				spaces 	= self.location[i][j]
				if player in spacesP:
					for wN in reversed(range(len(spacesP))):
						if spacesP[wN] == player:
							if not paid:
								self.retrieve([i,j],spaces[wN],player,cost)
								paid = True
							else:
								self.retrieve([i,j],spaces[wN],player)

			###################################################
			

			# fStr	= str(int(round(factionNum)))
			# lStr	= str(locationNum)
			# wStr	= str(int(round(workerNum)))

			# lStr 	= list(shlex.shlex(lStr))

			# factionNum	= []
			# locationNum	= []
			# workerNum	= []

			# for i in range(len(fStr)):
			# 	factionNum.append(int(fStr[i])-1)
			# 	workerNum.append(int(wStr[i]))

			# if int(lStr[2]) == 0:
			# 	locationNum.append(int(lStr[0])-1)
			# else:
			# 	dig = []
			# 	for i in range(len(lStr[2])):
			# 		dig.append(int(lStr[2][i]))
			# 	lStr = lStr[0]
			# 	for i in dig:
			# 		locationNum.append(int(lStr[:i])-1)
			# 		lStr = lStr[i:]



			# for i in range(len(factionNum)):
			# 	if i == 0:
			# 		self.retrieve([factionNum[i],locationNum[i]],
			# 			workerNum[i],player,cost)
			# 	else:
			# 		self.retrieve([factionNum[i],locationNum[i]],
			# 			workerNum[i],player)

		# Check worker flipping
		self.checkRecruitFlip()
		# Check worker stars
		self.checkRecruitStars()

		# Check end of the game
		if self.isOver():
			if self.existsWinner():
				self.winner = self.isWinner()
			else:
				self.winner = self.DRAW
			self.over = True

		self.turnCounter += 1

		# may implement moral dilemma later (moveList[0] == 2)

	def actionInterpreter(self,action,genList = False):
		# Converts between move label types

		# Find all moves
		acList 	= []
		placeNum	= 0
		retrieveNum	= 1

		# Placing
		for i in range(3):
			# regular factions
			for j in range(1,9):
				# exclusive spaces
				acList.append([placeNum,i,j,0,0])
			for j in [12]:
				# regular mines
				for r in range(2):
					acList.append([placeNum,i,j,0,r])
			for j in [13]:
				# advanced mines
				acList.append([placeNum,i,j,0,0])
			for j in [9,10]:
				# random markets (max options 6)
				for c in range(6):
					acList.append([placeNum,i,j,c,0])
		for i in range(4):
			# all factions
			for j in [0,11]:
				# commodity markets, artifact markets
				acList.append([placeNum,i,j,0,0])
		for i in [3]:
			# Icarite only markets
			for j in [9]:
				# Icarite res --> star market
				for c in range(10):
					acList.append([placeNum,i,j,c,0])
			for j in [10]:
				# Icarite com/bliss --> art market
				for c in range(3):
					acList.append([placeNum,i,j,c,0])
			for j in [12]:
				# Icarite com/blis --> res market
				for c in range(3):
					for r in range(6):
						acList.append([placeNum,i,j,c,r])

		for i in [4]:
			# worker generation
			for j in range(2):
				acList.append([placeNum,i,j,0,0])

		# Retrieving
		for c in range(3):
			acList.append([retrieveNum,0,0,c,0])

		if genList:
			return acList
		else:
			if len(action) == 1:
				return acList[int(action[0])]
			elif type(action) == list:
				return acList.index(action)

		




	def getSensors(self):
		# output from the most recent move
		from numpy import array, hstack
		from scipy import zeros
		from itertools import chain

		obs = zeros(469)
		oN = 2

		# for now should only be learning agent using this function
		player = 0
		if player == 0:
			obs[0] = 1
			obs[1] = 0
		if player == 1:
			obs[0] = 0
			obs[1] = 1

		pList = [0,1]

		# Players
		for pN in pList:
			# Normal faction spaces
			for i in range(3):
				for j in range(14):
					spacesP	= self.locationP[i][j]
					if pN in spacesP:
						obs[oN] = 1
					oN+=1

			# Icarite faction spaces
			i = 3
			for j in [0,9,10,11,12]:
				spacesP	= self.locationP[i][j]
				if pN in spacesP:
					obs[oN] = 1
				oN+=1

			# Worker gen. spaces
			i = 4
			for j in [0,1]:
				spacesP	= self.locationP[i][j]
				if pN in spacesP:
					obs[oN] = 1
				oN+=1

			# total workers, active workers
			for j in range(1,5):
				if len(self.p[pN].workers) >= j:
					obs[oN] = 1
				oN+=1

				if self.p[pN].nActiveWorkers >= j:
					obs[oN] = 1
				oN+=1


			# total resources per category
			resList = ['energy','water','food','bliss','gold','stone','brick']
			for r in resList:
				for j in range(1,5):
					if self.p[pN].resources[r] >= j:
						obs[oN] = 1
					oN+=1

				if self.p[pN].resources[r] >= j:
					obs[oN] = (self.p[pN].resources[r] - j)/2

				oN+=1

			# total morale/knowledge
			resList = ['morale','knowledge']
			for r in resList:
				for j in range(1,7):
					if self.p[pN].resources[r] >= j:
						obs[oN] = 1
					oN+=1

			# total stars left
			resList = ['stars']
			for r in resList:
				for j in range(1,9):
					if self.p[pN].resources[r] < j:
						obs[oN] = 1
					oN+=1

		# World
		for i in range(4):

			# allegiance tracks
			for j in range(1,12):
				if self.factions[i]['allegiance'] >= j:
					obs[oN] = 1
				oN+=1

			# commodity bonuses, mine bonuses
			for j in [2,5]:
				if self.factions[i]['allegiance'] >= j:
					obs[oN] = 1
				oN+=1

			# # of stars left per faciton
			for j in [1,2]:
				if self.factions[i]['starSlots'] < j:
					obs[oN] = 1
				oN+=1

			# Resource used as a random market cost (Icarites have no random markets)
			if i < 3:
				# mine level
				for j in range(1,8):
					if self.factions[i]['mine'] >= j:
						obs[oN] = 1
					oN+=1

				# if markets built
				if self.factions[i]['market1']:
					obs[oN] = 1
				oN+=1

				if self.factions[i]['market2']:
					obs[oN] = 1
				oN+=1

				resList = (['energy','water','food','bliss','gold','stone','brick',
					'bat','book','bear','balloon','glasses','game'])
				costNum = 0
				for j in [9,10]:
					for r in resList:
						marketThings = list(chain.from_iterable(list(chain.from_iterable(
							self.locationCR[i][j][costNum]))))
						if r in marketThings:
							obs[oN] = 1
						oN += 1

		# Hidden player elements (will be filtered by the task)
		for pN in pList:

			# artifacts per type, total artifacts
			totArt = 0
			artList = ['bat','book','bear','balloon','glasses','game']
			for r in artList:
				for j in range(1,4):
					if self.p[pN].resources[r] >= j:
						obs[oN] = 1
					oN+=1

				totArt += self.p[pN].resources[r]

				if self.p[pN].resources[r] >= j:
					obs[oN] = (self.p[pN].resources[r] - j)/2
				oN+=1

			for j in range(1,7):
				if totArt >= j:
					obs[oN] = 1
				oN+=1

			# recruits
			for r in range(2):
				for j in range(4):
					if self.p[pN].recruits[r] == j:
						obs[oN] = 1
					oN+=1

			# recruits active
			if self.p[pN].resources['recruit2Active']:
				obs[oN] = 1
			oN+=1

		# print oN

		acLegal 	= []
		acList 		= self.actionInterpreter(0,True)
		acLegal 	= self.legalMoves(player)

		# print '\n legal actions: ',acLegal,'\n'

		acLegalCheck = []
		for a in acList:
			if a in acLegal:
				acLegalCheck.append(1)
			else:
				acLegalCheck.append(0)
		acLegalCheck = array(acLegalCheck)
		
		obsAc = hstack((obs,acLegalCheck))

		return obsAc
		

	def legalMoves(self,player):
		# Generate list of legal moves for the current player
		from itertools import chain, combinations

		workersOnBoard	= list(chain.from_iterable(list(chain.from_iterable(self.locationP))))
		# print workersOnBoard
		costNum			= 0
		rewardNum 		= 1

		# May either place workers or retrieve workers
		moveList = []
		if self.p[player].workers:
			# may place if you have some active workers
			# for w in self.p[player].workers:
				
			# for each worker you may do these moves
			for i in range(3):
				# can always use commodity markets
				multiUseMove = [0,i,0,0,0]
				moveList.append(multiUseMove)

				for j in [1,2,3,4]:
					# first market exclusive spaces
					cost = self.locationCR[i][j][costNum][0][0]
					market1 = self.factions[i]['market1']
					if self.p[player].resources[cost[0]] >= cost[1] and not market1:
						tempMove = [0,i,j,0,0]
						moveList.append(tempMove)


				for j in [5,6,7,8]:
					# second market exclusive spaces
					cost = self.locationCR[i][j][costNum][0][0]
					market2 = self.factions[i]['market2']
					if self.p[player].resources[cost[0]] >= cost[1] and not market2:
						tempMove = [0,i,j,0,0]
						moveList.append(tempMove)

				if self.factions[i]['starSlots'] > 0:
					# random market 1 (space 9)
					j = 9
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					market1 = self.factions[i]['market1']
					if market1:
						for cNum in range(len(costList)):
							if self.checkCosts(player,costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum]
									moveList.append(tempMove)

					# random market 2 (space 10)
					j = 10
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					market2 = self.factions[i]['market2']
					if market2:
						for cNum in range(len(costList)):
							if self.checkCosts(player,costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum]
									moveList.append(tempMove)

					# artifact market (space 11)
					j = 11
					artCheck = []
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					for cNum in range(len(costList)):
						if self.checkCosts(player,costList[cNum]):
							# for rNum in range(len(rewardList)):
							artCheck.append(True)
						else:
							artCheck.append(False)

					if any(artCheck):
						tempMove = [0,i,j,0,0]
						moveList.append(tempMove)

				# regular mine
				j = 12
				costList = self.locationCR[i][j][costNum]
				rewardList = self.locationCR[i][j][rewardNum]
				if not self.mineCheck(player,i):
					for cNum in range(len(costList)):
						if self.checkCosts(player,costList[cNum]):
							for rNum in range(len(rewardList)):
								tempMove = [0,i,j,cNum,rNum]
								moveList.append(tempMove)

				# upgraded mine
				j = 13
				costList = self.locationCR[i][j][costNum]
				rewardList = self.locationCR[i][j][rewardNum]
				if self.mineCheck(player,i):
					for cNum in range(len(costList)):
						if self.checkCosts(player,costList[cNum]):
							for rNum in range(len(rewardList)):
								tempMove = [0,i,j,cNum,rNum]
								moveList.append(tempMove)


			# Icarite markets
			i = 3
			# can always use commodity markets
			multiUseMove = [0,i,0,0,0]
			moveList.append(multiUseMove)

			if self.factions[i]['starSlots'] > 0:
				# artifact market + 3 fixed markets
				for j in [9]:
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					for cNum in range(len(costList)):
						if self.checkCosts(player,costList[cNum]):
							for rNum in range(len(rewardList)):
								tempMove = [0,i,j,cNum,rNum]
								moveList.append(tempMove)

				j = 11
				artCheck = []
				costList = self.locationCR[i][j][costNum]
				rewardList = self.locationCR[i][j][rewardNum]
				for cNum in range(len(costList)):
					if self.checkCosts(player,costList[cNum]):
						# for rNum in range(len(rewardList)):
						artCheck.append(True)
					else:
						artCheck.append(False)

				if any(artCheck):
					tempMove = [0,i,j,0,0]
					moveList.append(tempMove)


				# 2 fixed com. markets
				for j in [10,12]:
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					for cNum in range(len(costList)):
						if self.checkCosts(player,costList[cNum]):
							for rNum in range(len(rewardList)):
								tempMove = [0,i,j,cNum,rNum]
								moveList.append(tempMove)

			# Worker generation
			i = 4
			for j in [0,1]:
				costList = self.locationCR[i][j][costNum]
				rewardList = self.locationCR[i][j][rewardNum]
				for cNum in range(len(costList)):
					if self.checkCosts(player,costList[cNum]):
						for rNum in range(len(rewardList)):
							if self.checkWorkers(player,rewardList[rNum]):
								tempMove = [0,i,j,cNum,rNum]
								moveList.append(tempMove)


		if player in workersOnBoard:
			# may retrieve if you have some workers on the board
			# find spaces that have workers and add them to list
			# fList	= []
			# lList 	= []
			# wList 	= []
			# for i in range(4):
			# 	for j in range(14):
			# 		spacesP	= self.locationP[i][j]
			# 		spaces 	= self.location[i][j]
			# 		if player in spacesP:
			# 			for wN in range(len(spacesP)):
			# 				if spacesP[wN] == player:
			# 					fList.append(str(i+1))
			# 					lList.append(str(j+1))
			# 					wList.append(str(spaces[wN]))

			# i = 4
			# for j in range(2):
			# 	spacesP	= self.locationP[i][j]
			# 	spaces 	= self.location[i][j]
			# 	if player in spacesP:
			# 		for wN in range(len(spacesP)):
			# 			if spacesP[wN] == player:
			# 				fList.append(str(i+1))
			# 				lList.append(str(j+1))
			# 				wList.append(str(spaces[wN]))

			# for tList in [fList,lList,wList]:
			# 	tListOrig = tList[:]
			# 	for l in range(1,len(tList)+1):
			# 		if l > 1:
			# 			comb = list(combinations(tListOrig,l))
			# 			for c in comb:
			# 				combList = ''
			# 				digList = ''
			# 				for n in c:
			# 					combList += n
			# 					digList += str(len(n))

			# 				tList.append(str(int(combList)+int(digList)/10.**len(digList) ))

			# 	for n in range(len(tList)):
			# 		tList[n] = float(tList[n])

			# for i in range(len(fList)):
			# 	# can always retrieve for morale loss
			# 	retrieveMove = [1,fList[i],lList[i],0,0,wList[i]]
			# 	moveList.append(retrieveMove)

			# 	# check for food, bliss removal
			# 	if self.p[player].resources['food'] >= 1:
			# 		retrieveMove = [1,fList[i],lList[i],1,0,wList[i]]
			# 		moveList.append(retrieveMove)

			# 	if self.p[player].resources['bliss'] >= 1:
			# 		retrieveMove = [1,fList[i],lList[i],2,0,wList[i]]
			# 		moveList.append(retrieveMove)

			# can always retrieve for morale loss
			retrieveMove = [1,0,0,0,0]
			moveList.append(retrieveMove)

			# check for food, bliss removal
			if self.p[player].resources['food'] >= 1:
				retrieveMove = [1,0,0,1,0]
				moveList.append(retrieveMove)

			if self.p[player].resources['bliss'] >= 1:
				retrieveMove = [1,0,0,2,0]
				moveList.append(retrieveMove)

		return moveList



	def mineCheck(self,player,factionNum):
		# check to see if you can use the upgraded mine
		mine = self.factions[factionNum]['mine']
		if self.p[player].resources['recruit2Active']:
			activeRecruits = self.p[player].recruits
		else:
			activeRecruits = [self.p[player].recruits[0]]
		if (mine >= 5) and (factionNum in activeRecruits):
			return True
		return False

	def checkWorkers(self,player,reward):
		# check to see if getting another worker would bump you over
		workers = len(self.p[player].workers)
		maxWorkers = 4
		for r in reward:
			if r[0] == 'worker':
				workers += 1
		if workers > maxWorkers:
			return False
		return True

	def checkCosts(self,player,cost):
		# check if all costs can be paid
		checker = []
		resources = dict(energy=0,water=0,food=0,bliss=0,
			gold=0,stone=0,brick=0,bat=0,book=0,bear=0,
			balloon=0,glasses=0,game=0)
		for c in cost:
			resources[c[0]]+=c[1]
		for c in cost:
			if self.p[player].resources[c[0]] >= resources[c[0]]:
				checker.append(True)
			else:
				checker.append(False)

		return all(checker)


	# def adjustMineBonus(self):
	# # use for move function to adjust mine space if allegiance high enough
	# 	adjust locationCR temporarily to account for bonus














		