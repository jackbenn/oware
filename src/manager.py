from game import Game
from agent import Agent


class Manager:
    def __init__(self):
        self.agents = [Agent(),
                       Agent()]

    def play_game(self):
        '''play a single game between agents'''
        game = Game()
        player = 0
        state = game.state(player)
        rewards = []
        states = []
        states.append(game.state)
        rewards.append(agent[0].move(state[-2], 0, states[-1]))

        while True:
            states.append(game.state)
            reward = rewards[-1] - rewards[-2]
            rewards.append(agent[1].move(state,
                                         states[-1]))

    def load_agents(self):
        '''load agent weights from file'''
        agent[0].load('agent0')
        agent[1].load('agent1')

    def save_agents(self):
        '''save agent weights to file'''
        agent[0].save('agent0')
        agent[1].save('agent1')
