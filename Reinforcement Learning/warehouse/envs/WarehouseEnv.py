from __future__ import annotations

from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Goal
from warehouse.envs.minigrid_env_mod import MiniGridEnvMod

from gymnasium import spaces


class WarehouseEnv(MiniGridEnvMod):

    """
    ## Mission Space

    "reach the goal"

    ## Action Space

    | Num | Name         | Action       |
    |-----|--------------|--------------|
    | 0   | left         | Turn left    |
    | 1   | right        | Turn right   |
    | 2   | forward      | Move forward |
    | 3   | pickup       | Unused       |
    | 4   | drop         | Unused       |
    | 5   | toggle       | Unused       |
    | 6   | done         | Unused       |

    ## Observations

    The observations consist of the part of the grid that the agent currently sees.

    ## Rewards

    A reward of '1' is given for success, and '0' for failure.

    ## Termination

    The episode ends if any one of the following conditions is met:

    1. The agent reaches the goal.
    2. Timeout (see `max_steps`).

    """

    def __init__(self, agent_pos=None, goal_pos=None, max_steps=100, **kwargs):
        self._agent_default_pos = agent_pos
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

        # Randomize the player start position and orientation
        if self._agent_default_pos is not None:
            self.agent_pos = self._agent_default_pos
            self.grid.set(*self._agent_default_pos, None)
            # assuming random start direction
            self.agent_dir = self._rand_int(0, 4)
        else:
            self.place_agent()

        if self._goal_default_pos is not None:
            goal = Goal()
            self.put_obj(goal, *self._goal_default_pos)
            goal.init_pos, goal.cur_pos = self._goal_default_pos
        else:
            self.place_obj(Goal())
