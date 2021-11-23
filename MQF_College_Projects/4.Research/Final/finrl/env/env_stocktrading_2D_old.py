import numpy as np
import pandas as pd
from gym.utils import seeding
import gym
from gym import spaces
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common import logger


class StockTradingEnv2D(gym.Env):
    """A stock trading environment for OpenAI gym. 
    State is 3D: [batch_size x seq_len x feature_size]. Currently the batch_size is 1.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df, stock_dim, hmax, initial_amount, buy_cost_pct, sell_cost_pct, 
                 action_space, tech_indicator_list, reward_scaling=1, reward_method='pnl',
                 stoploss_window=240, stoploss_factor=0.001, stoploss_pct=0.3, 
                 inactive_window=30, hmin=1, inactive_penalty_pct = 1e-5, 
                 turbulence_threshold=None, make_plots=False, print_verbosity=1, 
                 seq_len=30, day=29, initial=True, previous_state=[], model_name = '', mode='', iteration=''):
        self.df = df
        self.stock_dim = stock_dim
        self.hmax = hmax
        self.initial_amount = initial_amount
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.action_space = action_space
        self.tech_indicator_list = tech_indicator_list
        self.reward_scaling = reward_scaling
        self.reward_method = reward_method
        self.stoploss_window = stoploss_window
        self.stoploss_factor = stoploss_factor
        self.stoploss_pct = stoploss_pct
        self.inactive_window = inactive_window
        self.hmin = hmin
        self.inactive_penalty_pct = inactive_penalty_pct
        self.turbulence_threshold = turbulence_threshold
        self.make_plots = make_plots
        self.print_verbosity = print_verbosity
        self.seq_len = seq_len
        self.day = day
        self.initial = initial
        self.previous_state = previous_state
        self.model_name=model_name
        self.mode=mode 
        self.iteration=iteration
        
        # env
        self.action_space = spaces.Box(low = -1, high = 1,shape = (self.action_space,))
        # bal + (close, holding, TAs)*stock_dim
        self.state_space = 1 + (2 + len(self.tech_indicator_list)) * self.stock_dim
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape = (1, self.seq_len, self.state_space))
        self.data = self.df.loc[(self.day-self.seq_len-1):self.day,:]
        self.terminal = False     
  
        # initialize reward
        self.reward = 0
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0
        
        # history
        self.asset_memory = [self.initial_amount]
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        self.price_memory = []
        self.seed()
        
        # initalize state
        # state = [Balance, Closes, Holdings, TAs]
        self.state = self._initiate_state()
        
    def _sell_stock(self, index, action):
        def _do_sell_normal():
            if self.state[index+1]>0: 
                # Sell only if the price is > 0 (no missing data in this particular date)
                # perform sell action based on the sign of the action
                if self.state[index+self.stock_dim+1] > 0:
                    # Sell only if current asset is > 0
                    sell_num_shares = min(abs(action),self.state[index+self.stock_dim+1])
                    sell_amount = self.state[index+1] * sell_num_shares * (1- self.sell_cost_pct)
                    #update balance
                    self.state[0] += sell_amount
                    self.state[index+self.stock_dim+1] -= sell_num_shares
                    self.cost +=self.state[index+1] * sell_num_shares * self.sell_cost_pct
                    self.trades+=1
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = 0
            return sell_num_shares
            
        # perform sell action based on the sign of the action
        if self.turbulence_threshold is not None:
            if self.turbulence>=self.turbulence_threshold:
                if self.state[index+1]>0: 
                    # Sell only if the price is > 0 (no missing data in this particular date)
                    # if turbulence goes over threshold, just clear out all positions 
                    if self.state[index+self.stock_dim+1] > 0:
                        # Sell only if current asset is > 0
                        sell_num_shares = self.state[index+self.stock_dim+1]
                        sell_amount = self.state[index+1] * sell_num_shares * (1- self.sell_cost_pct)
                        #update balance
                        self.state[0] += sell_amount
                        self.state[index+self.stock_dim+1] =0
                        self.cost += self.state[index+1] * self.state[index+self.stock_dim+1] * self.sell_cost_pct
                        self.trades+=1
                    else:
                        sell_num_shares = 0
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = _do_sell_normal()
        else:
            sell_num_shares = _do_sell_normal()
        return sell_num_shares

    
    def _buy_stock(self, index, action):
        def _do_buy():
            if self.state[index+1]>0: 
                #Buy only if the price is > 0 (no missing data in this particular date)       
                available_amount = self.state[0] // self.state[index+1]
                #update balance
                buy_num_shares = min(available_amount, action)
                buy_amount = self.state[index+1] * buy_num_shares * (1+ self.buy_cost_pct)
                self.state[0] -= buy_amount
                self.state[index+self.stock_dim+1] += buy_num_shares
                self.cost+=self.state[index+1] * buy_num_shares * self.buy_cost_pct
                self.trades+=1
            else:
                buy_num_shares = 0
            return buy_num_shares
        # perform buy action based on the sign of the action
        if self.turbulence_threshold is None:
            buy_num_shares = _do_buy()
        else:
            if self.turbulence< self.turbulence_threshold:
                buy_num_shares = _do_buy()
            else:
                buy_num_shares = 0
        return buy_num_shares

    def _make_plot(self):
        plt.plot(self.asset_memory,'r')
        plt.savefig('results/account_value_trade_{}.png'.format(self.episode))
        plt.close()

    def step(self, actions):
        self.terminal = self.day >= len(self.df.index.unique())-1
        if self.terminal:
            if self.make_plots:
                self._make_plot()            
            end_total_asset = (self.state[0]+
                               sum(np.array(self.state[1:(self.stock_dim+1)])*
                                   np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
                              )
            df_total_value = pd.DataFrame(self.asset_memory)
            tot_reward = self.state[0]+sum(np.array(self.state[1:(self.stock_dim+1)])*
                                           np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))- self.initial_amount 
            df_total_value.columns = ['account_value']
            df_total_value['date'] = self.date_memory
            df_total_value['daily_return']=df_total_value['account_value'].pct_change(1)
            if df_total_value['daily_return'].std() !=0:
                sharpe = (252**0.5) * df_total_value['daily_return'].mean() / df_total_value['daily_return'].std()
            df_rewards = pd.DataFrame(self.rewards_memory)
            df_rewards.columns = ['account_rewards']
            df_rewards['date'] = self.date_memory[:-1]
            print('Episode:', self.episode)
            print(self.episode % self.print_verbosity)
            if self.episode % self.print_verbosity == 0:
                print("=================================")
                print(f"day: {self.day}, episode: {self.episode}")
                print(f"begin_total_asset: {self.asset_memory[0]:0.2f}")
                print(f"end_total_asset: {end_total_asset:0.2f}")
                print(f"total_reward: {tot_reward:0.2f}")
                print(f"total_cost: {self.cost:0.2f}")
                print(f"total_trades: {self.trades}")
                if df_total_value['daily_return'].std() != 0:
                    print(f"Sharpe: {sharpe:0.3f}")
                print("=================================")

            if (self.model_name!='') and (self.mode!=''):
                df_actions = self.save_action_memory()
                df_actions.to_csv('results/actions_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration))
                df_total_value.to_csv('results/account_value_{}_{}_{}.csv'.format(self.mode,
                                                                                  self.model_name, 
                                                                                  self.iteration),index=False)
                df_rewards.to_csv('results/account_rewards_{}_{}_{}.csv'.format(self.mode,
                                                                                self.model_name, 
                                                                                self.iteration),index=False)
                plt.plot(self.asset_memory,'r')
                plt.savefig('results/account_value_{}_{}_{}.png'.format(self.mode,
                                                                        self.model_name, 
                                                                        self.iteration),index=False)
                plt.close()

            # Add outputs to logger interface
            logger.record("environment/portfolio_value", end_total_asset)
            logger.record("environment/total_reward", tot_reward)
            logger.record("environment/total_reward_pct", (tot_reward / (end_total_asset - tot_reward)) * 100)
            logger.record("environment/total_cost", self.cost)
            logger.record("environment/total_trades", self.trades)
            return self.state, self.reward, self.terminal, {}
        else:
            actions = actions * self.hmax #actions initially is scaled between 0 to 1
            actions = (actions.astype(int)) #convert into integer because we can't by fraction of shares
            if self.turbulence_threshold is not None:
                if self.turbulence>=self.turbulence_threshold:
                    actions=np.array([-self.hmax]*self.stock_dim)
                    
            begin_total_asset = (self.state[0]+ 
                                 sum(np.array(self.state[1:(self.stock_dim+1)])*
                                     np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
                                )
            argsort_actions = np.argsort(actions)
            
            sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]
            for index in sell_index:
                actions[index] = self._sell_stock(index, actions[index]) * (-1)
            for index in buy_index:
                actions[index] = self._buy_stock(index, actions[index])
            self.actions_memory.append(actions)

            self.day += 1
            self.data = self.df.loc[(self.day-self.seq_len-1):self.day,:]    
            if self.turbulence_threshold is not None:
                if self.stock_dim == 1:
                    self.turbulence = self.data['turbulence']
                else:
                    self.turbulence = self.data['turbulence'].values[0]
            prev_holdings = self.state[(self.stock_dim+1):(self.stock_dim*2+1)]
            self.state =  self._update_state()
                           
            # balance_{i+1} = balance_i - C_{i+1}*delta_N_{i}
            # begin_total_asset = balance_{i} + N_{i}*C_{i}
            # end_total_asset = balance_{i+1} + N_{i+1}*C_{i+1}
            # reward = N_{i+1}*C_{i+1} - N_{i}*C_{i} - C_{i+1}*(N_{i+1} - N_{i}) = N_{i}(C_{i} - C_{i+1})
            end_total_asset = (self.state[0]+ 
                               sum(np.array(self.state[1:(self.stock_dim+1)])*
                                   np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
                              )
            # Penalize for not trading: if actions < hmin during a interval inactive_window for stock_i,
            # we decrease reward by holding_cash_penality. Similar to discounting.
            # inactive_penalty = balance*inactive_penalty_pct
#             if len(self.actions_memory) >= self.inactive_window:
#                 inactive_cnt = 0
#                 inactive_penalty = 0
#                 penalize = True
#                 for past_actions in self.actions_memory[-self.inactive_window:]:
#                     for a in past_actions:
#                         if a != 0:                      
#                             penalize = False
#                             break
#                 if penalize:
#                     inactive_penalty = self.state[0] * self.inactive_penalty_pct
# #                     print(f'Penalize {inactive_penalty} due to inactive behavior')
                    
            self.asset_memory.append(end_total_asset)
            self.date_memory.append(self._get_date())
            if self.reward_method == 'end_total_asset':
                self.reward = end_total_asset - self.initial_amount
                
            elif self.reward_method == 'pnl':
                self.reward = end_total_asset - begin_total_asset
                
            elif self.reward_method == 'stoploss_avg':
                stoploss_penalty = 0
                # if close < mean_price-2*std_price
                # stop_loss_penalty = - stop_loss_factor * (close - avg_buy)*holding
                if self.day > self.stoploss_window:
                    price_df = self.df[self.df.index < self.day].groupby('tic')['close'][:self.stoploss_window]
                    mean_price = price_df.mean().values
                    std_price = price_df.std().values
                    diff = np.array(self.state[1:(self.stock_dim+1)]) - mean_price + 2*std_price
                    neg_diff = np.clip(diff, -np.inf, 0) - 2*std_price
                    stoploss_penalty = -1 * np.dot(np.array(prev_holdings), neg_diff)
                self.reward = end_total_asset - self.initial_amount - self.stoploss_factor*stoploss_penalty
                
            elif self.reward_method == 'stoploss_pct':
                stoploss_penalty = 0
                if self.day > self.stoploss_window:
                    # penalize if price drop below s% of last peak
                    last_peak = self._find_last_peak()
                    diff = np.array(self.price_memory[-1]) - np.array(last_peak)*(1-self.stoploss_pct)
                    neg_diff = np.clip(diff, -np.inf, 0)
                    stoploss_penalty = -1 * np.dot(np.array(prev_holdings), neg_diff)
                self.reward = end_total_asset - self.initial_amount - self.stoploss_factor*stoploss_penalty
               
            self.reward = self.reward / self.initial_amount
            self.rewards_memory.append(self.reward)
            
        return self.state, self.reward, self.terminal, {}

    def reset(self):  
        #initiate state
        self.state = self._initiate_state()
        
        if self.initial:
            self.asset_memory = [self.initial_amount]
        else:
            previous_total_asset = (self.previous_state[0]+ 
                                    sum(np.array(self.state[1:(self.stock_dim+1)])*
                                        np.array(self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]))
                                   )
            self.asset_memory = [previous_total_asset]

        self.day = self.seq_len - 1
        self.data = self.df.loc[(self.day-self.seq_len+1):self.day,:] 
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.terminal = False 
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        self.episode+=1
        return self.state
    
    def render(self, mode='human',close=False):
        return self.state

    def _initiate_state(self):
        if self.initial:
            # For Initial State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                states = []
                for i in self.data.index:
                    data = self.data.loc[i]
                    s = (
                        [self.initial_amount] + data.close.values.tolist() + [0]*self.stock_dim +
                        sum([data[tech].values.tolist() for tech in self.tech_indicator_list], [])
                    )
                    states.append(s)
                state = np.vstack(states)
            else:
                # for single stock
                states = []
                for i in self.data.index:
                    data = self.data.loc[i]
                    s = (
                        [self.initial_amount]+[data.close] + [0]+
                        sum([[data[tech]] for tech in self.tech_indicator_list ], [])
                    )
                    states.append(s)
                state = np.vstack(states)
        else:
            #Using Previous State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                prev_states = self.state[1:]
                last_state = self.state[-1]
                data = self.data.loc[seq_len-1]
                curr_state = (
                    last_state[0] + data.close.values.tolist() + 
                    list(last_state[(self.stock_dim+1):(self.stock_dim*2+1)]) +
                    sum([data[tech].values.tolist() for tech in self.tech_indicator_list], [])
                )
                state = np.vstack([prev_states, curr_state])
            else:
                # for single stock
                state = (
                    [self.previous_state[0]] +
                    [self.data.close] +
                    list(self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]) +
                    sum([[self.data[tech]] for tech in self.tech_indicator_list], [])
                )
                
        self.price_memory.append(state[1:(self.stock_dim+1)])
                
        return np.array(state)

    def _update_state(self):
        if len(self.df.tic.unique())>1:
            # for multiple stock
            state =  [self.state[0]] + \
                      self.data.close.values.tolist() + \
                      list(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]) + \
                      sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])

        else:
            # for single stock
            state =  [self.state[0]] + \
                     [self.data.close] + \
                     list(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]) + \
                     sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
            
        self.price_memory.append(state[1:(self.stock_dim+1)])
        # only cache the last 4 hours data
        if len(self.price_memory) > 240:
            self.price_memory = self.price_memory[-240:]
        return np.array(state)

    def _get_date(self):
        if len(self.df.tic.unique())>1:
            date = self.data.date.unique()[0]
        else:
            date = self.data.date
        return date

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs