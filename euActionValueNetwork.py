from pybrain.rl.learners.valuebased import ActionValueInterface

class euActionValueNetwork(Module, ActionValueInterface):
    """ A network that approximates action values for continuous state /
        discrete action RL environments. To receive the maximum action
        for a given state, a forward pass is executed for all discrete
        actions, and the maximal action is returned. This network is used
        for the NFQ algorithm. """

    def __init__(self, dimState, name=None):
        Module.__init__(self, dimState, 1, name)
        self.network = buildNetwork(dimState, dimState, 1)
        self.numActions = numActions

    def _forwardImplementation(self, inbuf, outbuf):
        """ takes the state vector and return the discrete action with
            the maximum value over all actions for this state.
        """
        outbuf[0] = self.getMaxAction(asarray(inbuf))

    def getMaxAction(self, state):
        """ Return the action with the maximal value for the given state. """
        return argmax(self.getActionValues(state))

    def getActionValues(self, state):
        """ Run forward activation for each of the actions and returns all values. """
        values = array([self.network.activate(r_[state, one_to_n(i, self.numActions)]) for i in range(self.numActions)])
        return values

    def getValue(self, state, action):
        return self.network.activate(r_[state, one_to_n(action, self.numActions)])