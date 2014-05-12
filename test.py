from game import *

g = Game()

# n = g.p[0].workers[0]

# g.useMultiUse(g.factions[move[0]],g.p[g.turn].workers[move[2]])

move = [0,1,0]
g.useExclusive(g.factions[move[0]],move[1],g.p[g.turn].workers[move[2]],[['gold',1]])

move = [0,2,0]
g.useExclusive(g.factions[move[0]],move[1],g.p[g.turn].workers[move[2]],[['stone',1]])

# print g.locationCR
