import numpy as np
import os
from tensorflow import keras
from tensorflow.keras.layers import Activation, Dense, Input
from tensorflow.keras.models import Model


class Agent:
    model_dir = 'models'

    def __init__(self, epsilon, discount=1, size=6):
        self.discount = discount
        self.epsilon = epsilon
        self.size = size
        self.model = None
    
    def initialize_model(self):
        inputs = Input(self.size * 2, name='input')
        x = inputs
        x = Dense(16)(x)
        x = Dense(32)(x)
        x = Dense(self.size, name='output')(x)
        self.model = Model(inputs, x, name='model')
        # no idea the best opitmizer
        self.model.compile(optimizer='adam',
                           loss='mean_squared_error')

    def update(self, last_state, last_action, reward, state):
        # terminal state has state == None
        if state is None:
            qmax = 0
        else:
            qmax = np.max(self.predict(state))
        
        last_qs = self.predict(last_state)
        #print(last_qs)
        last_qs[last_action] = reward + self.discount * qmax
        self.model.fit(last_state[None, :],
                       last_qs[None, :],
                        verbose=0)

    def move(self, last_state, last_action, reward, state):
        '''Decide on the next move and update the model
         * Predict the q values for all the possible actions from state
         * Update the model based on the rewards from the prior step
         * Choose the best action following epsilon-greedy
        Parameters:
            last_state: the previous state, used in the update
            reward: the reward since the last state, use in the update
            state: current state
        Returns:
            the new state
            the reward from that move?
        '''
        if last_state is not None: # if this isn't the first move
            self.update(last_state, last_action, reward, state)
    
        if state is None:  # if we're done with the game
            return

        qs = self.predict(state)
        if np.random.random() < self.epsilon:
            #print('random', end='')
            action = np.random.randint(self.size)
        else:
            # choose randomly among ties
            action = np.random.choice(np.flatnonzero(qs ==
                                                     qs.max()))
        #print(action)
        return action

    def predict(self, state):
        return self.model.predict(state[None, :])[0]

    def save(self, filename):
        path = os.path.join(self.model_dir, filename)
        self.model.save(path)

    def load(self, filename):
        path = os.path.join(self.model_dir, filename)
        if os.path.exists(path):
            self.model = keras.models.load_model(path)
        else:
            self.initialize_model()