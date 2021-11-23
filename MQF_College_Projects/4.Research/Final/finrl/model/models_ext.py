# common library
import operator
from tqdm import tqdm
import pandas as pd
import numpy as np
import time
import gym
import multiprocessing

# RL models from stable-baselines
# from stable_baselines.ppo2 import PPO2
# from stable_baselines.ppo1 import PPO1
from stable_baselines import A2C, ACKTR, PPO2, PPO1, TRPO, TD3, SAC, DQN, DDPG
from stable_baselines3.ppo import PPO
from stable_baselines3.td3 import TD3
from stable_baselines.common.policies import MlpLnLstmPolicy, MlpPolicy, MlpLstmPolicy
from stable_baselines.common.policies import CnnLstmPolicy, CnnLnLstmPolicy, CnnPolicy
from stable_baselines.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise, AdaptiveParamNoiseSpec
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines.common.cmd_util import make_vec_env
from stable_baselines.common.env_checker import check_env


# local
from finrl.config import config
from finrl.preprocessing.data import data_split
from finrl.env.env_stocktrading import StockTradingEnv

MODELS = {"a2c": A2C, "ddpg": DDPG, "sac": SAC, 'ppo1':PPO1, 'ppo2':PPO2, 'ppo':PPO, 'TD3':TD3}

MODEL_KWARGS = {x: config.__dict__[f"{x.upper()}_PARAMS"] for x in MODELS.keys()}

NOISE = {
    "normal": NormalActionNoise,
    "ornstein_uhlenbeck": OrnsteinUhlenbeckActionNoise,
}


############################################# SINGLE MODEL ################################################
class DRLAgent:
    """Provides implementations for DRL algorithms

    Attributes
    ----------
        env: gym environment class
            user-defined class

    Methods
    -------
        train_PPO()
            the implementation for PPO algorithm
        train_A2C()
            the implementation for A2C algorithm
        train_DDPG()
            the implementation for DDPG algorithm
        train_TD3()
            the implementation for TD3 algorithm
        train_SAC()
            the implementation for SAC algorithm
        DRL_prediction()
            make a prediction in a test dataset and get results
    """

    @staticmethod
    def DRL_prediction(model, environment):
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                account_memory = test_env.env_method(method_name="save_asset_memory")
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return account_memory[0], actions_memory[0]

    def __init__(self, env):
        self.env = env

    def get_model(
        self,
        model_name,
        policy="MlpPolicy",
        policy_kwargs=None,
        model_kwargs=None,
        verbose=1,
    ):
        if model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if model_kwargs is None:
            model_kwargs = MODEL_KWARGS[model_name]

        if "action_noise" in model_kwargs:
            n_actions = self.env.action_space.shape[-1]
            model_kwargs["action_noise"] = NOISE[model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.5 * np.ones(n_actions)
            )

        print(model_kwargs)
        model = MODELS[model_name](
            policy=policy,
            env=self.env,
            tensorboard_log=f"{config.TENSORBOARD_LOG_DIR}/{model_name}",
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **model_kwargs,
        )
        return model

    def train_model(self, model, tb_log_name, total_timesteps=5000):
        model = model.learn(total_timesteps=total_timesteps, tb_log_name=tb_log_name)
        return model
    
    
############################################# ENSEMBLE ################################################


