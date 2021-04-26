import numpy as np
from tensorflow import keras
from tensorflow.keras.layers import Activation, Dense, Input
from tensorflow.keras.models import Model

class Agent:
    def __init__(self, size=6):
        self.size = size
        self.initialize_model()

    def initialize_model(self):
        inputs = Input(self.size * 2, name='input')
        x = inputs
        x = Dense(32)(x)
        x = Dense(64)(x)
        x = Dense(self.size, name='output')(x)
        self.model = Model(inputs, x, name='model')
        # no idea the best opitmizer
        self.model.compile(optimizer='rmsprop',
                           loss='mean_squared_error')

    def update(self, state, action, next_state, reward=0, terminal=False):
        # not sure of the inputs
        pass

    def move(self, last_state, reward, state):
        '''Decide on the next move and update the model
         * Predict the q values for all the possible actions
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
        pass
    
    def predict_q(self, state):
        return self.model.predict(state[1, -1])

