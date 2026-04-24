import os
import random
import datetime
import argparse
import numpy as np
from game import Game
from agent import Agent


class Manager:
    def __init__(self, size=6):
        self.size = size
        self.model_names = [None, None]
        self.agents = [Agent(epsilon=0.1, state_size=114),
                       Agent(epsilon=0.1, state_size=114)]

    def play_game(self, train=True):
        '''play a single game between agents'''
        game = Game(size=self.size)
        player = 0
        states = [[None], [None]]
        actions = [[None], [None]]
        old_score = (0, 0)

        if not train:
            saved_epsilons = [a.epsilon for a in self.agents]
            for a in self.agents:
                a.epsilon = 0.05

        t = 0
        while True:
            agent = self.agents[player]
            states[player].append(game.get_state(player))
            legal_moves = [i for i in range(self.size) if game.houses[player, i] > 0]

            last_state = states[player][-2] if train else None
            last_action = actions[player][-1] if train else None
            action = agent.move(last_state, last_action, 0, states[player][-1], legal_moves)

            actions[player].append(action)
            game.move(action)

            if game.done:
                if train:
                    reward = 1 if player == game.winner else -1
                    agent.move(states[player][-1], actions[player][-1], reward, None)
                    self.agents[1-player].move(states[1-player][-1],
                                               actions[1-player][-1],
                                               -reward, None)
                break

            if tuple(game.score) != old_score:
                print(f"{t:3} Player {player} moved {action} score {game.score}")
                print(game)
                old_score = tuple(game.score)

            player = 1 - player
            t += 1

        if not train:
            for a, e in zip(self.agents, saved_epsilons):
                a.epsilon = e

        print(f"{t:3} Winner is {game.winner}", flush=True)
        return game.winner

    def load_agents(self):
        '''load from file if exists or initialize'''
        self.agents[0].load(self.model_names[0])
        self.agents[1].load(self.model_names[1])

    def save_agents(self):
        '''save agent weights to file'''
        self.agents[0].save(self.model_names[0])
        self.agents[1].save(self.model_names[1])


def list_models():
    model_dir = Agent.model_dir
    if not os.path.isdir(model_dir):
        print("No models directory found.")
        return
    files = sorted(f for f in os.listdir(model_dir) if not f.startswith('.'))
    if not files:
        print("No saved models found.")
        return
    print(f"{'Model':<30} {'Size':>12}  Modified")
    print('-' * 58)
    for f in files:
        path = os.path.join(model_dir, f)
        size = os.path.getsize(path)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        print(f"{f:<30} {size:>10,}B  {mtime:%Y-%m-%d %H:%M}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count', help='Number of games', type=int, default=1)
    parser.add_argument('-0', '--model0', help='Name of model for Agent 0', default='model0')
    parser.add_argument('-1', '--model1', help='Name of model for Agent 1', default='model1')
    parser.add_argument('--no-train', action='store_true', help='Play without training')
    parser.add_argument('--list', action='store_true', help='List saved models and exit')
    args = parser.parse_args()

    if args.list:
        list_models()
    else:
        train = not args.no_train
        m = Manager(size=3)
        m.model_names = [args.model0, args.model1]
        m.load_agents()

        wins = [0, 0]
        draws = 0
        for i in range(args.count):
            seed = random.randint(0, 2**31 - 1)
            np.random.seed(seed)
            print(f"\nPlaying game {i} (seed {seed})")
            winner = m.play_game(train=train)
            if train:
                m.save_agents()
            if winner == 0.5:
                draws += 1
            else:
                wins[int(winner)] += 1

        print(f"\nResults over {args.count} game(s):")
        print(f"  Player 0: {wins[0]:4d} wins")
        print(f"  Player 1: {wins[1]:4d} wins")
        if draws:
            print(f"  Draws:    {draws:4d}")
