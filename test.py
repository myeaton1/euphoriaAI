from game import *
import random

g = Game()

over = False
while not over:

	m = random.choice(g.legalMoves())
	# print 'm = ', m, 'turn = ', g.turn
	g.move(m)

	over = g.over

print g.winner(), g.turnCounter

# g.move([0,4,0,0,0,g.p[0].workers[0]])

# g.move([0,0,0,0,0,g.p[0].workers[0]])

# g.move([0,1,0,0,0,g.p[0].workers[0]])

# g.legalMoves()
