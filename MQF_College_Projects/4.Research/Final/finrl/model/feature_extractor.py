import gym
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Type, Union
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.utils import get_device
from itertools import zip_longest

    
class MLPExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Box, 
                 features_dim,
                 net_arch: List[Union[int, Dict[str, List[int]]]] = [64, 64],
                 activation_fn: Type[nn.Module] = torch.nn.ReLU,
                 device: Union[torch.device, str] = "auto"
                ):
        super(MLPExtractor, self).__init__(observation_space, features_dim)
        n_input_channels = observation_space.shape[0]
        self.layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(n_input_channels, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim)
        )

    def forward(self, x):
        return self.layers(x)


class LstmExtractor(BaseFeaturesExtractor):
    """
    :param observation_space: (gym.Space)
    :param features_dim: (int) Number of features extracted.
        This corresponds to the number of unit for the last layer.
    """
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 16,
                 hidden_dim=32, num_layers=1, dropout=0.5):
        super(LstmExtractor, self).__init__(observation_space, features_dim)
        input_dim = observation_space.shape[1]
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # lstm
        self.lstm1 = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.lstm2 = nn.LSTM(hidden_dim, hidden_dim, num_layers, batch_first=True)
        
        # dropout
        self.dropout = nn.Dropout(dropout)

        # dense
        self.fc = nn.Sequential(nn.Linear(hidden_dim, features_dim), nn.ReLU())

    def forward(self, x):
        # Initial states
        h1, c1, h2, c2 = self._initial_state(x)
        lstm_out, (hn, cn) = self.lstm1(x, (h1.detach(), c1.detach()))
        lstm_out = self.dropout(lstm_out)
        lstm_out, (hn, cn) = self.lstm2(lstm_out, (h2.detach(), c2.detach()))
        out = self.dropout(lstm_out)
        lstm_out = lstm_out.contiguous().view(-1, self.hidden_dim)
        out = self.fc(lstm_out) # [batch x seq_len x output_dim]
        return out[-1, :]
    
    def _initial_state(self, x):
        h1 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        c1 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        h2 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        c2 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        
        torch.nn.init.xavier_normal_(h1)
        torch.nn.init.xavier_normal_(c1)
        torch.nn.init.xavier_normal_(h2)
        torch.nn.init.xavier_normal_(c2)
        return h1, c1, h2, c2