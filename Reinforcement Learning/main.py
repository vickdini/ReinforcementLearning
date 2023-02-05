from __future__ import annotations

from time import sleep
import warnings

import gymnasium as gym
import minigrid
from minigrid.wrappers import ImgObsWrapper, RGBImgPartialObsWrapper
from minigrid.utils.window import Window

import torch as t
from tensorboardX import SummaryWriter
import numpy as np

import warehouse, model

def observationToState(grid):
    state = []

    for i in range(len(grid)):
        if (grid[i] == None):
            state.append(0)
        elif (type(grid[i]) is minigrid.core.world_object.Wall):
            state.append(-1)
        elif (type(grid[i]) is minigrid.core.world_object.Goal):
            state.append(1)

    return state

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    # Change this value to True to enable the GUI or False to disable it.
    enableUI = False

    episodes = 100
    steps = 5000

    env = gym.make("WarehouseEnv-v0", agent1_pos=(2, 3), agent2_pos=(7, 6), goal_pos=(4, 8), max_steps = steps)
    agent_view = False

    writer = SummaryWriter("./logs")

    scores = []
    eps1_history = []
    eps2_history = []
    losses = []

    if enableUI:
        window = Window("Project 2 - Vick Dini")
        window.set_caption(env.mission + "\nEpisode: 1")
        window.show(block=False)

    agent1 = model.DQN(
       n_features=env.observation_space.n,
       n_actions=env.action_space.n - 1,
       lr=1e-3,
       reward_decay=0.99,
       epsilon=1.0,
       eps_dec=1e-5,
       eps_min=1e-2)

    agent2 = model.DQN(
        n_features=env.observation_space.n,
        n_actions=env.action_space.n - 1,
        lr=1e-3,
        reward_decay=0.99,
        epsilon=1.0,
        eps_dec=1e-5,
        eps_min=1e-2)

    for i in range(episodes):
        print("Episode:", i + 1)
        score = 0
        done1 = False
        done2 = False
        reward1 = 0
        reward2 = 0

        obs = env.reset()
        state1 = observationToState(obs["grid1"])
        state2 = observationToState(obs["grid2"])

        if enableUI:
            window.show_img(env.get_frame(agent_pov=agent_view))
            sleep(0.1)

        loss_ep = 0
        step = 0

        for j in range(steps):
            if not done1:
                action1 = agent1.choose_action(t.FloatTensor(state1).unsqueeze(0))
                obs1_, reward1_, done1, truncated1, u1 = env.stepN(action1, 1, reward1)
                state1_ = observationToState(obs1_["grid1"])
                loss1 = agent1.learn(state1, action1, reward1_, state1_)
                state1 = state1_
                reward1 = reward1_
            if not done2:
                action2 = agent2.choose_action(t.FloatTensor(state2).unsqueeze(0))
                obs2_, reward2_, done2, truncated2, u2 = env.stepN(action2, 2, reward2)
                state2_ = observationToState(obs2_["grid2"])
                loss2 = agent2.learn(state2, action2, reward2_, state2_)
                state2 = state2_
                reward2 = reward2_

            env.render()
            if enableUI:
                window.set_caption(env.mission + "\nEpisode: " + str(i + 1) + "    Actions: " + str(j) + "    Reward1: " + str(reward1) + "    Reward2: " + str(reward2))
                window.show_img(env.get_frame(agent_pov=agent_view))

            loss_ep += loss1 + loss2
            loss1 = 0
            loss2 = 0

            step += 1

            if done1 and done2:
                score += reward1 + reward2
                print(f"> Terminated: steps = {env.step_count}, reward1 = {reward1:.2f}, reward2 = {reward2:.2f}, score = {score:.2f}")

                if enableUI:
                    window.set_caption(env.mission + "\nEpisode: " + str(i + 1) + "    Actions: " + str(j) + "    Combined reward: " + str(score))
                    window.show_img(env.get_frame(agent_pov=agent_view))
                    sleep(0.5)

                break
            elif truncated1 or truncated2:
                print("> Truncated")
                break

            if enableUI: sleep(0.01)

        loss_ep /= step
        scores.append(score)
        eps1_history.append(agent1.epsilon)
        eps2_history.append(agent2.epsilon)
        losses.append(loss_ep)
        writer.add_scalar("SCORES", score, i)
        writer.add_scalar("epsilon1", agent1.epsilon, i)
        writer.add_scalar("epsilon2", agent2.epsilon, i)
        writer.add_scalar("loss_ep", loss_ep, i)

    agent1.save_model("./saved_models")
    agent2.save_model("./saved_models")

    writer.close()
