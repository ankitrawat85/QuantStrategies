from code import interact

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt   
from financepy.finutils import *
from financepy.market.curves import *
from financepy.products.equity import *
from financepy.finutils import *
from financepy.models.FinModelSABR import *

import ipywidgets as widgets
from IPython.display import display
from ipywidgets import interact, interact_manual

valueDate = FinDate(1, 9, 2020)
expiryDate = valueDate.addYears(1)
strikePrice = 100
callOption = FinEquityVanillaOption(expiryDate, strikePrice, FinOptionTypes.EUROPEAN_CALL)

stockPrice = 100
dividendYield = 0.00
interestRate = 0.00
volatility = 0.185
model = FinModelBlackScholes(volatility)
num_time_steps = 10

# a simulated path for the first 10 time steps including today
spot = [stockPrice, 108, 104, 102, 104, 106, 98, 90, 89, 100]

spot = [stockPrice, 101, 102, 101, 100, 101, 100, 101, 100, 101]

realized_vol = np.zeros(num_time_steps)

dt = 1.0 / 365

for i in range(1, num_time_steps):
    realized_vol[i] = np.sqrt(np.log(spot[i] / spot[i - 1]) ** 2 / dt)

print(realized_vol)

hedge_delta = np.zeros(num_time_steps)
hedge_pnl = np.zeros(num_time_steps)

option_price = np.zeros(num_time_steps)
option_delta = np.zeros(num_time_steps)
option_pnl = np.zeros(num_time_steps)

for i in range(0, num_time_steps):
    currentDate = valueDate.addDays(i)

    discountCurve = FinDiscountCurveFlat(currentDate, interestRate, FinFrequencyTypes.CONTINUOUS)
    option_price[i] = callOption.value(currentDate, spot[i], discountCurve, dividendYield, model)
    option_delta[i] = callOption.delta(currentDate, spot[i], discountCurve, dividendYield, model)

# compute the hedge portfolio delta and its change
hedge_delta = pd.Series(-1 * option_delta)
hedge_delta_change = hedge_delta.diff()
hedge_delta_change[0] = -1 * option_delta[0]

# compute the hedge portfolio pnl
for i in range(1, num_time_steps):
    hedge_pnl[i] = hedge_delta[i - 1] * (spot[i] - spot[i - 1])

# compute option pnl
option_pnl[1:] = np.diff(option_price)

df = pd.DataFrame(zip(spot, option_delta, option_pnl, hedge_delta_change, hedge_pnl, realized_vol),
                  columns=['spot', 'option delta', 'option pnl', 'hedge delta change', 'hedge pnl', 'realized_vol'])

df['option + hedge pnl'] = df['option pnl'] + df['hedge pnl']

df['change in spot'] = df['spot'].diff()

total_portfolio_pnl = df['option + hedge pnl'].sum()

print(" total PNL :  {} ".format(total_portfolio_pnl))

f = 10
strikes = np.linspace(1, 20, 20)
t = 1
@interact
def plot_SABR(alpha0=(0.1, 1, 0.1), beta=(-1, 1, 0.1), rho=(-0.999, 0.999, 0.1), nu=(0.001, 2, 0.2),
              ymax=(0.2, 1, 0.1)):

    model = FinModelSABR(alpha0, beta, rho, nu)

    volsSABR = model.blackVol(f, strikes, t)
    plt.plot(strikes, volsSABR);
    plt.ylim((0, ymax))
    plt.title("SABR");
    plt.xlabel("Strike");
    plt.ylabel("Black Volatility");
    plt.grid()
    plt.show()


callOption.impliedVolatility()