import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def simulate_gbm(s_0, mu, sigma, n_sims, T, N):
    dt = T / N
    dW = np.random.normal(scale=np.sqrt(dt),
                          size=(n_sims, N))
    print(dW.shape)
    W = np.cumsum(dW, axis=1)
    time_step = np.linspace(dt, T, N)
    time_steps = np.broadcast_to(time_step, (n_sims, N))
    S_t = s_0 * np.exp((mu - 0.5 * sigma ** 2) * time_steps
                       + sigma * W)
    S_t = np.insert(S_t, 0, s_0, axis=1)
    return S_t

RISKY_ASSET = 'INFY.NS'
START_DATE = '2016-01-01'
END_DATE = '2022-02-03'
df = yf.download(RISKY_ASSET, start=START_DATE,
                             end=END_DATE, adjusted=True)
adj_close = df['Adj Close']
returns = adj_close.pct_change().dropna()
print(f'Average return: {100 * returns.mean():.2f}%')
returns.plot(title=f'{RISKY_ASSET} returns: {START_DATE} -{END_DATE}')

train = returns['2019-01-01':'2019-06-30']
test = returns['2019-07-01':'2019-07-31']

T = len(test)
N = len(test)
print(train.index[-1].date())
S_0 = adj_close.loc[str(train.index[-1].date())]
N_SIM = 100
mu = train.mean()
sigma = train.std()
gbm_simulations = simulate_gbm(S_0, mu, sigma, N_SIM, T, N)
print(gbm_simulations)



# prepare objects for plotting
LAST_TRAIN_DATE = train.index[-1].date()
FIRST_TEST_DATE = test.index[0].date()
LAST_TEST_DATE = test.index[-1].date()
PLOT_TITLE = (f'{RISKY_ASSET} Simulation '
                         f'({FIRST_TEST_DATE}:{LAST_TEST_DATE})')
selected_indices = adj_close[LAST_TRAIN_DATE:LAST_TEST_DATE].index
index = [date.date() for date in selected_indices]
gbm_simulations_df = pd.DataFrame(np.transpose(gbm_simulations),
                                             index=index)
           # plotting
ax = gbm_simulations_df.plot(alpha=0.2, legend=False)
line_1, = ax.plot(index, gbm_simulations_df.mean(axis=1),
                             color='red')
line_2, = ax.plot(index, adj_close[LAST_TRAIN_DATE:LAST_TEST_DATE],
                             color='blue')
ax.set_title(PLOT_TITLE, fontsize=16)
ax.legend((line_1, line_2), ('mean', 'actual'))
plt.show()
