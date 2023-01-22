from gymnasium.envs.registration import register

register(
     id="WarehouseEnv-v0",
     entry_point="warehouse.envs:WarehouseEnv",
     max_episode_steps=3000
)
