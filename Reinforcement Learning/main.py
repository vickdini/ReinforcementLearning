from __future__ import annotations

from time import sleep

import gymnasium as gym
import minigrid
from minigrid.wrappers import ImgObsWrapper, RGBImgPartialObsWrapper
from minigrid.utils.window import Window

import torch as t
from tensorboardX import SummaryWriter
import numpy as np

import warehouse, model

def observationToState(grid, direction):
    state = []

    for i in range(len(grid)):
        if (grid[i] == None):
            state.append(0)
        elif (type(grid[i]) is minigrid.core.world_object.Wall):
            state.append(-1)
        elif (type(grid[i]) is minigrid.core.world_object.Goal):
            state.append(1)
    state.append(direction)

    return state

if __name__ == "__main__":
    episodes = 100
    steps = 5000

    env = gym.make("WarehouseEnv-v0", agent1_pos=(2, 3), agent2_pos=(7, 6), goal_pos=(4, 8), max_steps = steps)
    agent_view = False

    if agent_view:
        print("Using agent view")
        env = RGBImgPartialObsWrapper(env, env.tile_size)
        env = ImgObsWrapper(env)

    writer = SummaryWriter("./logs")

    # scores = []
    # eps_history = []
    # losses = []

    window = Window("Project 2 - Vick Dini")
    window.set_caption(env.mission + "\nEpisode: 1")
    window.show(block=False)

    agent = model.DQN(
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
        done = False

        obs = env.reset()
        state1 = observationToState(obs["grid1"], obs["direction1"])
        state2 = observationToState(obs["grid2"], obs["direction2"])
        # state = state1 + state2
        window.show_img(env.get_frame(agent_pov=agent_view))
        sleep(0.1)

        loss_ep = 0
        step = 0

        for j in range(steps):
            action = agent.choose_action(t.FloatTensor(state).unsqueeze(0))

            obs_, reward, done, truncated, u = env.step(action)
            state_ = observationToState(obs_["grid"], obs_["direction"])

            print(f"step={env.step_count}, reward={reward:.2f}")
            env.render()
            window.set_caption(env.mission + "\nEpisode: " + str(i + 1) + "    Range: " + str(j))
            window.show_img(env.get_frame(agent_pov=agent_view))

            score += reward
            loss = agent.learn(state, action, reward, state_)
            loss_ep += loss
            step += 1
            state = state_

            if done:
                print("terminated!")
                window.set_caption(env.mission + "\nEpisode: " + str(i + 1) + "    Range: " + str(j) + "    Reward: " + str(score))
                window.show_img(env.get_frame(agent_pov=agent_view))
                sleep(0.5)
                break
            elif truncated:
                print("truncated!")
                break

            sleep(0.01)

        # loss_ep /= step
        # """scores.append(score)
        # eps_history.append(agent.epsilon)
        # losses.append(loss_ep)"""
        # writer.add_scalar("SCORES", score, i)
        # writer.add_scalar("epsilon", agent.epsilon, i)
        # writer.add_scalar("loss_ep", loss_ep, i)

    agent.save_model("./saved_models")
    env.destroy()