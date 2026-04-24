import os
import random
import datetime
import logging
import argparse
import numpy as np
from game import Game
from agent import Agent

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, size=6):
        self.size = size
        self.model_names = [None, None]
        self.agents = [Agent(epsilon=0.1, state_size=114),
                       Agent(epsilon=0.1, state_size=114)]

    def play_game(self, train=True):
        '''Play a single game. Returns (winner, turns, score, avg_loss).'''
        game = Game(size=self.size)
        player = 0
        states = [[None], [None]]
        actions = [[None], [None]]
        old_score = (0, 0)
        losses = []

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
            action, loss = agent.move(last_state, last_action, 0,
                                      states[player][-1], legal_moves)
            if loss is not None:
                losses.append(loss)

            actions[player].append(action)
            game.move(action)

            logger.debug('%3d  p%d -> house %d', t, player, action)
            if tuple(game.score) != old_score:
                logger.debug('     score %s\n%s', game.score, game)
                old_score = tuple(game.score)

            if game.done:
                if train:
                    reward = 1 if player == game.winner else -1
                    _, loss = agent.move(states[player][-1],
                                         actions[player][-1], reward, None)
                    if loss is not None:
                        losses.append(loss)
                    _, loss = self.agents[1-player].move(states[1-player][-1],
                                                         actions[1-player][-1],
                                                         -reward, None)
                    if loss is not None:
                        losses.append(loss)
                break

            player = 1 - player
            t += 1

        if not train:
            for a, e in zip(self.agents, saved_epsilons):
                a.epsilon = e

        avg_loss = float(np.mean(losses)) if losses else None
        return game.winner, t, game.score.copy(), avg_loss

    def load_agents(self):
        '''Load from file if exists, otherwise initialize.'''
        self.agents[0].load(self.model_names[0])
        self.agents[1].load(self.model_names[1])

    def save_agents(self):
        '''Save agent weights to file.'''
        self.agents[0].save(self.model_names[0])
        self.agents[1].save(self.model_names[1])


def list_models():
    model_dir = Agent.model_dir
    if not os.path.isdir(model_dir):
        logger.info('No models directory found.')
        return
    files = sorted(f for f in os.listdir(model_dir) if not f.startswith('.'))
    if not files:
        logger.info('No saved models found.')
        return
    logger.info('%-30s  %12s  %s', 'Model', 'Size', 'Modified')
    logger.info('-' * 58)
    for f in files:
        path = os.path.join(model_dir, f)
        size = os.path.getsize(path)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        logger.info('%-30s  %10,dB  %s', f, size, mtime.strftime('%Y-%m-%d %H:%M'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count', help='Number of games', type=int, default=1)
    parser.add_argument('-0', '--model0', help='Name of model for Agent 0', default='model0')
    parser.add_argument('-1', '--model1', help='Name of model for Agent 1', default='model1')
    parser.add_argument('--no-train', action='store_true', help='Play without training')
    parser.add_argument('--list', action='store_true', help='List saved models and exit')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show per-move detail')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s',
    )

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
            winner, turns, score, avg_loss = m.play_game(train=train)
            if train:
                m.save_agents()

            winner_str = 'draw' if winner == 0.5 else f'player {int(winner)}'
            loss_str = f'  avg_loss={avg_loss:.4f}' if avg_loss is not None else ''
            logger.info('Game %3d (seed %10d): %-8s  turns=%3d  score=[%d %d]%s',
                        i, seed, winner_str, turns, score[0], score[1], loss_str)

            if winner == 0.5:
                draws += 1
            else:
                wins[int(winner)] += 1

        logger.info('')
        logger.info('Results over %d game(s):', args.count)
        logger.info('  Player 0: %4d wins', wins[0])
        logger.info('  Player 1: %4d wins', wins[1])
        if draws:
            logger.info('  Draws:    %4d', draws)
