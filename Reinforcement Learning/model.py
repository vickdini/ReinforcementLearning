import torch as t
import torch.nn as nn
import numpy as np
from torch.nn.functional import fractional_max_pool2d_with_indices
import torch.optim as optim
import os
import time


class FeedForwardNN(nn.Module):
    def __init__(self, n_features, n_actions) -> None:
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions)
        )

    def forward(self, observation: np.ndarray):
        if isinstance(observation, np.ndarray):
            observation = t.FloatTensor(observation)
        return self.net(observation)


class DQN(nn.Module):
    def __init__(self,
                 n_features,
                 n_actions,
                 lr: float,
                 reward_decay: float,
                 epsilon: float,
                 eps_dec: float,
                 eps_min: float) -> None:
        super().__init__()
        # member variables
        self.n_features = n_features
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = reward_decay
        self.eps_dec = eps_dec
        self.eps_min = eps_min
        self.epsilon = epsilon

        # neural network
        self.net = FeedForwardNN(n_features, n_actions)

        # optimizer, loss function and device
        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)
        self.device = t.device("cuda:0" if t.cuda.is_available() else "cpu")
        self.to(self.device)
        self.lossfunc = nn.MSELoss()

    def forward(self, state: t.Tensor) -> t.Tensor:
        state = state.to(self.device)
        return self.net(state)

    def choose_action(self, state: t.FloatTensor) -> int:
        if np.random.random() > self.epsilon:
            state = state.to(self.device)
            actions = self.forward(state)
            action = t.argmax(actions).item()
        else:
            action = np.random.choice(self.n_actions)

        return action

    def learn(self, state, action, reward, state_):
        self.optimizer.zero_grad()
        states = t.FloatTensor(state).to(self.device)
        actions = t.tensor(action).to(self.device)
        rewards = t.tensor(reward, dtype=t.float32).to(self.device)
        states_ = t.FloatTensor(state_).to(self.device)

        q_pred = self.forward(states)[actions]

        q_target = rewards+self.gamma * self.forward(states_).max()

        loss = self.lossfunc(q_pred, q_target)
        loss.backward()
        self.optimizer.step()
        self._decrement_epsilon()
        return loss.item()

    def _decrement_epsilon(self):
        self.epsilon = self.epsilon-self.eps_dec\
            if self.epsilon > self.eps_min else self.eps_min

    def save_model(self, dir: str):
        if not os.path.exists(dir):
            os.makedirs(dir)
        save_time = "{}-{}-{} {}-{}-{}".format(time.localtime()[0],
                                               time.localtime()[1],
                                               time.localtime()[2],
                                               time.localtime()[3],
                                               time.localtime()[4],
                                               time.localtime()[5], )
        t.save(self.net.state_dict(), os.path.join(
            dir, "DQN {}.pth".format(save_time)))
