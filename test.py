from game import *
import random

win = []
for i in range(1):
	g = Game()

	over = False
	while not over:

		m = random.choice(g.legalMoves())
		# print 'm = ', m, ' turn = ', g.turn, ' turn # = ', g.turnCounter
		g.performAction(m)

		over = g.over

	if g.winner() in [0,1]:
		win.append(g.winner())
		print i

print sum(win)/float(len(win))


# g.move([0,4,0,0,0,g.p[0].workers[0]])

# g.move([0,0,0,0,0,g.p[0].workers[0]])

# g.move([0,1,0,0,0,g.p[0].workers[0]])

# g.legalMoves()
