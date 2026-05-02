import numpy as np

from smds.scheduler.config import DQNConfig
from smds.scheduler.network import QNetwork
from smds.scheduler.replay_buffer import ReplayBuffer
from smds.scheduler.agent import DQNAgent


def test_q_network_forward():
    net = QNetwork(state_dim=67, action_dim=120)
    state = np.random.randn(67).astype(np.float32)
    import torch
    with torch.no_grad():
        q = net(torch.FloatTensor(state).unsqueeze(0))
    assert q.shape == (1, 120)


def test_replay_buffer_push_sample():
    buf = ReplayBuffer(capacity=100)
    for i in range(10):
        buf.push(np.zeros(67), i % 120, float(i), np.zeros(67), False)
    assert len(buf) == 10
    states, actions, rewards, next_states, dones = buf.sample(5)
    assert states.shape == (5, 67)
    assert actions.shape == (5,)
    assert rewards.shape == (5,)


def test_agent_epsilon_decay():
    config = DQNConfig(epsilon_start=1.0, epsilon_end=0.01, epsilon_decay_steps=100)
    agent = DQNAgent(config)
    eps_start = agent.epsilon()
    agent.step_count = 100
    eps_mid = agent.epsilon()
    agent.step_count = 10000
    eps_end = agent.epsilon()
    assert eps_start > eps_mid > eps_end
    assert abs(eps_end - 0.01) < 0.01


def test_agent_select_action_explore():
    config = DQNConfig(state_dim=67, action_dim=120)
    agent = DQNAgent(config)
    state = np.zeros(67, dtype=np.float32)
    actions = {agent.select_action(state, epsilon=1.0) for _ in range(100)}
    assert len(actions) > 1  # Should explore different actions


def test_agent_select_action_exploit():
    config = DQNConfig(state_dim=67, action_dim=120)
    agent = DQNAgent(config)
    state = np.zeros(67, dtype=np.float32)
    action1 = agent.select_action(state, epsilon=0.0)
    action2 = agent.select_action(state, epsilon=0.0)
    assert action1 == action2  # Greedy should be deterministic


def test_agent_train_step_insufficient_data():
    config = DQNConfig(state_dim=67, action_dim=120, min_replay_size=500)
    agent = DQNAgent(config)
    loss = agent.train_step()
    assert loss is None  # Not enough data


def test_agent_train_step_with_data():
    config = DQNConfig(state_dim=67, action_dim=120, min_replay_size=5, batch_size=5)
    agent = DQNAgent(config)
    for i in range(10):
        agent.replay.push(np.zeros(67, dtype=np.float32), 0, 1.0, np.zeros(67, dtype=np.float32), False)
    loss = agent.train_step()
    assert loss is not None
    assert loss >= 0
    assert agent.step_count == 1
