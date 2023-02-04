from __future__ import annotations

from warehouse.envs.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Goal
from warehouse.envs.minigrid_env_mod import MiniGridEnvMod

from gymnasium import spaces


class WarehouseEnv(MiniGridEnvMod):

    def __init__(self, agent1_pos=None, agent2_pos=None, goal_pos=None, max_steps=100, **kwargs):
        self._agent1_default_pos = agent1_pos
        self._agent2_default_pos = agent2_pos
        self._goal_default_pos = goal_pos

        # Grid size (in cells, per side): left border + 8 cells + right border
        self.size = 10
        mission_space = MissionSpace(mission_func=self._gen_mission)

        super().__init__(
            mission_space=mission_space,
            width=self.size,
            height=self.size,
            agent_view_size=3,
            max_steps=max_steps,
            **kwargs,
        )

        # Actions are discrete integer values
        #self.action_space = spaces.Discrete(len(self.actions))
        
        # The amount of observations corresponds to the number of cells in the grid (8x8)
        #num_states = 64
        #self.observation_space = spaces.Discrete(num_states)


    @staticmethod
    def _gen_mission():
        return "Reach the target location"

    def _gen_grid(self, width, height):
        # Create the grid
        self.grid = Grid(width, height)

        # Generate the surrounding walls
        self.grid.horz_wall(0, 0)
        self.grid.horz_wall(0, height - 1)
        self.grid.vert_wall(0, 0)
        self.grid.vert_wall(width - 1, 0)

        # Generate the internal walls
        self.grid.horz_wall(4, 2)
        self.grid.vert_wall(4, 3, length=3)

        self.grid.vert_wall(1, 7, length=2)
        self.grid.vert_wall(2, 7, length=2)

        self.grid.vert_wall(6, 5, length=4)

        # Set the start position and orientation of agent 1
        if self._agent1_default_pos is not None:
            self.agent1_pos = self._agent1_default_pos
            self.grid.set(*self._agent1_default_pos, None)
            # assuming random start direction
            self.agent1_dir = 1
        else:
            self.place_agent1()

        # Set the start position and orientation of agent 2
        if self._agent2_default_pos is not None:
            self.agent2_pos = self._agent2_default_pos
            self.grid.set(*self._agent2_default_pos, None)
            # assuming random start direction
            self.agent2_dir = 1
        else:
            self.place_agent2()

        if self._goal_default_pos is not None:
            goal = Goal()
            self.put_obj(goal, *self._goal_default_pos)
            goal.init_pos, goal.cur_pos = self._goal_default_pos
        else:
            self.place_obj(Goal())
