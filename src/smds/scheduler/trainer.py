import time
from typing import Optional

import numpy as np

from .agent import DQNAgent
from .config import DQNConfig
from ..digital_twin.cnc_twin import CNCTwin
from ..digital_twin.robot_twin import RobotTwin
from ..digital_twin.agv_twin import AGVTwin
from ..digital_twin.warehouse_twin import WarehouseTwin
from ..digital_twin.manager import DigitalTwinManager
from ..digital_twin.manufacturing_env import ManufacturingEnv
from ..digital_twin.order_manager import OrderManager
from ..digital_twin.reward_calculator import RewardCalculator


def create_env() -> ManufacturingEnv:
    dt = DigitalTwinManager()
    dt.register(CNCTwin("CNC-001", "ns=2;s=CNC-001"))
    dt.register(CNCTwin("CNC-002", "ns=2;s=CNC-002"))
    dt.register(CNCTwin("CNC-003", "ns=2;s=CNC-003"))
    dt.register(RobotTwin("ROB-001", "ns=2;s=ROB-001"))
    dt.register(RobotTwin("ROB-002", "ns=2;s=ROB-002"))
    dt.register(AGVTwin("AGV-001", "ns=2;s=AGV-001"))
    dt.register(WarehouseTwin("WH-001", "ns=2;s=WH-001"))
    return ManufacturingEnv(dt, OrderManager(), RewardCalculator())


class Trainer:
    def __init__(self, config: Optional[DQNConfig] = None, device: Optional[str] = None):
        self.config = config or DQNConfig()
        self.agent = DQNAgent(self.config, device)
        self.env = create_env()
        self.episode_rewards: list = []
        self.episode_lengths: list = []
        self.losses: list = []

    def train(self, total_episodes: Optional[int] = None):
        n_episodes = total_episodes or self.config.total_episodes
        print(f"Training Double DQN for {n_episodes} episodes")
        print(f"  Device: {self.agent.device}")
        print(f"  State dim: {self.config.state_dim}, Action dim: {self.config.action_dim}")
        print(f"  Epsilon: {self.config.epsilon_start} -> {self.config.epsilon_end}")
        print()

        t_start = time.time()

        for episode in range(1, n_episodes + 1):
            state = self.env.reset()
            total_reward = 0.0
            loss_sum = 0.0
            loss_count = 0

            for step in range(self.config.max_steps_per_episode):
                action = self.agent.select_action(state)
                next_state, reward, done, info = self.env.step(action)

                self.agent.replay.push(state, action, reward, next_state, done)
                loss = self.agent.train_step()

                if loss is not None:
                    loss_sum += loss
                    loss_count += 1

                total_reward += reward
                state = next_state

                if done:
                    break

            self.episode_rewards.append(total_reward)
            self.episode_lengths.append(step + 1)
            if loss_count > 0:
                self.losses.append(loss_sum / loss_count)

            if episode % self.config.log_freq == 0:
                elapsed = time.time() - t_start
                avg_reward = np.mean(self.episode_rewards[-self.config.log_freq:])
                avg_length = np.mean(self.episode_lengths[-self.config.log_freq:])
                avg_loss = np.mean(self.losses[-self.config.log_freq:]) if self.losses else 0
                eps = self.agent.epsilon()
                print(
                    f"Ep {episode:>6d} | "
                    f"Reward {avg_reward:>8.2f} | "
                    f"Length {avg_length:>6.1f} | "
                    f"Loss {avg_loss:>8.4f} | "
                    f"Eps {eps:.4f} | "
                    f"Steps {self.agent.step_count:>7d} | "
                    f"Time {elapsed:.1f}s"
                )

            if episode % self.config.save_freq == 0:
                self.agent.save(f"dqn_checkpoint_ep{episode}.pt")
                print(f"  Saved checkpoint: dqn_checkpoint_ep{episode}.pt")

        print(f"\nTraining complete. Total time: {time.time() - t_start:.1f}s")
        self.agent.save("dqn_final.pt")
        print("Saved final model: dqn_final.pt")

    def evaluate(self, n_episodes: int = 10) -> dict:
        rewards = []
        lengths = []
        for _ in range(n_episodes):
            state = self.env.reset()
            total_reward = 0.0
            for step in range(self.config.max_steps_per_episode):
                action = self.agent.select_action(state, epsilon=0.0)
                next_state, reward, done, info = self.env.step(action)
                total_reward += reward
                state = next_state
                if done:
                    break
            rewards.append(total_reward)
            lengths.append(step + 1)
        return {
            "mean_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "mean_length": np.mean(lengths),
        }
