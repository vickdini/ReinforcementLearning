from __future__ import annotations

import hashlib
import math
from abc import abstractmethod
from enum import IntEnum
from typing import Iterable, TypeVar

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from minigrid.core.constants import COLOR_NAMES, DIR_TO_VEC, TILE_PIXELS
from warehouse.envs.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Point, WorldObj
from minigrid.utils.window import Window

T = TypeVar("T")


class MiniGridEnvMod(gym.Env):
    """
    2D grid world game environment
    """

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 10,
    }

    # Enumeration of possible actions
    class Actions(IntEnum):
        # Turn left, turn right, move forward
        left = 0
        right = 1
        up = 2
        down = 3
        stay = 4
        # Done completing task
        done = 6

    def __init__(
        self,
        mission_space: MissionSpace,
        grid_size: int | None = None,
        width: int | None = None,
        height: int | None = None,
        max_steps: int = 100,
        see_through_walls: bool = False,
        agent_view_size: int = 7,
        render_mode: str | None = None,
        highlight: bool = True,
        tile_size: int = TILE_PIXELS,
        agent_pov: bool = False,
    ):
        # Initialize mission
        self.mission = mission_space.sample()

        # Can't set both grid_size and width/height
        if grid_size:
            assert width is None and height is None
            width = grid_size
            height = grid_size
        assert width is not None and height is not None

        # Action enumeration for this environment
        self.actions = MiniGridEnvMod.Actions

        # Actions are discrete integer values
        self.action_space = spaces.Discrete(len(self.actions))

        # Number of cells (width and height) in the agent view
        assert agent_view_size % 2 == 1
        assert agent_view_size >= 3
        self.agent_view_size = agent_view_size

        # The observations are comprised of a snapshot of what the agent is currently seeing.
        self.observation_space = spaces.Discrete(agent_view_size ** 2)

        # Observations are dictionaries containing an
        # encoding of the grid and a textual 'mission' string
        # image_observation_space = spaces.Box(
        #     low=0,
        #     high=255,
        #     shape=(self.agent_view_size, self.agent_view_size, 3),
        #     dtype="uint8",
        # )
        # self.observation_space = spaces.Dict(
        #     {
        #         "image": image_observation_space,
        #         "direction": spaces.Discrete(4),
        #         "mission": mission_space,
        #     }
        # )

        # Range of possible rewards
        self.reward_range = (0, 1)

        self.window: Window = None

        # Environment configuration
        self.width = width
        self.height = height

        assert isinstance(
            max_steps, int
        ), f"The argument max_steps must be an integer, got: {type(max_steps)}"
        self.max_steps = max_steps

        self.see_through_walls = see_through_walls

        # Current position and direction of the agent
        self.agent1_pos: np.ndarray | tuple[int, int] = None
        self.agent1_dir: int = None
        self.agent2_pos: np.ndarray | tuple[int, int] = None
        self.agent2_dir: int = None

        # Current grid and mission and carrying
        self.grid = Grid(width, height)
        self.carrying = None

        # Rendering attributes
        self.render_mode = render_mode
        self.highlight = highlight
        self.tile_size = tile_size
        self.agent_pov = agent_pov

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        # Reinitialize episode-specific variables
        self.agent1_pos = (-1, -1)
        self.agent1_dir = -1
        self.agent2_pos = (-1, -1)
        self.agent2_dir = -1

        # Generate a new random grid at the start of each episode
        self._gen_grid(self.width, self.height)

        # These fields should be defined by _gen_grid
        assert (
            self.agent1_pos >= (0, 0)
            if isinstance(self.agent1_pos, tuple)
            else all(self.agent1_pos >= 0) and self.agent1_dir >= 0
        )

        assert (
            self.agent2_pos >= (0, 0)
            if isinstance(self.agent2_pos, tuple)
            else all(self.agent2_pos >= 0) and self.agent2_dir >= 0
        )

        # Check that the agents don't overlap with an object
        start_cell1 = self.grid.get(*self.agent1_pos)
        assert start_cell1 is None or start_cell1.can_overlap()
        start_cell2 = self.grid.get(*self.agent2_pos)
        assert start_cell2 is None or start_cell2.can_overlap()

        # Item picked up, being carried, initially nothing
        self.carrying = None

        # Step count since episode start
        self.step_count = 0

        if self.render_mode == "human":
            self.render()

        # Return first observation
        obs = self.gen_obs()

        return obs

    def hash(self, size=16):
        """Compute a hash that uniquely identifies the current state of the environment.
        :param size: Size of the hashing
        """
        sample_hash = hashlib.sha256()

        to_encode = [self.grid.encode().tolist(), self.agent_pos, self.agent_dir]
        for item in to_encode:
            sample_hash.update(str(item).encode("utf8"))

        return sample_hash.hexdigest()[:size]

    @property
    def steps_remaining(self):
        return self.max_steps - self.step_count

    def __str__(self):
        """
        Produce a pretty string of the environment's grid along with the agent.
        A grid cell is represented by 2-character string, the first one for
        the object and the second one for the color.
        """

        # Map of object types to short string
        OBJECT_TO_STR = {
            "wall": "W",
            "floor": "F",
            "door": "D",
            "key": "K",
            "ball": "A",
            "box": "B",
            "goal": "G",
            "lava": "V",
        }

        # Map agent's direction to short string
        AGENT_DIR_TO_STR = {0: ">", 1: "V", 2: "<", 3: "^"}

        str = ""

        for j in range(self.grid.height):

            for i in range(self.grid.width):
                if i == self.agent1_pos[0] and j == self.agent1_pos[1]:
                    str += 2 * AGENT_DIR_TO_STR[self.agent1_dir]
                    continue

                if i == self.agent2_pos[0] and j == self.agent2_pos[1]:
                    str += 2 * AGENT_DIR_TO_STR[self.agent2_dir]
                    continue

                c = self.grid.get(i, j)

                if c is None:
                    str += "  "
                    continue

                if c.type == "door":
                    if c.is_open:
                        str += "__"
                    elif c.is_locked:
                        str += "L" + c.color[0].upper()
                    else:
                        str += "D" + c.color[0].upper()
                    continue

                str += OBJECT_TO_STR[c.type] + c.color[0].upper()

            if j < self.grid.height - 1:
                str += "\n"

        return str

    @abstractmethod
    def _gen_grid(self, width, height):
        pass

    def _reward(self) -> float:
        """
        Compute the reward to be given upon success
        """

        return 1 - 0.9 * (self.step_count / self.max_steps)

    def _rand_int(self, low: int, high: int) -> int:
        """
        Generate random integer in [low,high[
        """

        return self.np_random.integers(low, high)

    def _rand_float(self, low: float, high: float) -> float:
        """
        Generate random float in [low,high[
        """

        return self.np_random.uniform(low, high)

    def _rand_bool(self) -> bool:
        """
        Generate random boolean value
        """

        return self.np_random.integers(0, 2) == 0

    def _rand_elem(self, iterable: Iterable[T]) -> T:
        """
        Pick a random element in a list
        """

        lst = list(iterable)
        idx = self._rand_int(0, len(lst))
        return lst[idx]

    def _rand_subset(self, iterable: Iterable[T], num_elems: int) -> list[T]:
        """
        Sample a random subset of distinct elements of a list
        """

        lst = list(iterable)
        assert num_elems <= len(lst)

        out: list[T] = []

        while len(out) < num_elems:
            elem = self._rand_elem(lst)
            lst.remove(elem)
            out.append(elem)

        return out

    def _rand_color(self) -> str:
        """
        Generate a random color name (string)
        """

        return self._rand_elem(COLOR_NAMES)

    def _rand_pos(
        self, x_low: int, x_high: int, y_low: int, y_high: int
    ) -> tuple[int, int]:
        """
        Generate a random (x,y) position tuple
        """

        return (
            self.np_random.integers(x_low, x_high),
            self.np_random.integers(y_low, y_high),
        )

    def place_obj(
        self,
        obj: WorldObj | None,
        top: Point = None,
        size: tuple[int, int] = None,
        reject_fn=None,
        max_tries=math.inf,
    ):
        """
        Place an object at an empty position in the grid

        :param top: top-left position of the rectangle where to place
        :param size: size of the rectangle where to place
        :param reject_fn: function to filter out potential positions
        """

        if top is None:
            top = (0, 0)
        else:
            top = (max(top[0], 0), max(top[1], 0))

        if size is None:
            size = (self.grid.width, self.grid.height)

        num_tries = 0

        while True:
            # This is to handle with rare cases where rejection sampling
            # gets stuck in an infinite loop
            if num_tries > max_tries:
                raise RecursionError("rejection sampling failed in place_obj")

            num_tries += 1

            pos = (
                self._rand_int(top[0], min(top[0] + size[0], self.grid.width)),
                self._rand_int(top[1], min(top[1] + size[1], self.grid.height)),
            )

            # Don't place the object on top of another object
            if self.grid.get(*pos) is not None:
                continue

            # Don't place the object where the agent is
            if np.array_equal(pos, self.agent1_pos):
                continue
            if np.array_equal(pos, self.agent2_pos):
                continue

            # Check if there is a filtering criterion
            if reject_fn and reject_fn(self, pos):
                continue

            break

        self.grid.set(pos[0], pos[1], obj)

        if obj is not None:
            obj.init_pos = pos
            obj.cur_pos = pos

        return pos

    def put_obj(self, obj: WorldObj, i: int, j: int):
        """
        Put an object at a specific position in the grid
        """

        self.grid.set(i, j, obj)
        obj.init_pos = (i, j)
        obj.cur_pos = (i, j)

    def place_agent1(self, top=None, size=None, rand_dir=True, max_tries=math.inf):
        """
        Set the agent's starting point at an empty position in the grid
        """

        self.agent1_pos = (-1, -1)
        pos = self.place_obj(None, top, size, max_tries=max_tries)
        self.agent1_pos = pos

        if rand_dir:
            self.agent1_dir = self._rand_int(0, 4)

        return pos

    def place_agent2(self, top=None, size=None, rand_dir=True, max_tries=math.inf):
        """
        Set the agent's starting point at an empty position in the grid
        """

        self.agent2_pos = (-1, -1)
        pos = self.place_obj(None, top, size, max_tries=max_tries)
        self.agent2_pos = pos

        if rand_dir:
            self.agent2_dir = self._rand_int(0, 4)

        return pos

    @property
    def dir_vec1(self):
        """
        Get the direction vector for the agent, pointing in the direction
        of forward movement.
        """

        assert (
            self.agent1_dir >= 0 and self.agent1_dir < 4
        ), f"Invalid agent_dir: {self.agent1_dir} is not within range(0, 4)"
        return DIR_TO_VEC[self.agent1_dir]

    @property
    def dir_vec2(self):
        """
        Get the direction vector for the agent, pointing in the direction
        of forward movement.
        """

        assert (
                self.agent2_dir >= 0 and self.agent2_dir < 4
        ), f"Invalid agent_dir: {self.agent2_dir} is not within range(0, 4)"
        return DIR_TO_VEC[self.agent2_dir]

    @property
    def right_vec1(self):
        """
        Get the vector pointing to the right of the agent.
        """

        dx, dy = self.dir_vec1
        return np.array((-dy, dx))

    @property
    def right_vec2(self):
        """
        Get the vector pointing to the right of the agent.
        """

        dx, dy = self.dir_vec2
        return np.array((-dy, dx))

    @property
    def front_pos1(self):
        """
        Get the position of the cell that is right in front of the agent
        """

        return self.agent1_pos + self.dir_vec1

    @property
    def front_pos2(self):
        """
        Get the position of the cell that is right in front of the agent
        """

        return self.agent2_pos + self.dir_vec2

    def get_view_coords(self, i, j):
        """
        Translate and rotate absolute grid coordinates (i, j) into the
        agent's partially observable view (sub-grid). Note that the resulting
        coordinates may be negative or outside of the agent's view size.
        """

        ax1, ay1 = self.agent1_pos
        dx1, dy1 = self.dir_vec1
        rx1, ry1 = self.right_vec1

        ax2, ay2 = self.agent2_pos
        dx2, dy2 = self.dir_vec2
        rx2, ry2 = self.right_vec2

        # Compute the absolute coordinates of the top-left view corner
        sz = self.agent_view_size
        hs = self.agent_view_size // 2
        tx1 = ax1 + (dx1 * (sz - 1)) - (rx1 * hs)
        ty1 = ay1 + (dy1 * (sz - 1)) - (ry1 * hs)
        tx2 = ax2 + (dx2 * (sz - 1)) - (rx2 * hs)
        ty2 = ay2 + (dy2 * (sz - 1)) - (ry2 * hs)

        lx1 = i - tx1
        ly1 = j - ty1
        lx2 = i - tx2
        ly2 = j - ty2

        # Project the coordinates of the object relative to the top-left
        # corner onto the agent's own coordinate system
        vx1 = rx1 * lx1 + ry1 * ly1
        vy1 = -(dx1 * lx1 + dy1 * ly1)

        vx2 = rx2 * lx2 + ry2 * ly2
        vy2 = -(dx2 * lx2 + dy2 * ly2)

        return vx1, vy1, vx2, vy2

    def get_view_exts(self, agent_view_size=None):
        """
        Get the extents of the square set of tiles visible to the agent
        Note: the bottom extent indices are not included in the set
        if agent_view_size is None, use self.agent_view_size
        """

        agent_view_size = agent_view_size or self.agent_view_size

        topX1 = self.agent1_pos[0] - agent_view_size // 2
        topY1 = self.agent1_pos[1] - agent_view_size // 2

        botX1 = topX1 + agent_view_size - agent_view_size // 2
        botY1 = topY1 + agent_view_size - agent_view_size // 2

        topX2 = self.agent2_pos[0] - agent_view_size // 2
        topY2 = self.agent2_pos[1] - agent_view_size // 2

        botX2 = topX2 + agent_view_size - agent_view_size // 2
        botY2 = topY2 + agent_view_size - agent_view_size // 2

        return (topX1, topY1, botX1, botY1, topX2, topY2, botX2, botY2)

    def relative_coords(self, x, y):
        """
        Check if a grid position belongs to the agent's field of view, and returns the corresponding coordinates
        """

        vx, vy = self.get_view_coords(x, y)

        if vx < 0 or vy < 0 or vx >= self.agent_view_size or vy >= self.agent_view_size:
            return None

        return vx, vy

    def in_view(self, x, y):
        """
        check if a grid position is visible to the agent
        """

        return self.relative_coords(x, y) is not None

    def agent_sees(self, x, y):
        """
        Check if a non-empty grid position is visible to the agent
        """

        coordinates = self.relative_coords(x, y)
        if coordinates is None:
            return False
        vx, vy = coordinates

        obs = self.gen_obs()

        obs_grid, _ = Grid.decode(obs["image"])
        obs_cell = obs_grid.get(vx, vy)
        world_cell = self.grid.get(x, y)

        assert world_cell is not None

        return obs_cell is not None and obs_cell.type == world_cell.type

    def stepN(self, action, agentN, reward):
        self.step_count += 1

        reward = 0
        terminated = False
        truncated = False

        if agentN == 1:
            agent_pos = self.agent1_pos
        elif agentN == 2:
            agent_pos = self.agent2_pos

        # Set next cell to the left
        if action == self.actions.left:
            # Get the contents of the cell in front of the agent
            fwd_pos = agent_pos + np.array([-1, 0])
            fwd_cell = self.grid.get(*fwd_pos)

        # Set next cell to the right
        elif action == self.actions.right:
            # Get the contents of the cell in front of the agent
            fwd_pos = agent_pos + np.array([1, 0])
            fwd_cell = self.grid.get(*fwd_pos)

        # Set next cell up
        elif action == self.actions.up:
            # Get the contents of the cell in front of the agent
            fwd_pos = agent_pos + np.array([0, -1])
            fwd_cell = self.grid.get(*fwd_pos)

        # Set next cell to down
        elif action == self.actions.down:
            # Get the contents of the cell in front of the agent
            fwd_pos = agent_pos + np.array([0, 1])
            fwd_cell = self.grid.get(*fwd_pos)

        # Stay in the same cell
        elif action == self.actions.stay:
            # Get the contents of the cell in front of the agent
            fwd_pos = agent_pos
            fwd_cell = self.grid.get(*fwd_pos)

        # Done action (not used by default)
        elif action == self.actions.done:
            pass

        else:
            raise ValueError(f"Unknown action: {action}")

        # Move robot
        if fwd_cell is None or fwd_cell.can_overlap():
            if agentN == 1:
                self.agent1_pos = tuple(fwd_pos)
            elif agentN == 2:
                self.agent2_pos = tuple(fwd_pos)

        if fwd_cell is not None and fwd_cell.type == "goal":
            terminated = True
            reward = self._reward()

        if self.step_count >= self.max_steps:
            truncated = True

        if self.render_mode == "human":
            self.render()

        obs = self.gen_obs()

        return obs, reward, terminated, truncated, {}

    def gen_obs_grid(self, agent_view_size=None):
        """
        Generate the sub-grid observed by the agent.
        This method also outputs a visibility mask telling us which grid
        cells the agent can actually see.
        if agent_view_size is None, self.agent_view_size is used
        """

        topX1, topY1, botX1, botY1, topX2, topY2, botX2, botY2 = self.get_view_exts(self.agent_view_size)

        agent_view_size = agent_view_size or self.agent_view_size

        grid1 = self.grid.slice(topX1, topY1, agent_view_size, agent_view_size)
        vis_mask1 = np.ones(shape=(grid1.width, grid1.height), dtype=bool)

        grid2 = self.grid.slice(topX2, topY2, agent_view_size, agent_view_size)
        vis_mask2 = np.ones(shape=(grid2.width, grid2.height), dtype=bool)

        return grid1, vis_mask1, grid2, vis_mask2

    def gen_obs(self):
        """
        Generate the agent's view (partially observable, low-resolution encoding)
        """

        grid1, vis_mask1, grid2, vis_mask2 = self.gen_obs_grid()

        obs = {"grid1": grid1.grid, "mask1": vis_mask1, "direction1": self.agent1_dir,
            "grid2": grid2.grid, "mask2": vis_mask2, "direction2": self.agent2_dir}

        return obs

    def get_pov_render(self, tile_size):
        """
        Render an agent's POV observation for visualization
        """
        grid, vis_mask = self.gen_obs_grid()

        # Render the whole grid
        img = grid.render(
            tile_size,
            agent_pos=(self.agent_view_size // 2, self.agent_view_size - 1),
            agent_dir=3,
            highlight_mask=vis_mask,
        )

        return img

    def get_full_render(self, highlight, tile_size):
        """
        Render a non-partial observation for visualization
        """
        # Compute which cells are visible to the agent
        grid1, vis_mask1, grid2, vis_mask2 = self.gen_obs_grid()

        # Compute the world coordinates of the bottom-left corner
        # of the agent's view area
        f_vec1 = self.dir_vec1
        f_vec2 = self.dir_vec2
        r_vec1 = self.right_vec1
        r_vec2 = self.right_vec2
        top_left1 = (
            self.agent1_pos
            + f_vec1 * (self.agent_view_size // 2)
            - r_vec1 * (self.agent_view_size // 2)
        )
        top_left2 = (
            self.agent2_pos
            + f_vec2 * (self.agent_view_size // 2)
            - r_vec2 * (self.agent_view_size // 2)
        )

        # Mask of which cells to highlight
        highlight_mask = np.zeros(shape=(self.width, self.height), dtype=bool)

        # For each cell in the visibility mask
        for vis_j in range(0, self.agent_view_size):
            for vis_i in range(0, self.agent_view_size):
                # If this cell is not visible, don't highlight it
                if not vis_mask1[vis_i, vis_j] and not vis_mask2[vis_i, vis_j]:
                    continue

                # Compute the world coordinates of this cell
                abs_i1, abs_j1 = top_left1 - (f_vec1 * vis_j) + (r_vec1 * vis_i)
                abs_i2, abs_j2 = top_left2 - (f_vec2 * vis_j) + (r_vec2 * vis_i)

                if (abs_i1 < 0 or abs_i1 >= self.width) and (abs_i2 < 0 or abs_i2 >= self.width):
                    continue
                if (abs_j1 < 0 or abs_j1 >= self.height) and (abs_j2 < 0 or abs_j2 >= self.height):
                    continue

                if (abs_i1 >= 0 and abs_i1 < self.width) and (abs_j1 >= 0 and abs_j1 < self.height):
                    # Mark this cell to be highlighted
                    highlight_mask[abs_i1, abs_j1] = True
                if (abs_i2 >= 0 and abs_i2 < self.width) and (abs_j2 >= 0 and abs_j2 < self.height):
                    # Mark this cell to be highlighted
                    highlight_mask[abs_i2, abs_j2] = True

        # Render the whole grid
        img = self.grid.render(
            tile_size,
            self.agent1_pos,
            self.agent2_pos,
            self.agent1_dir,
            self.agent2_dir,
            highlight_mask=highlight_mask if highlight else None
        )

        return img

    def get_frame(
        self,
        highlight: bool = True,
        tile_size: int = TILE_PIXELS,
        agent_pov: bool = False,
    ):
        """Returns an RGB image corresponding to the whole environment or the agent's point of view.

        Args:

            highlight (bool): If true, the agent's field of view or point of view is highlighted with a lighter gray color.
            tile_size (int): How many pixels will form a tile from the NxM grid.
            agent_pov (bool): If true, the rendered frame will only contain the point of view of the agent.

        Returns:

            frame (np.ndarray): A frame of type numpy.ndarray with shape (x, y, 3) representing RGB values for the x-by-y pixel image.

        """

        if agent_pov:
            return self.get_pov_render(tile_size)
        else:
            return self.get_full_render(highlight, tile_size)

    def render(self):

        img = self.get_frame(self.highlight, self.tile_size, self.agent_pov)

        if self.render_mode == "human":
            if self.window is None:
                self.window = Window("minigrid")
                self.window.show(block=False)
            self.window.set_caption(self.mission)
            self.window.show_img(img)
        elif self.render_mode == "rgb_array":
            return img

    def close(self):
        if self.window:
            self.window.close()
