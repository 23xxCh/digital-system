import math
import random
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .config import DQNConfig
from .network import QNetwork
from .replay_buffer import ReplayBuffer


class DQNAgent:
    def __init__(self, config: Optional[DQNConfig] = None, device: Optional[str] = None):
        self.config = config or DQNConfig()
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        self.q_main = QNetwork(
            self.config.state_dim, self.config.action_dim,
            self.config.hidden_dims, self.config.dropout,
        ).to(self.device)

        self.q_target = QNetwork(
            self.config.state_dim, self.config.action_dim,
            self.config.hidden_dims, self.config.dropout,
        ).to(self.device)
        self.q_target.load_state_dict(self.q_main.state_dict())
        self.q_target.eval()

        self.optimizer = optim.Adam(self.q_main.parameters(), lr=self.config.learning_rate)
        self.replay = ReplayBuffer(self.config.replay_capacity)
        self.step_count = 0

    def epsilon(self) -> float:
        return self.config.epsilon_end + (
            self.config.epsilon_start - self.config.epsilon_end
        ) * math.exp(-self.step_count / self.config.epsilon_decay_steps)

    def select_action(self, state: np.ndarray, epsilon: Optional[float] = None) -> int:
        eps = epsilon if epsilon is not None else self.epsilon()
        if random.random() < eps:
            return random.randrange(self.config.action_dim)
        with torch.no_grad():
            state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_main(state_t)
            return q_values.argmax(dim=1).item()

    def train_step(self) -> Optional[float]:
        if len(self.replay) < self.config.min_replay_size:
            return None

        states, actions, rewards, next_states, dones = self.replay.sample(self.config.batch_size)

        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).to(self.device)
        rewards_t = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).to(self.device)

        # Current Q values
        q_values = self.q_main(states_t)
        q_current = q_values.gather(1, actions_t.unsqueeze(1)).squeeze(1)

        # Double DQN: main network selects action, target network evaluates
        with torch.no_grad():
            next_actions = self.q_main(next_states_t).argmax(dim=1)
            q_next = self.q_target(next_states_t).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            q_target = rewards_t + self.config.gamma * q_next * (1 - dones_t)

        loss = nn.MSELoss()(q_current, q_target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.step_count += 1
        if self.step_count % self.config.target_update_freq == 0:
            self.q_target.load_state_dict(self.q_main.state_dict())

        return loss.item()

    def save(self, path: str):
        torch.save({
            "q_main": self.q_main.state_dict(),
            "q_target": self.q_target.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "step_count": self.step_count,
        }, path)

    def load(self, path: str):
        checkpoint = torch.load(path, map_location=self.device, weights_only=True)
        self.q_main.load_state_dict(checkpoint["q_main"])
        self.q_target.load_state_dict(checkpoint["q_target"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.step_count = checkpoint["step_count"]
