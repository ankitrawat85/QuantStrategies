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
    """A stock trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self, df, stock_dim, hmax, initial_amount, buy_cost_pct, sell_cost_pct, 
                 state_space, action_space, tech_indicator_list, reward_scaling=1, reward_method='pnl',
                 stoploss_window=240, stoploss_factor=0.001, stoploss_pct=0.3, 
                 inactive_window=30, hmin=1, inactive_penalty_pct = 1e-5, 
                 turbulence_threshold=None, make_plots=False, print_verbosity=1, 
                 seq_len = 30, day=29, initial=True, previous_state=[], model_name = '', mode='', iteration=''):
        self.df = df
        self.stock_dim = stock_dim
        self.hmax = hmax
        self.initial_amount = initial_amount
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.state_space = state_space
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
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape = (self.seq_len, self.state_space))
        self.data = self.df.loc[self.day,:]
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
        self.state_memory = []
        self.seed()
        
        # initalize state
        # state = [Balance, Closes, Holdings, TAs]
        self.state = self._initiate_state()
        self._init_state_memory()
        
        
    def _init_state_memory(self):
        for d in range(0, self.day):
            data = self.df.loc[d]
            if self.stock_dim > 1:
                # for multiple stock
                s = (
                    [self.initial_amount] + data.close.values.tolist() + [0]*self.stock_dim +
                    sum([data[tech].values.tolist() for tech in self.tech_indicator_list], [])
                )
                
            else:
                # for single stock
                s = (
                    [self.initial_amount]+[data.close] + [0]+
                    sum([[data[tech]] for tech in self.tech_indicator_list ], [])
                )
            self.state_memory.append(s)
            
        
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
            if self.stock_dim == 1:
                actions = np.array([actions])
            argsort_actions = np.argsort(actions)
            sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]
            for index in sell_index:
                actions[index] = self._sell_stock(index, actions[index]) * (-1)
            for index in buy_index:
                actions[index] = self._buy_stock(index, actions[index])
            self.actions_memory.append(actions)

            self.day += 1
            self.data = self.df.loc[self.day,:]    
            if self.turbulence_threshold is not None:
                if self.stock_dim == 1:
                    self.turbulence = self.data['turbulence']
                else:
                    self.turbulence = self.data['turbulence'].values[0]
            prev_holdings = self.state[(self.stock_dim+1):(self.stock_dim*2+1)]
            self.state =  self._update_state()
            end_total_asset = (self.state[0]+ 
                               sum(np.array(self.state[1:(self.stock_dim+1)])*
                                   np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
                              )
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
                    prev_price = np.vstack(self.price_memory[:self.stoploss_window])
                    mean_price = prev_price.mean(axis=0)
                    std_price = prev_price.std(axis=0)
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
               
            self.reward = self.reward * self.reward_scaling
            self.rewards_memory.append(self.reward)
        return_state = np.vstack([self.state_memory[-self.seq_len+1:], self.state])
        # return_state = return_state[np.newaxis, ...]
        
        if self.day % 2000 == 0:
            print('===================================')
            print('Current balance:', self.state[0])
            print('Current holding:', self.state[(self.stock_dim+1):(self.stock_dim*2+1)])
            print('Current total reward:', end_total_asset - self.initial_amount)
            print('===================================')
        if self.day % 200000 == 0:
            plt.plot(self.asset_memory,'r')
        return return_state, self.reward, self.terminal, {}

    
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

        self.day = self.seq_len-1
#         self.day = int(np.random.sample(1)*(len(self.df.index.unique())-1))
        self.data = self.df.loc[self.day,:]
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.terminal = False 
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        self.episode+=1
        return_state = np.vstack([self.state_memory[-self.seq_len+1:], self.state])
        return return_state
    
    def render(self, mode='human',close=False):
        return_state = np.vstack([self.state_memory[-self.seq_len+1:], self.state])
        return return_state

    def _initiate_state(self):
        if self.initial:
            # For Initial State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                state = [self.initial_amount] + \
                         self.data.close.values.tolist() + \
                         [0]*self.stock_dim  + \
                         sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])
            else:
                # for single stock
                state = [self.initial_amount] + \
                        [self.data.close] + \
                        [0]*self.stock_dim  + \
                        sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
        else:
            #Using Previous State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                state = (
                    [self.previous_state[0]] +
                    self.data.close.values.tolist() +
                    self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]  +
                    sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])
                )
            else:
                # for single stock
                state = (
                    [self.previous_state[0]] +
                    [self.data.close] +
                    list(self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]) +
                    sum([[self.data[tech]] for tech in self.tech_indicator_list], [])
                )
                
        self.price_memory.append(state[1:(self.stock_dim+1)])
        self.state_memory.append(state)
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
        self.state_memory.append(state)
        return np.array(state)
        
    def _find_last_peak(self):
        if len(self.price_memory) == 1:
            return [0]*self.len(self.state[1:(self.stock_dim+1)])

        prev_closes = list(zip(*self.price_memory))
        last_peak = self.state[1:(self.stock_dim+1)]
        # for close prices of asset i
        for i, closes in enumerate(prev_closes):
            last_peak[i] = self._find_peak(closes, last_peak[i])
        return last_peak
    
    def _find_peak(self, arr, curr):
        n = len(arr)
        # first or last element is peak element
        if (n == 1):
            return curr
        if (arr[n-1] >= arr[n-2]) & (arr[n-1] >= curr):
            return arr[n-1]

        # check for every other element
        for i, a in enumerate(arr[::-1]):
            # check if the neighbors are smaller
            if (a >= arr[i-1]) & (a >= arr[i+1]):
                return a
        return curr

    def _get_date(self):
        if len(self.df.tic.unique())>1:
            date = self.data.date.unique()[0]
        else:
            date = self.data.date
        return date

    def save_asset_memory(self):
        date_list = self.date_memory
        asset_list = self.asset_memory
        df_account_value = pd.DataFrame({'date':date_list,'account_value':asset_list})
        return df_account_value

    def save_action_memory(self):
        if len(self.df.tic.unique())>1:
            # date and close price length must match actions length
            date_list = self.date_memory[:-1]
            df_date = pd.DataFrame(date_list)
            df_date.columns = ['date']
            
            action_list = self.actions_memory
            df_actions = pd.DataFrame(action_list)
            df_actions.columns = self.data.tic.values
            df_actions.index = df_date.date
            #df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        else:
            date_list = self.date_memory[:-1]
            action_list = self.actions_memory
            df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        return df_actions

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs