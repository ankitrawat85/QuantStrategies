import matplotlib.pyplot as plt
import warnings
import numpy as np
import yfinance as yf
import pandas as pd

## Graph
import plotly.io as pio
import plotly.graph_objs as go
import plotly.offline as ply
pio.renderers.default = "browser"
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# setup
plt.style.use('seaborn')
plt.rcParams['figure.figsize'] = [16, 9]
plt.rcParams['figure.dpi'] = 300
warnings.simplefilter(action='ignore', category=FutureWarning)

# Stats Calcualtion Libraries
import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns
import scipy.stats as scs
import statsmodels.api as sm
import statsmodels.tsa.api as smt

## Functions

def realized_volatility(x):
    return np.sqrt(np.sum(x ** 2))

def indentify_outliers(row, n_sigmas=3):
        x = row['simple_rtn']
        mu = row['mean']
        sigma = row['std']
        if (x > mu + 3 * sigma) | (x < mu - 3 * sigma):
            return 1
        else:
            return 0

## Import Data
df = yf.download('AAPL',
                       start='2000-01-01',
                       end='2010-12-31',
                       progress=False)

df = df.loc[:, ['Adj Close']]
df.rename(columns={'Adj Close':'adj_close'}, inplace=True)
df['simple_rtn'] = df.adj_close.pct_change()
df['log_rtn'] = np.log(df.adj_close/df.adj_close.shift(1))

## Volatility
df_rv = df.groupby(pd.Grouper(freq='M')).apply(realized_volatility)
df_rv.rename(columns={'log_rtn': 'rv'}, inplace=True)

## Annulize volatility
df_rv.rv = df_rv.rv * np.sqrt(12)


## Outliers
df_rolling = df[['simple_rtn']].rolling(window=21).agg(['mean', 'std'])
df_rolling.columns = df_rolling.columns.droplevel()
df_outliers = df.join(df_rolling)
df_outliers['outlier'] = df_outliers.apply(indentify_outliers,axis=1)
outliers = df_outliers.loc[df_outliers['outlier'] == 1,['simple_rtn']]


## histogram and QQ Plot
'''
Negative skewness (third moment): Large negative returns occur more frequently than large positive ones.
Excess kurtosis (fourth moment) : Large (and small) returns occur more often than expected.
'''
r_range = np.linspace(min(df.log_rtn), max(df.log_rtn), num=1000)
mu = df.log_rtn.mean()
sigma = df.log_rtn.std()
norm_pdf = scs.norm.pdf(r_range, loc=mu, scale=sigma)


## Absence of Autocorrelation in returns - Log return
N_LAGS = 50
SIGNIFICANCE_LEVEL = 0.05
acf = smt.graphics.plot_acf(df.log_rtn,lags=N_LAGS,alpha=SIGNIFICANCE_LEVEL)

ig, ax = plt.subplots(2, 1, figsize=(12, 10))
smt.graphics.plot_acf(df.log_rtn ** 2, lags=N_LAGS,
                                  alpha=SIGNIFICANCE_LEVEL, ax = ax[0])
ax[0].set(title='Autocorrelation Plots',
             ylabel='Squared Returns')
smt.graphics.plot_acf(np.abs(df.log_rtn), lags=N_LAGS,
                         alpha=SIGNIFICANCE_LEVEL, ax = ax[1])
ax[1].set(ylabel='Absolute Returns',xlabel='Lag')
plt.show()

## Leverage Effect
'''
This fact states that most measures of asset volatility are negatively correlated with their returns. 
To investigate it, we used the moving standard deviation (calculated using
the rolling method of a pandas DataFrame) as a measure of historical volatility. 
We used windows of 21 and 252 days, which correspond to one month and one year of trading data.
'''
df['moving_std_252'] = df[['log_rtn']].rolling(window=252).std()
df['moving_std_21'] = df[['log_rtn']].rolling(window=21).std()

fig, ax = plt.subplots(3, 1, figsize=(18, 15),sharex=True)
df.adj_close.plot(ax=ax[0])
ax[0].set(title='MSFT time series',ylabel='Stock price ($)')
df.log_rtn.plot(ax=ax[1])
ax[1].set(ylabel='Log returns (%)')
df.moving_std_252.plot(ax=ax[2], color='r',label='Moving Volatility 252d')
df.moving_std_21.plot(ax=ax[2], color='g',label='Moving Volatility 21d')
ax[2].set(ylabel='Moving Volatility',xlabel='Date')
ax[2].legend()

## Graph Plot
fig = make_subplots(rows=7, cols=1,subplot_titles=("adj_close", "simple_rtn", "log_rtn",))
fig.append_trace(go.Scatter(x=df.index,y=df.adj_close, name = "adj_close",line = dict(color = "green", width = 4,dash = "dash")), row=1, col=1)
fig.append_trace(go.Scatter(x=df.index,y=df.simple_rtn,name = "simple_rtn",line = dict(color = "red", width = 4,dash = "dot")), row=2, col=1)
fig.append_trace(go.Scatter(x=df.index,y=df.log_rtn,name = "log_rtn",line = dict(color = "blue", width = 4,dash = "dashdot")), row=3, col=1)
fig.append_trace(go.Scatter(x=df_outliers.index,y=df_outliers.simple_rtn,name = "Outliners",line = dict(color = "green", width = 4,dash = "dash")), row=4, col=1)
fig.append_trace(go.Scatter(x=outliers.index,y=outliers.simple_rtn,name = "Anomaly",mode="markers+text",line = dict(color = "red", width = 6,dash = "dot")), row=4, col=1)
fig.append_trace(go.Histogram(x=df.log_rtn, histnorm='probability',name = "Histogram"),row=5, col=1)
fig.append_trace(go.Scatter(x=df.index,y=df['moving_std_252'],name = "Moving Volatility 252d",line = dict(color = "red", width = 6,dash = "dot")), row=6, col=1)
fig.append_trace(go.Scatter(x=df.index,y=df['moving_std_21'],name = "Moving Volatility 21d",line = dict(color = "green", width = 6,dash = "dot")), row=6, col=1)

df.log_rtn.plot(title='Daily MSFT returns')
# Q-Q plot
print(df.log_rtn.dropna().values)

## Historgram
fig.update_layout(height=5200, width=1800, title_text="Technical Indicators")

# Update xaxis properties
fig.update_xaxes(title_text="Time", row=1, col=1)
fig.update_xaxes(title_text="Time", row=1, col=2)
fig.update_xaxes(title_text="Time", showgrid=False, row=3, col=1)
fig.update_xaxes(title_text="Time", showgrid=False, row=4, col=1)
fig.update_xaxes(title_text="StandardDeviation", showgrid=False, row=5, col=1)
fig.update_xaxes(title_text="Time", showgrid=False, row=6, col=1)
# Update yaxis properties
fig.update_yaxes(title_text="Closing Price", row=1, col=1)
fig.update_yaxes(title_text="Return ", row=2, col=1)
fig.update_yaxes(title_text="Log Return ", showgrid=True, row=3, col=1)
fig.update_yaxes(title_text="Outliers", showgrid=True, row=4, col=1)
fig.update_yaxes(title_text="Histogram", showgrid=True, row=5, col=1)
fig.update_yaxes(title_text="Rolling Volatility", showgrid=True, row=6, col=1)
fig.show()
