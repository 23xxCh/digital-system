import torch
import torch.nn as nn


class QNetwork(nn.Module):
    def __init__(self, state_dim: int = 67, action_dim: int = 120, hidden_dims: tuple = (128, 256, 256), dropout: float = 0.1):
        super().__init__()
        layers = []
        prev_dim = state_dim
        for h_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, h_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
            ])
            prev_dim = h_dim
        layers.append(nn.Linear(prev_dim, action_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.net(state)