class DRLEnsembleAgent:
    @staticmethod
    def get_model(model_name, env, policy="MlpPolicy", policy_kwargs=None, model_kwargs=None, verbose=1):
        if model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")
        if model_kwargs is None:
            temp_model_kwargs = MODEL_KWARGS[model_name]
        else:
            temp_model_kwargs = model_kwargs.copy()
        if "action_noise" in temp_model_kwargs:
            n_actions = env.action_space.shape[-1]
            temp_model_kwargs["action_noise"] = NOISE[temp_model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions)
            )
        print(temp_model_kwargs)
        model = MODELS[model_name](
            policy=policy,
            env=env,
            tensorboard_log=f"{config.TENSORBOARD_LOG_DIR}/{model_name}",
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **temp_model_kwargs,
        )
        return model

    @staticmethod
    def train_model(model, model_name, tb_log_name, iter_num, total_timesteps=5000):
        model = model.learn(total_timesteps=total_timesteps, tb_log_name=tb_log_name)
        model.save(f"{config.TRAINED_MODEL_DIR}/{model_name.upper()}_{total_timesteps//1000}k_{iter_num}")
        return model

    @staticmethod
    def get_validation_sharpe(iteration, model_name):
        ###Calculate Sharpe ratio based on validation results###
        df_total_value = pd.read_csv('results/account_value_validation_{}_{}.csv'.format(model_name,iteration))
        sharpe = (4 ** 0.5) * df_total_value['daily_return'].mean() / df_total_value['daily_return'].std()
        return sharpe

    def __init__(self,df,
                train_period,
                val_test_period,
                test_period,
                rebalance_window, validation_window,
                stock_dim,
                hmax,                
                initial_amount,
                buy_cost_pct,
                sell_cost_pct,
                reward_scaling,
                state_space,
                action_space,
                tech_indicator_list,
                print_verbosity):

        self.df=df
        self.train_period = train_period
        self.val_test_period = val_test_period
        self.test_period = test_period

        self.unique_trade_date = df[(df.date > val_test_period[0])&(df.date <= val_test_period[1])].date.unique()
        self.rebalance_window = rebalance_window
        self.validation_window = validation_window

        self.stock_dim = stock_dim
        self.hmax = hmax
        self.initial_amount = initial_amount
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.reward_scaling = reward_scaling
        self.state_space = state_space
        self.action_space = action_space
        self.tech_indicator_list = tech_indicator_list
        self.print_verbosity = print_verbosity


    def DRL_validation(self, model, test_data, test_env, test_obs):
        ###validation process###
        for i in range(len(test_data.index.unique())):
            action, _states = model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)

    def DRL_prediction(self, model, name, last_state, iter_num, turbulence_threshold, initial):
        ### make a prediction based on trained model###

        ## trading env
        trade_data = data_split(self.df, 
                                start=self.unique_trade_date[iter_num - self.rebalance_window],
                                end=self.unique_trade_date[iter_num])
        trade_env = DummyVecEnv([lambda: StockTradingEnv(trade_data,
                                                        self.stock_dim,
                                                        self.hmax,
                                                        self.initial_amount,
                                                        self.buy_cost_pct,
                                                        self.sell_cost_pct,
                                                        self.reward_scaling,
                                                        self.state_space,
                                                        self.action_space,
                                                        self.tech_indicator_list,
                                                        turbulence_threshold=turbulence_threshold,
                                                        initial=initial,
                                                        previous_state=last_state,
                                                        model_name=name,
                                                        mode='trade',
                                                        iteration=iter_num,
                                                        print_verbosity=self.print_verbosity)])

        trade_obs = trade_env.reset()

        for i in range(len(trade_data.index.unique())):
            action, _states = model.predict(trade_obs)
            trade_obs, rewards, dones, info = trade_env.step(action)
            if i == (len(trade_data.index.unique()) - 2):
                # print(env_test.render())
                last_state = trade_env.render()

        df_last_state = pd.DataFrame({'last_state': last_state})
        df_last_state.to_csv('results/last_state_{}_{}.csv'.format(name, i), index=False)
        return last_state

    def run_ensemble_strategy(self, model_names, model_kwargs, timesteps_dict, policy_dict=None, n_procs=1):
        print("============Start Ensemble Strategy============")
        # for ensemble model, it's necessary to feed the last state
        # of the previous model to the current model as the initial state
        last_state_ensemble = []
        
        Sharpe_dict_full = {m:[] for m in model_names}
        model_use = []
        validation_start_date_list = []
        validation_end_date_list = []
        iteration_list = []

        insample_turbulence = self.df[(self.df.date<self.train_period[1]) & (self.df.date>=self.train_period[0])]
        insample_turbulence_threshold = np.quantile(insample_turbulence.turbulence.values, .90)
        
        if policy_dict == None:
            policy_dict = {m:'MlpPolicy' for m in model_names}

        start = time.time()
        num_epochs = int((len(self.unique_trade_date) - self.rebalance_window + self.validation_window) 
                         / self.rebalance_window) - 1
        for i in range(self.rebalance_window + self.validation_window, len(self.unique_trade_date), self.rebalance_window):
            validation_start_date = self.unique_trade_date[i - self.rebalance_window - self.validation_window]
            validation_end_date = self.unique_trade_date[i - self.rebalance_window]

            validation_start_date_list.append(validation_start_date)
            validation_end_date_list.append(validation_end_date)
            iteration_list.append(i)
            
            epoch_i = int((i - self.rebalance_window - self.validation_window) / self.rebalance_window) + 1
            print(f"=====================Epoch {epoch_i}/{num_epochs}=======================")
            ## initial state is empty
            if i - self.rebalance_window - self.validation_window == 0:
                # inital state
                initial = True
            else:
                # previous state
                initial = False

            # Tuning turbulence index based on historical data
            # Turbulence lookback window is one quarter (63 days)
            end_date_index = self.df.index[self.df["date"] == 
                                           self.unique_trade_date[i - self.rebalance_window - self.validation_window]
                                          ].to_list()[-1]
           
            start_date_index = end_date_index - self.rebalance_window + 1

            historical_turbulence = self.df.iloc[start_date_index:(end_date_index + 1), :]

            historical_turbulence = historical_turbulence.drop_duplicates(subset=['date'])

            historical_turbulence_mean = np.mean(historical_turbulence.turbulence.values)

            if historical_turbulence_mean > insample_turbulence_threshold:
                # if the mean of the historical data is greater than the 90% quantile of insample turbulence data
                # then we assume that the current market is volatile,
                # therefore we set the 90% quantile of insample turbulence data as the turbulence threshold
                # meaning the current turbulence can't exceed the 90% quantile of insample turbulence data
                turbulence_threshold = insample_turbulence_threshold
            else:
                # if the mean of the historical data is less than the 90% quantile of insample turbulence data
                # then we tune up the turbulence_threshold, meaning we lower the risk
                turbulence_threshold = np.quantile(insample_turbulence.turbulence.values, 1)
            print("turbulence_threshold: ", turbulence_threshold)

            ############## Environment Setup starts ##############
            ## training env
            train = data_split(self.df, start=self.train_period[0], 
                               end=validation_start_date)
            
            # Multiprocesing
            env = StockTradingEnv(train, self.stock_dim, self.hmax, self.initial_amount, self.buy_cost_pct,
                                  self.sell_cost_pct, self.reward_scaling, self.state_space, self.action_space,
                                  self.tech_indicator_list, print_verbosity=self.print_verbosity)
          
            check_env(env)
            if n_procs == 1:
                self.train_env = DummyVecEnv([lambda: env])
            else:
                self.train_env = make_vec_env(env, n_envs=n_procs, vec_env_cls=SubprocVecEnv, 
                                              vec_env_kwargs=dict(start_method='spawn'))
            validation = data_split(self.df, validation_start_date, validation_end_date)
            ############## Environment Setup ends ##############

            ############## Training and Validation starts ##############
            print("======Model training from: ", self.train_period[0], "to ", validation_start_date)
            sharpe_dict = {}
            for model in model_names:
                print(f"======{model} Training========")
                Model = self.get_model(model, self.train_env, policy=policy_dict[model], model_kwargs=model_kwargs[model])
                Model = self.train_model(Model, model, 
                                         tb_log_name="{}_{}".format(model, i), 
                                         iter_num = i, 
                                         total_timesteps=timesteps_dict[model])

                print(f"======{model} Validation from: ", validation_start_date, " to ", validation_end_date)
                val_env = DummyVecEnv([
                    lambda: StockTradingEnv(validation, self.stock_dim, self.hmax, self.initial_amount,
                                            self.buy_cost_pct, self.sell_cost_pct, self.reward_scaling,
                                            self.state_space, self.action_space, self.tech_indicator_list,
                                            turbulence_threshold=turbulence_threshold,
                                            iteration=i,
                                            model_name=model,
                                            mode='validation',
                                            print_verbosity=self.print_verbosity)])
                val_obs = val_env.reset()
                self.DRL_validation(model=Model, test_data=validation, test_env=val_env, test_obs=val_obs)
                sharpe = self.get_validation_sharpe(i, model_name=model)
                print(f"{model} Sharpe Ratio: ", sharpe)
                sharpe_dict[model] = sharpe
                Sharpe_dict_full[model].append(sharpe)

            print("======Best Model Retraining from: ", self.train_period[0], "to ", validation_end_date)
            # Environment setup for model retraining up to first trade date
            train_full = data_split(self.df, start=self.train_period[0], end=validation_end_date)
            self.train_full_env = DummyVecEnv([
                lambda: StockTradingEnv(train_full,
                                        self.stock_dim,
                                        self.hmax,
                                        self.initial_amount,
                                        self.buy_cost_pct,
                                        self.sell_cost_pct,
                                        self.reward_scaling,
                                        self.state_space,
                                        self.action_space,
                                        self.tech_indicator_list,
                                        print_verbosity=self.print_verbosity)
            ])
            # Model Selection based on sharpe ratio
            best_model = max(sharpe_dict.items(), key=operator.itemgetter(1))[0]
            model_use.append(best_model)
            model_ensemble = self.get_model(best_model, self.train_full_env, 
                                            policy=policy_dict[best_model],
                                            model_kwargs=model_kwargs[best_model])
            model_ensemble = self.train_model(model_ensemble, "ensemble", 
                                              tb_log_name="ensemble_{}".format(i), 
                                              iter_num = i, 
                                              total_timesteps=timesteps_dict[best_model])

            ############## Training and Validation ends ##############

            ############## Trading starts ##############
            print("======Trading from: ", validation_end_date, "to ", self.unique_trade_date[i])
            last_state_ensemble = self.DRL_prediction(model=model_ensemble, name="ensemble",
                                                      last_state=last_state_ensemble, iter_num=i,
                                                      turbulence_threshold = turbulence_threshold,
                                                      initial=initial)
            ############## Trading ends ##############
        end = time.time()
        print("Ensemble Strategy took: ", (end - start) / 3600, " hours")
        sharpe_dict['Iter'] = iteration_list
        sharpe_dict['Val_Start'] = validation_start_date_list
        sharpe_dict['Val_End'] = validation_end_date_list
        sharpe_dict['Model_Used'] = model_use
        df_summary = pd.DataFrame(sharpe_dict)
        return df_summary



