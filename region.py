import spaces
from numpy import *

class Region:

	def __init__(self, isMine=1, isRandMkt=2, isFixedMkt=0, players=2):

		self.isMine = isMine
		self.isRandMkt = isRandMkt
		self.isFixedMkt = isFixedMkt
		self.starSpots = players

		self.temp = 0
		self.multi = 0
		self.oneTime = 0

		self.comMkt = spaces.multiSpace(self)

		if isMine:
			self.mine = spaces.mine(self)

		for i in arange(isRandMkt):
			self.









