import os
import argparse
import numpy as np
from game import Game
from agent import Agent


class Manager:
    def __init__(self, size=6):
        self.size = size
        self.agent_names = [None, None]
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
            if tuple(game.score) != old_score:
                print(f"{t:3} Player {player} moved {action} score {game.score}")
                print(game)
                old_score = tuple(game.score)

            player = 1 - player
            t += 1
        print(f"{t:3} Winner is {game.winner}")
        return game.winner

    def load_agents(self):
        '''load from file if exists or initialize'''
        self.agents[0].load('agent0')
        self.agents[1].load('agent1')

    def save_agents(self):
        '''save agent weights to file'''
        self.agents[0].save('agent0')
        self.agents[1].save('agent1')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count',
                        help='Number of games',
                        action='store',
                        type=int,
                        default=1)
    args = parser.parse_args()
    m = Manager(size=3)
    m.load_agents()
    m.save_agents()
    for i in range(args.count):
        print(f"\nPlaying game {i}")
        winner = m.play_game()
        m.save_agents()