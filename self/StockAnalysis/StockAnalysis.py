'''

Back Testing -  RSI and MV

'''

import backtrader.sizers
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.analyzers as btanalyzer

from self.tradingSetup.backtrader.Strategy.oldrsi import oldrsi
from self.tradingSetup.backtrader.code.analyzer import strategyParamAnalysis
from fbprophet.diagnostics import cross_validation,performance_metrics
from fbprophet.plot import plot_cross_validation_metric

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns
import scipy.stats as scs
import statsmodels.api as sm
import statsmodels.tsa.api as smt
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import seaborn as sns
from fbprophet import Prophet

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


def simulate_gbm(s_0, mu, sigma, n_sims, T, N):
    dt = T / N
    dW = np.random.normal(scale=np.sqrt(dt),
                          size=(n_sims, N))
    W = np.cumsum(dW, axis=1)
    time_step = np.linspace(dt, T, N)
    time_steps = np.broadcast_to(time_step, (n_sims, N))
    print(s_0 * np.exp((mu - 0.5 * sigma ** 2)))
    print(time_steps)
    print(s_0  * time_steps)
    S_t = s_0 * np.exp((mu - 0.5 * sigma ** 2) * time_steps
                       + sigma * W)
    S_t = np.insert(S_t, 0, s_0, axis=1)
    return S_t

def simulate_gbm1(s_0, mu, sigma, n_sims, T, N):
    dt = T / N
    dW = np.random.normal(scale=np.sqrt(dt),
                          size=(n_sims, N))
    W = np.cumsum(dW, axis=1)
    time_step = np.linspace(dt, T, N)
    time_steps = np.broadcast_to(time_step, (n_sims, N))
    S_t = s_0 * np.exp((mu - 0.5 * sigma ** 2) * time_steps
                       + sigma * W)
    S_t = np.insert(S_t, 0, s_0, axis=1)
    return S_t

