from typing import Callable
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
from stable_baselines.common import set_global_seeds, make_vec_env
from finrl.model.models_ext import DRLAgent
from finrl.env.env_stocktrading import StockTradingEnv
from tqdm import tqdm


def train_model(model_name, env, model_kwargs, policy, policy_kwargs=None, total_timesteps=80000, 
                save=True, file_name='models/model.pkl'):
    agent = DRLAgent(env=env)
    model = agent.get_model(model_name=model_name, policy=policy, policy_kwargs=policy_kwargs, model_kwargs=model_kwargs)
    trained_model = agent.train_model(model=model, 
                                      tb_log_name=model_name,
                                      total_timesteps=total_timesteps)
    if save:
        file_name = f'models/{model_name}.pkl'
        trained_model.save(file_name)
    return trained_model


def train_multi_env(model_name, df, env_kwargs, model_kwargs, policy, Env=StockTradingEnv, policy_kwargs=None,
                    num_cpu=4, total_timesteps=100000, save=True, file_name=None):
    # Create the vectorized environment
    print('Setting up vectorized env ...')
    multi_env = SubprocVecEnv([make_env(df, i, Env, env_kwargs) for i in range(num_cpu)])
    print('=================Start training=================')
    model = train_model(model_name, multi_env, model_kwargs, policy, policy_kwargs=policy_kwargs, 
                        total_timesteps=total_timesteps, save=False)
    if save:
        if file_name == None:
            file_name = f"models/{model_name}_{env_kwargs['reward_method']}.pkl"
        model.save(file_name)
    return model

def test_single_env(model, df_test, env_kwargs, Env=StockTradingEnv):
    account_memory = []
    actions_memory = []
    environment = Env(df_test, **env_kwargs)
    environment = DummyVecEnv([lambda: environment])
    test_obs = environment.reset()
    
    for i in tqdm(range(len(df_test.index.unique()))):
        action, _states = model.predict(test_obs)
        account_memory.append(test_obs[0][0]+test_obs[0][1]*test_obs[0][2])
        actions_memory.append(action.mean())
        test_obs, rewards, dones, info = environment.step(action)
        if dones[0]:
            print("hit end!")
            break
    return account_memory, actions_memory


def test_multi_env(model, df_test, env_kwargs, Env=StockTradingEnv, num_cpu=4):
    account_memory = []
    actions_memory = []
    environment = SubprocVecEnv([make_env(df_test, i, Env, env_kwargs) for i in range(num_cpu)])
    test_obs = environment.reset()

    for i in tqdm(range(len(df_test.index.unique()))):
        action, _states = model.predict(test_obs)
        avg_obs = test_obs.mean(axis=0)
        account_memory.append(avg_obs[0]+avg_obs[1]*avg_obs[2])
        actions_memory.append(action.mean())
        test_obs, rewards, dones, info = environment.step(action)
        if dones[0]:
            print("hit end!")
            break
    return account_memory, actions_memory


def make_env(df, rank, Env, env_kwargs, seed=266):
    """
    Utility function for multiprocessed env.

    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = Env(df, **env_kwargs)
        env.seed(seed + rank)
        return env
    set_global_seeds(seed)
    return _init


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Linear learning rate schedule.

    :param initial_value: Initial learning rate.
    :return: schedule that computes
      current learning rate depending on remaining progress
    """
    def func(progress_remaining: float) -> float:
        """
        Progress will decrease from 1 (beginning) to 0.

        :param progress_remaining:
        :return: current learning rate
        """
        return progress_remaining * initial_value

    return func

def get_sharpe(returns):
    return returns.mean() / returns.std()

def get_turbulence_threshold(df, start_date, end_date, insample_turbulence):
    insample_turbulence_threshold = np.quantile(insample_turbulence.turbulence.values, .90)
    
    # Tuning turbulence index based on historical data
    historical_turbulence = data_split(df, start_date, end_date)
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
        turbulence_threshold = np.quantile(insample_turbulence.turbulence.values, 0.99)
    print("turbulence_threshold: ", turbulence_threshold)
    return turbulence_threshold

def evaluate(df, model, env, num_cpu=4, trade=False):
    account_memory = []
    test_obs = environment.reset()

    for i in tqdm(range(len(df.index.unique()))):
        action, _states = model.predict(test_obs)
        avg_obs = test_obs.mean(axis=0)
        account_memory.append(avg_obs[0]+avg_obs[1]*avg_obs[2])
        test_obs, rewards, dones, info = env.step(action)
        if dones[0]:
            print("hit end!")
            break
    if trade:
        return account_memory
    
    returns = pd.Series(account_memory).pct_change().bfill()
    sharpe = get_sharpe(returns)
    return sharpe, account_memory