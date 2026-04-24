import numpy as np
import os
import torch
import torch.nn as nn
import torch.optim as optim


class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, action_size),
        )
        layers = [m for m in self.net if isinstance(m, nn.Linear)]
        for layer in layers[:-1]:
            nn.init.kaiming_normal_(layer.weight, nonlinearity='relu')
            nn.init.zeros_(layer.bias)
        nn.init.xavier_uniform_(layers[-1].weight)
        nn.init.zeros_(layers[-1].bias)

    def forward(self, x):
        return self.net(x)


class Agent:
    model_dir = 'trained_models'

    def __init__(self, epsilon, discount=1, size=3, state_size=12):
        self.discount = discount
        self.epsilon = epsilon
        self.size = size
        self.state_size = state_size
        self.model = None
        self.optimizer = None
        self.loss_fn = nn.MSELoss()

    def initialize_model(self):
        self.model = QNetwork(self.state_size, self.size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)

    def predict(self, state):
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(state)
            return self.model(x).numpy()

    def update(self, last_state, last_action, reward, state):
        if state is None:
            qmax = 0
        else:
            qmax = np.max(self.predict(state))

        last_qs = self.predict(last_state).copy()

        print(reward, last_action)
        print(last_qs)

        last_qs[last_action] = reward + self.discount * qmax

        self.model.train()
        self.optimizer.zero_grad()
        x = torch.FloatTensor(last_state)
        target = torch.FloatTensor(last_qs)
        loss = self.loss_fn(self.model(x), target)
        loss.backward()
        self.optimizer.step()

        print(self.predict(last_state))
        print()

    def move(self, last_state, last_action, reward, state, legal_moves=None):
        if last_state is not None:
            self.update(last_state, last_action, reward, state)

        if state is None:
            return

        qs = self.predict(state)
        if legal_moves is not None:
            mask = np.ones(self.size, dtype=bool)
            mask[legal_moves] = False
            qs[mask] = -np.inf
        choices = legal_moves if legal_moves is not None else list(range(self.size))
        if np.random.random() < self.epsilon:
            action = np.random.choice(choices)
        else:
            action = np.random.choice(np.flatnonzero(qs == qs.max()))
        return action

    def save(self, filename):
        path = os.path.join(self.model_dir, filename)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)

    def load(self, filename):
        path = os.path.join(self.model_dir, filename)
        if os.path.exists(path):
            self.initialize_model()
            checkpoint = torch.load(path, weights_only=True)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        else:
            self.initialize_model()