if __name__ == "__main__":
    df = yf.download('INFY.NS', '2016-01-01', '2022-02-04')
    df_ = df.copy(deep = True)
    df = df.loc[:, ['Adj Close']]
    df.rename(columns={'Adj Close': 'adj_close'}, inplace=True)
    df['simple_rtn'] = df.adj_close.pct_change()
    df['log_rtn'] = np.log(df.adj_close / df.adj_close.shift(1))
    df = df.dropna()
    df_rv = df.groupby(pd.Grouper(freq='M')).apply(realized_volatility)
    df_rv.rename(columns={'log_rtn': 'rv'}, inplace=True)
    ## Annulized volatility
    df_rv["Annual_vol"] = df_rv.rv * np.sqrt(12)
    fig, ax = plt.subplots(4, 1, sharex=True)
    ax[0].plot(df["adj_close"])
    ax[1].plot(df["simple_rtn"])
    ax[2].plot(df["log_rtn"])
    ax[3].plot(df_rv["Annual_vol"])

    #Identifying outliers
    df_rolling = df[['simple_rtn']].rolling(window=21).agg(['mean', 'std'])
    df_rolling.columns = df_rolling.columns.droplevel()
    df_outliers = df.join(df_rolling)

    df_outliers['outlier'] = df_outliers.apply(indentify_outliers,
                                               axis=1)
    outliers = df_outliers.loc[df_outliers['outlier'] == 1,['simple_rtn']]
    fig, ax = plt.subplots()
    ax.plot(df_outliers.index, df_outliers.simple_rtn,
            color='blue', label='Normal')
    ax.scatter(outliers.index, outliers.simple_rtn,
               color='red', label='Anomaly')
    ax.set_title("stock returns")
    ax.legend(loc='lower right')
    plt.show()

    ## Investigating stylized facts ofasset returns
    '''
    Stylized facts are statistical properties that appear to be 
    present in many empirical asset returns (across time and markets).
    '''
    ## 1 . PDF
    print("PDF---")
    r_range = np.linspace(min(df.log_rtn), max(df.log_rtn), num=1000)
    mu = df.log_rtn.mean()
    sigma = df.log_rtn.std()
    norm_pdf = scs.norm.pdf(r_range, loc=mu, scale=sigma)
    print(norm_pdf)

    ## 2 QQ Plot

    fig, ax = plt.subplots(1, 2, figsize=(16, 8))
    # histogram
    '''
    By looking at the metrics such as the mean, standard deviation, skewness, and kurtosis 
    we can infer that they deviate from what we would expect under normality.
    '''
    sns.distplot(df.log_rtn, kde=False, norm_hist=True, ax=ax[0])
    ax[0].set_title('Distribution of Stock returns', fontsize=16)
    ax[0].plot(r_range, norm_pdf, 'g', lw=2,
               label=f'N({mu:.2f}, {sigma ** 2:.4f})')
    ax[0].legend(loc='upper left');
    # Q-Q plot
    qq = sm.qqplot(df.log_rtn.values, line='s', ax=ax[1])
    ax[1].set_title('Q-Q plot', fontsize=16)
    plt.show()

    ## Correlation Absenceof autocorrelation in returns
    '''
    Only a few values lie outside the confidence interval (we do not look at lag 0) and can be considered statistically significant. We can assume that we have verified that 
    there is no autocorrelation in the log returns series.
    '''
    N_LAGS = 50
    SIGNIFICANCE_LEVEL = 0.05
    acf = smt.graphics.plot_acf(df.log_rtn,
                                lags=N_LAGS,
                                alpha=SIGNIFICANCE_LEVEL)
    plt.show()

    ## Small and decreasing autocorrelation in squared/absolute returns
    fig, ax = plt.subplots(2, 1, figsize=(12, 10))
    smt.graphics.plot_acf(df.log_rtn ** 2, lags=N_LAGS,
                          alpha=SIGNIFICANCE_LEVEL, ax=ax[0])
    ax[0].set(title='Autocorrelation Plots',
              ylabel='Squared Returns')
    smt.graphics.plot_acf(np.abs(df.log_rtn), lags=N_LAGS,
                          alpha=SIGNIFICANCE_LEVEL, ax=ax[1])
    ax[1].set(ylabel='Absolute Returns',
              xlabel='Lag')
    plt.show()

    ## Leverage effect
    '''
    For the fifth fact, run the following steps to investigate 
    the existence of the leverage effect.
    '''
    df['moving_std_252'] = df[['log_rtn']].rolling(window=252).std()
    df['moving_std_21'] = df[['log_rtn']].rolling(window=21).std()

    fig, ax = plt.subplots(3, 1, figsize=(18, 15),
                           sharex=True)
    df.adj_close.plot(ax=ax[0])
    ax[0].set(title='MSFT time series',
              ylabel='Stock price ($)')
    df.log_rtn.plot(ax=ax[1])
    ax[1].set(ylabel='Log returns (%)')
    df.moving_std_252.plot(ax=ax[2], color='r',
                           label='Moving Volatility 252d')
    df.moving_std_21.plot(ax=ax[2], color='g',
                          label='Moving Volatility 21d')
    ax[2].set(ylabel='Moving Volatility',
              xlabel='Date')
    ax[2].legend()
    plt.show()

    ## MODELING
    # additive model:
    '''
    There are two types of models that are used for decomposing time series: additive and
    multiplicative.
    The following are the characteristics of the additive model:
    Model's form: y(t) = level + trend + seasonality + noise
    
    Linear model: changes over time are consistent in size
    The trend is linear (straight line)
    
    Linear seasonality with the same frequency (width) and amplitude (height) of cycles over time
    The following are the characteristics of the multiplicative model: Model's form: y(t) = level * trend * seasonality * noise
    Non-linear model: changes over time are not consistent in size, for example, exponential
    A curved, non-linear trend
    Non-linear seasonality with increasing/decreasing frequency and amplitude of cycles over time
        
    '''
    WINDOW_SIZE = 12
    # =================> Approach#1 <==================
    # Set period after building dataframe

    # Reproduce the OP's example
    seasonal_decompose(df_['Close'], model='additive', period=30).plot()
    plt.show()
    seasonal_decompose(df_['Close'], model='multiplicative', period=30).plot()
    plt.show()
    df_ = df_.reset_index()
    print("model_prophet")
    df_.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
    print(df_.dtypes)
    print("**&&&&&")
    print(df_.tail(10))
    print("**********")
    train_indices = df_.ds.apply(lambda x: x.year) < 2022
    df_train = df_.loc[train_indices].dropna()
    df_test = df_.loc[~train_indices].reset_index(drop=True)

    ##  Monte Carlo Simulations
    print(df_train)
    adj_close = df_[['ds','Adj Close']].set_index('ds')
    returns = adj_close.pct_change().dropna()
    df_train = returns[returns.index.year <2022]
    df_test = returns[returns.index.year >=  2022]
    print(adj_close)
    T = len(df_test)
    N = len(df_test)
    S_0 = adj_close.loc[str(df_train.index[-1].date())][0]
    N_SIM = 100
    mu = df_train['Adj Close'].mean()
    sigma1 = df_train['Adj Close'].std()
    print(sigma1)
    print(df_train['Adj Close'].std())
    gbm_simulations = simulate_gbm(S_0, mu, sigma1, N_SIM, T, N)

    # prepare objects for plotting
    LAST_TRAIN_DATE = df_train.index[-1].date()
    FIRST_TEST_DATE = df_test.index[0].date()
    LAST_TEST_DATE = df_test.index[-1].date()
    selected_indices = adj_close.loc[LAST_TRAIN_DATE:LAST_TEST_DATE]
    index = selected_indices.index
    gbm_simulations_df = pd.DataFrame(np.transpose(gbm_simulations),
                                      index=index)
    # plotting
    ax = gbm_simulations_df.plot(alpha=0.2, legend=False)
    line_1, = ax.plot(index, gbm_simulations_df.mean(axis=1),
                      color='red')
    line_2, = ax.plot(index, adj_close[LAST_TRAIN_DATE:LAST_TEST_DATE],
                      color='blue')
    #ax.set_title(PLOT_TITLE, fontsize=16)
    ax.legend((line_1, line_2), ('mean', 'actual'))

    ## Testing Prophet
    df_train = df_train.reset_index()
    df_train.rename(columns={'Adj Close': 'y'}, inplace=True)
    m = Prophet(interval_width=0.95,daily_seasonality=True)
    m.fit(df_train)
    future = m.make_future_dataframe(periods=100,freq='D')
    forecast = m.predict(future)
    print(forecast)
    m.plot(forecast)
    m.plot_components(forecast)
    plt.show()

    df_cv = cross_validation(m,initial='700 days',period='180 days',horizon='365 days')
    print(df_cv.head(20))
    df_p = performance_metrics(df_cv)
    print(df_p.head(20))
    plot_cross_validation_metric(df_cv,metric='rmse')
    plt.show()
    ##

    model_prophet = Prophet(seasonality_mode='additive')
    model_prophet.add_seasonality(name='monthly', period=30.5,
                                  fourier_order=5)
    model_prophet.fit(df_train)
    df_future = model_prophet.make_future_dataframe(periods=365)
    df_pred = model_prophet.predict(df_future)
    model_prophet.plot(df_pred)
    plt.show()
    model_prophet.plot_components(df_pred)
    plt.show()
    print("predictions----")
    print("df_pred")
    print(df_pred)
    selected_columns = ['ds', 'yhat_lower', 'yhat_upper', 'yhat']
    df_pred = df_pred.loc[:, selected_columns].reset_index(drop=True)
    df_test = df_test.merge(df_pred, on=['ds'], how='left')
    df_test.rename(columns={'Adj Close': 'y'}, inplace=True)
    df_test.ds = pd.to_datetime(df_test.ds)
    df_test.set_index('ds', inplace=True)
    fig, ax = plt.subplots(1, 1)
    print(df_test[['y', 'yhat_lower', 'yhat_upper',
                                    'yhat']])
    ax = sns.lineplot(data=df_test[['y', 'yhat_lower', 'yhat_upper',
                                    'yhat']])
    ax.fill_between(df_test.index,
                    df_test.yhat_lower,
                    df_test.yhat_upper,
                    alpha=0.3)
    ax.set(title='actual vs. predicted',
           xlabel='Date',
           ylabel='Gold Price ($)')

    plt.show()


