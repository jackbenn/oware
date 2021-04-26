from game import Game
from agent import Agent

class Manager:
    def __init__(self):
        self.agents = [Agent(),
                       Agent()

    def play_game(self):
        '''play a single game between agents'''
        game = Game()
        player = 0
        state = game.state(player)
        
    
    def load_agents(self):
        '''load agent weights from file'''
        pass

    def save_agents(self):
        '''save agent weights to file'''
        pass