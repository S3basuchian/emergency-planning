# qlearningAgents.py
# ------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC
# Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
import time

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *

import random, util, math
import pickle

from clingoHelper import ClingoHelper


class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent

      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """

    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)

        "*** YOUR CODE HERE ***"
        self.qvalues = util.Counter()

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()
        return self.qvalues[state, action]

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()
        try:
            return max([self.getQValue(state, action)
                        for action in self.getLegalActions(state)])
        except  ValueError:
            return 0.0

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()
        actionValuePairs = [(action, self.getQValue(state, action))
                            for action in self.getLegalActions(state)]
        if actionValuePairs == []:
            return None
        maxValue = max(actionValuePairs, key=lambda x: x[1])[1]

        # Filter into list with same max value.
        bestActions = list(
            filter(lambda x: x[1] == maxValue, actionValuePairs))

        return random.choice(bestActions)[0]

    def getBestActions(self, state):
        actionValuePairs = [(action, self.getQValue(state, action))
                            for action in self.getLegalActions(state)]

        if actionValuePairs == []:
            return None
        maxValue = max(actionValuePairs, key=lambda x: x[1])[1]

        # Filter into list with same max value.
        bestActions = list(
            filter(lambda x: x[1] == maxValue, actionValuePairs))
        return [t[0] for t in bestActions]

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        # Pick Action
        "*** YOUR CODE HERE ***"
        legalActions = self.getLegalActions(state)
        if util.flipCoin(self.epsilon):
            return random.choice(legalActions)

        return self.computeActionFromQValues(state)

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        futureValue = self.discount * self.getValue(nextState)
        currentValue = self.getQValue(state, action)
        predictedReward = futureValue - currentValue
        self.qvalues[state, action] += self.alpha * (reward + predictedReward)

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, epsilon=0.05, gamma=0.8, alpha=0.2, numTraining=0,
                 mode=0, name=None, **args):
        """
        These default parameters can be changed from the pacman.py command
        line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after
        these many episodes
        """
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        args['mode'] = mode
        args['name'] = name
        self.clingo = None
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        time_pre_compute = round(time.time() * 1000)
        if self.clingo is not None:
            actionValuePairs = [(action, self.getQValue(state, action))
                                for action in self.getLegalActions(state)]
            action = self.clingo.get_action(state, actionValuePairs)

            actionsQ = QLearningAgent.getBestActions(self, state)
            if action not in actionsQ:
                state.data.interventions += 1

            self.doAction(state, action)
        else:
            action = QLearningAgent.getAction(self, state)

        self.doAction(state, action)

        time_post_compute = round(time.time() * 1000)
        time_diff = time_post_compute - time_pre_compute
        state.data.times.append(time_diff)
        return action


class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """

    def __init__(self, weights, numGhosts, horizon, radius, extractor='IdentityExtractor', **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()
        if weights is not None:
            self.weights = weights
            self.epsilon = 0.0  # no exploration
            self.alpha = 0.0
            if self.mode == 2:
                self.clingo = ClingoHelper(horizon=horizon, radius=radius, ghosts=numGhosts, vegetarian=False)
            if self.mode == 3:
                self.clingo = ClingoHelper(horizon=horizon, radius=radius, ghosts=numGhosts, vegetarian=True)

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()
        features = self.featExtractor.getFeatures(state, action)
        weights = self.getWeights()
        return sum([features[key] * weights[key] for key in features])

    def update(self, state, action, nextState, reward):
        """
           Should update your weights based on transition
        """
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()
        futureValue = reward + self.discount * self.getValue(nextState)
        currentValue = self.getQValue(state, action)
        predictedReward = futureValue - currentValue
        features = self.featExtractor.getFeatures(state, action)
        for key in self.getWeights():
            self.weights[key] += self.alpha * predictedReward * features[key]

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining and self.mode == 0:
            # you might want to print your weights here for debugging
            "*** YOUR CODE HERE ***"

            # pass
            #print(self.getWeights())
            name = self.name.split('.')[0]
            os.makedirs(
                os.path.dirname(
                    'layouts/learning/' + self.featExtractor.__class__.__name__ + '/%s.pkl' % name),
                exist_ok=True)
            pickle.dump(self.getWeights(),
                        open(
                            'layouts/learning/' + self.featExtractor.__class__.__name__ + '/%s.pkl' % name,
                            'wb'))
