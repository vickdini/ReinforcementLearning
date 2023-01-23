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
    '''
    for i in range(episodes):
        print("Episode:", i)
        score = 0
        done = False
        stateTemp = env.reset()
        state = state[0]
        loss_ep = 0
        step = 0

        for j in range(steps):
            a = agent.choose_action(t.FloatTensor(state).unsqueeze(0))
            action = tuple([a])  # action is a tuple of all agent actions

            state_, reward, done, _ = env.step(action)
            env.render()  # comment this line to train faster
            state_ = state_[0]
            reward = reward[0]
            done = done[0]

            score += reward
            loss = agent.learn(state, a, reward, state_)
            loss_ep += loss
            step += 1
            state = state_

        # loss_ep /= step
        # """scores.append(score)
        # eps_history.append(agent.epsilon)
        # losses.append(loss_ep)"""
        # writer.add_scalar("SCORES", score, i)
        # writer.add_scalar("epsilon", agent.epsilon, i)
        # writer.add_scalar("loss_ep", loss_ep, i)

    agent.save_model("./saved_models")
    env.destroy()
    '''

    manual_control = ManualControl(env, agent_view=agent_view, seed=None)
    manual_control.start()

