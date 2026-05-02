from dataclasses import dataclass


@dataclass
class DQNConfig:
    # Network
    state_dim: int = 67
    action_dim: int = 120  # 6 devices × 20 tasks
    hidden_dims: tuple = (128, 256, 256)
    dropout: float = 0.1

    # Training
    learning_rate: float = 5e-4
    gamma: float = 0.99
    batch_size: int = 64
    total_episodes: int = 50000
    max_steps_per_episode: int = 1000

    # Exploration
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay_steps: int = 2000

    # Replay
    replay_capacity: int = 10000
    min_replay_size: int = 500

    # Target network
    target_update_freq: int = 100  # steps

    # Logging
    log_freq: int = 100  # episodes
    save_freq: int = 1000  # episodes
