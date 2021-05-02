import os
import numpy as np
from game import Game
from agent import Agent


class Manager:
    def __init__(self, size=6):
        self.size = size
        self.agents = [Agent(epsilon=0.1, size=self.size),
                       Agent(epsilon=0.1, size=self.size)]

    def play_game(self):
        '''play a single game between agents'''
        game = Game(size=self.size)
        player = 0
        states = [[None], [None]]
        actions = [[None], [None]]
        old_score = (0, 0)


        t = 0
        while True:
            agent = self.agents[player]
            states[player].append(game.get_state(player))
            action = agent.move(states[player][-2],
                                actions[player][-1],
                                0,
                                states[player][-1])
            actions[player].append(action)
            game.move(action)

            if game.done:
                reward = 1 if player == game.winner else -1
                agent.move(states[player][-1],
                           actions[player][-1],
                           reward,
                           None)
                self.agents[1-player].move(states[1-player][-1],
                                           actions[1-player][-1],
                                           -reward,
                                           None)
                break
            if (game.score != old_score).any():
                print(f"{t:3} Player {player} moved {action} score {game.score}")
                print(game)
                old_score = game.score.copy()

            player = 1 - player
            t += 1
        return game.winner

    def load_agents(self):
        '''load agents from file if they exist'''
        if os.path.exists('agent0') and os.path.exists('agent1'):
            self.agents[0].load('agent0')
            self.agents[1].load('agent1')
            return True
        return False

    def save_agents(self):
        '''save agent weights to file'''
        self.agents[0].save('agent0')
        self.agents[1].save('agent1')


if __name__ == '__main__':
    m = Manager(size=3)
    m.load_agents()

    m.save_agents()
    for i in range(10):
        print(f"\nPlaying game {i}")
        winner = m.play_game()
        print(f"Winner is {winner}")
        m.save_agents()