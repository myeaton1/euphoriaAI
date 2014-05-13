from player import *
from pybrain.rl.environments.twoplayergame import TwoPlayerGame

class Game(TwoPlayerGame):
	def __init__(self):
		from random import shuffle, randint

		self.pNum = 2

		self.reset()

	def reset(self):
		self.turn = 0

		self.over = False

		self.turnCounter = 0

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
			((self.p[self.turn].recruits[1] == faction['num']) and
				(self.p[self.turn].resources['recruit2Active']))):

			if faction['allegiance'] >= 2:
				return 1	
		
		return 0

		


	def useTemp(self,faction,locationN,workerVal,cost=None,reward=None):

		# deal with upgraded mines 
		if locationN == 13:
			lN = 12
		else:
			lN = locationN

		if len(self.location[faction['num']][lN]) == 1:			# if we need to bump, then:
			facPair = [faction['num'],lN]						# list of [ faction #, location key #]
			dieN = self.location[faction['num']][lN][0]			# list of number of die in that location
			pN = self.locationP[faction['num']][lN][0]			# list of player #s

			self.retrieve(facPair, dieN, pN)

		self.workerDrop(faction,lN,workerVal)					# add new worker die

		if cost:
			for i in range(len(cost)):
				self.p[self.turn].resources[cost[i][0]]-=cost[i][1]

		if reward:
			# Check maintenance heavy rewards
			#	(allegiance,stars,worker,artifact)
			for i in range(len(reward)):
				if reward[i][0] == 'allegiance':
					self.factions[faction['num']]['allegiance']+=1
				elif reward[i][0] == 'stars':
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

						self.checkMoraleCap()


				else:
					self.p[self.turn].resources[reward[i][0]]+=reward[i][1]

				# Make sure knowledge/morale not out of whack
				self.verifyMoraleKnowledgeRange()

	def checkMoraleCap(self):
		from random import choice
		# in case player has too many artifacts, discard down
		totArt = 0
		artType = ['bat','book','bear','balloon','glasses','game']
		for a in artType:
			totArt += self.p[self.turn].resources[a]
		while totArt > self.p[self.turn].resources['morale']:
			# if you have too many artifacts, you must discard one randomly
			self.p[self.turn].resources[choice(artType)]-=1
			totArt = 0
			for a in artType:
				totArt += self.p[self.turn].resources[a]


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

		self.location[facN][locN].remove(workerVal)
		self.locationP[facN][locN].remove(pN)

		self.p[pN].retrieveWorkers(1,cost)

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
			[[['worker',1],['knowledge',-2]],
			[['knowledge',-2]]]]
		self.locationCR[4][1] = [[[['water',3]]],
			[[['worker',1],['morale',2]],
			[['morale',2]]]]



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
		self.market.append(anyArtRes)

		shuffle(self.market)

		self.market = self.market[:6]

	def verifyMoraleKnowledgeRange(self):

		# Verify morale range
		if self.p[self.turn].resources['morale'] <= 0:
			self.p[self.turn].resources['morale'] = 1
		elif self.p[self.turn].resources['morale'] >= 7:
			self.p[self.turn].resources['morale'] = 6

		# Verify knowledge range
		if self.p[self.turn].resources['knowledge'] <= 0:
			self.p[self.turn].resources['knowledge'] = 1
		elif self.p[self.turn].resources['knowledge'] >= 7:
			self.p[self.turn].resources['knowledge'] = 6

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

	def winner(self):
		# declare winner, not generalized.  Only for pNum == 2
		if self.p[0].resources['stars'] < self.p[1].resources['stars']:
			return 0
		if self.p[0].resources['stars'] > self.p[1].resources['stars']:
			return 1

	def performAction(self,moveList):
		import shlex
		# Turn move list into a move
		moveList = list(moveList)

		factionNum	= moveList[1]
		locationNum	= moveList[2]
		costOp		= moveList[3]
		rewardOp	= moveList[4]
		costNum 	= 0
		rewardNum 	= 1
		workerNum	= moveList[5]

		if moveList[0] == 0:
			# place a worker
			if not locationNum == 0:
				cost = self.locationCR[factionNum][locationNum][costNum][costOp]
				reward = self.locationCR[factionNum][locationNum][rewardNum][rewardOp]

			if factionNum in [0,1,2,3]:
				# if normal (not worker gen) space
				if locationNum == 0:
					# use commodity market
					self.useMultiUse(self.factions[factionNum],workerNum)
				elif locationNum in [1,2,3,4,5,6,7,8]:
					# use exclusive spots (building markets)
					self.useExclusive(self.factions[factionNum],
						locationNum,workerNum,cost)
				else:
					# use another market
					self.useTemp(self.factions[factionNum],
						locationNum,workerNum,cost,reward)

					if locationNum == 12:
						self.factions[factionNum]['mine'] += 1
			
			elif factionNum == 4:
				# worker generation
				cost = self.locationCR[factionNum][locationNum][costNum][costOp]
				reward = self.locationCR[factionNum][locationNum][rewardNum][rewardOp]

				self.useTemp(self.factions[factionNum],
					locationNum,workerNum,cost,reward)

		elif moveList[0] == 1:
			# retrieve worker(s)
			if costOp == 0:
				cost = 'morale'
			elif costOp == 1:
				cost = 'food'
			elif costOp == 2:
				cost = 'bliss'

			fStr	= str(int(round(factionNum)))
			lStr	= str(locationNum)
			wStr	= str(int(round(workerNum)))

			lStr 	= list(shlex.shlex(lStr))

			factionNum	= []
			locationNum	= []
			workerNum	= []

			for i in range(len(fStr)):
				factionNum.append(int(fStr[i])-1)
				workerNum.append(int(wStr[i]))

			if int(lStr[2]) == 0:
				locationNum.append(int(lStr[0])-1)
			else:
				dig = []
				for i in range(len(lStr[2])):
					dig.append(int(lStr[2][i]))
				lStr = lStr[0]
				for i in dig:
					locationNum.append(int(lStr[:i])-1)
					lStr = lStr[i:]



			for i in range(len(factionNum)):
				if i == 0:
					self.retrieve([factionNum[i],locationNum[i]],
						workerNum[i],self.turn,cost)
				else:
					self.retrieve([factionNum[i],locationNum[i]],
						workerNum[i],self.turn)

		# Check end of the game
		if self.isOver():
			if self.existsWinner():
				self.winnerP = self.winner()
			self.over = True

		# Check worker flipping
		self.checkRecruitFlip()
		# Check worker stars
		self.checkRecruitStars()

		if self.turn == 0:
			self.turn = 1
		elif self.turn == 1:
			self.turn = 0

		self.turnCounter += 1




		# may implement moral dilemma later (moveList[0] == 2)

	def legalMoves(self):
		# Generate list of legal moves for the current player
		from itertools import chain, combinations

		workersOnBoard	= list(chain.from_iterable(list(chain.from_iterable(self.locationP))))
		costNum			= 0
		rewardNum 		= 1

		# May either place workers or retrieve workers
		moveList = []
		if self.p[self.turn].workers:
			# may place if you have some active workers
			for w in self.p[self.turn].workers:
				# for each worker you may do these moves
				for i in range(3):
					# can always use commodity markets
					multiUseMove = [0,i,0,0,0,w]
					moveList.append(multiUseMove)

					for j in [1,2,3,4]:
						# first market exclusive spaces
						cost = self.locationCR[i][j][costNum][0][0]
						market1 = self.factions[i]['market1']
						if self.p[self.turn].resources[cost[0]] >= cost[1] and not market1:
							tempMove = [0,i,j,0,0,w]
							moveList.append(tempMove)


					for j in [5,6,7,8]:
						# second market exclusive spaces
						cost = self.locationCR[i][j][costNum][0][0]
						market2 = self.factions[i]['market2']
						if self.p[self.turn].resources[cost[0]] >= cost[1] and not market2:
							tempMove = [0,i,j,0,0,w]
							moveList.append(tempMove)

					if self.factions[i]['starSlots'] > 0:
						# random market 1 (space 9)
						j = 9
						costList = self.locationCR[i][j][costNum]
						rewardList = self.locationCR[i][j][rewardNum]
						market1 = self.factions[i]['market1']
						if market1:
							for cNum in range(len(costList)):
								if self.checkCosts(costList[cNum]):
									for rNum in range(len(rewardList)):
										tempMove = [0,i,j,cNum,rNum,w]
										moveList.append(tempMove)

						# random market 2 (space 10)
						j = 10
						costList = self.locationCR[i][j][costNum]
						rewardList = self.locationCR[i][j][rewardNum]
						market2 = self.factions[i]['market2']
						if market2:
							for cNum in range(len(costList)):
								if self.checkCosts(costList[cNum]):
									for rNum in range(len(rewardList)):
										tempMove = [0,i,j,cNum,rNum,w]
										moveList.append(tempMove)

						# artifact market (space 11)
						j = 11
						costList = self.locationCR[i][j][costNum]
						rewardList = self.locationCR[i][j][rewardNum]
						for cNum in range(len(costList)):
							if self.checkCosts(costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum,w]
									moveList.append(tempMove)

					# regular mine
					j = 12
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					if not self.mineCheck(i):
						for cNum in range(len(costList)):
							if self.checkCosts(costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum,w]
									moveList.append(tempMove)

					# upgraded mine
					j = 13
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					if self.mineCheck(i):
						for cNum in range(len(costList)):
							if self.checkCosts(costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum,w]
									moveList.append(tempMove)


				# Icarite markets
				i = 3
				# can always use commodity markets
				multiUseMove = [0,i,0,0,0,w]
				moveList.append(multiUseMove)

				if self.factions[i]['starSlots'] > 0:
					# artifact market + 3 fixed markets
					for j in [9,11]:
						costList = self.locationCR[i][j][costNum]
						rewardList = self.locationCR[i][j][rewardNum]
						for cNum in range(len(costList)):
							if self.checkCosts(costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum,w]
									moveList.append(tempMove)

				# 2 fixed com. markets
					for j in [10,12]:
						costList = self.locationCR[i][j][costNum]
						rewardList = self.locationCR[i][j][rewardNum]
						for cNum in range(len(costList)):
							if self.checkCosts(costList[cNum]):
								for rNum in range(len(rewardList)):
									tempMove = [0,i,j,cNum,rNum,w]
									moveList.append(tempMove)

				# Worker generation
				i = 4
				for j in [0,1]:
					costList = self.locationCR[i][j][costNum]
					rewardList = self.locationCR[i][j][rewardNum]
					for cNum in range(len(costList)):
						if self.checkCosts(costList[cNum]):
							for rNum in range(len(rewardList)):
								if self.checkWorkers(rewardList[rNum]):
									tempMove = [0,i,j,cNum,rNum,w]
									moveList.append(tempMove)


		if self.turn in workersOnBoard:
			# may retrieve if you have some workers on the board
			# find spaces that have workers and add them to list
			fList	= []
			lList 	= []
			wList 	= []
			for i in range(4):
				for j in range(14):
					spacesP	= self.locationP[i][j]
					spaces 	= self.location[i][j]
					if self.turn in spacesP:
						for wN in range(len(spacesP)):
							if spacesP[wN] == self.turn:
								fList.append(str(i+1))
								lList.append(str(j+1))
								wList.append(str(spaces[wN]))

			i = 4
			for j in range(2):
				spacesP	= self.locationP[i][j]
				spaces 	= self.location[i][j]
				if self.turn in spacesP:
					for wN in range(len(spacesP)):
						if spacesP[wN] == self.turn:
							fList.append(str(i+1))
							lList.append(str(j+1))
							wList.append(str(spaces[wN]))

			for tList in [fList,lList,wList]:
				tListOrig = tList[:]
				for l in range(1,len(tList)+1):
					if l > 1:
						comb = list(combinations(tListOrig,l))
						for c in comb:
							combList = ''
							digList = ''
							for n in c:
								combList += n
								digList += str(len(n))

							tList.append(str(int(combList)+int(digList)/10.**len(digList) ))

				for n in range(len(tList)):
					tList[n] = float(tList[n])

			for i in range(len(fList)):
				# can always retrieve for morale loss
				retrieveMove = [1,fList[i],lList[i],0,0,wList[i]]
				moveList.append(retrieveMove)

				# check for food, bliss removal
				if self.p[self.turn].resources['food'] >= 1:
					retrieveMove = [1,fList[i],lList[i],1,0,wList[i]]
					moveList.append(retrieveMove)

				if self.p[self.turn].resources['bliss'] >= 1:
					retrieveMove = [1,fList[i],lList[i],2,0,wList[i]]
					moveList.append(retrieveMove)

		return moveList



	def mineCheck(self,factionNum):
		# check to see if you can use the upgraded mine
		mine = self.factions[factionNum]['mine']
		if self.p[self.turn].resources['recruit2Active']:
			activeRecruits = self.p[self.turn].recruits
		else:
			activeRecruits = [self.p[self.turn].recruits[0]]
		if (mine >= 5) and (factionNum in activeRecruits):
			return True
		return False

	def checkWorkers(self,reward):
		# check to see if getting another worker would bump you over
		workers = len(self.p[self.turn].workers)
		maxWorkers = 4
		for r in reward:
			if r[0] == 'worker':
				workers += 1
		if workers > maxWorkers:
			return False
		return True

	def checkCosts(self,cost):
		# check if all costs can be paid
		checker = []
		resources = dict(energy=0,water=0,food=0,bliss=0,
			gold=0,stone=0,brick=0,bat=0,book=0,bear=0,
			balloon=0,glasses=0,game=0)
		for c in cost:
			resources[c[0]]+=c[1]
		for c in cost:
			if self.p[self.turn].resources[c[0]] >= resources[c[0]]:
				checker.append(True)
			else:
				checker.append(False)

		return all(checker)


	# def adjustMineBonus(self):
	# # use for move function to adjust mine space if allegiance high enough
	# 	adjust locationCR temporarily to account for bonus














		