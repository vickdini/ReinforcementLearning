from __future__ import annotations

import gymnasium as gym
from minigrid.wrappers import ImgObsWrapper, RGBImgPartialObsWrapper

import torch as t
from tensorboardX import SummaryWriter
import numpy as np

import warehouse, model
from ManualControl import ManualControl

if __name__ == "__main__":
    env = gym.make("WarehouseEnv", agent_pos=(2, 3), goal_pos=(4, 8))
    agent_view = False

    if agent_view:
        print("Using agent view")
        env = RGBImgPartialObsWrapper(env, env.tile_size)
        env = ImgObsWrapper(env)

    writer = SummaryWriter("./logs")

    episodes = 100
    steps = 5000
    # scores = []
    # eps_history = []
    # losses = []

    agent = model.DQN(
       n_features=env.observation_space.n,
       n_actions=env.action_space.n,
       lr=1e-3,
       reward_decay=0.99,
       epsilon=1.0,
       eps_dec=1e-5,
       eps_min=1e-2)

    manual_control = ManualControl(env, agent_view=agent_view, seed=None)
    manual_control.start()

