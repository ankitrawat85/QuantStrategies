"""
    Title: Template for Options Price Prediction Using Decision Tree
    Description: A decision tree is used to predict whether the price of an
    option will go up or down. Trades are placed if the prediction is better
    than a random guess.

    Data requirement: Data subscription to the your local exchange is required
    for Futures and Options data feed.

    ############################# DISCLAIMER #############################
    This is a strategy template only and should not be
    used for live trading without appropriate backtesting and tweaking of
    the strategy parameters.
    ######################################################################
"""

# To calculate implied volatility
import mibian as m

# Import pandas and numpy
import pandas as pd
import numpy as np

# Machine learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from datetime import datetime


def initialize(context):

    # Define the retrain flag
    context.retrain_flag = 0

    for i in range(7):
        schedule_function(
            rebalance,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open(hours=i, minutes=10)
        )

    schedule_function(
            retrain_model_flag,
            date_rule=date_rules.month_start(),
            time_rule=time_rules.market_open(minutes=5)
        )
    # Define the lookback
    context.lookback = 100

    # Define the split
    context.split = int(0.7 * context.lookback)

    # Define the position
    context.position = 0

    # Define the model
    context.cls = None

    '''
    ############################# ATTENTION ##############################
    The following parameters need to be changed as per your selection of
    the option and future contract.
    ######################################################################
    '''

    # Define the number of lots to purchase
    context.quantity = 75

    # Define the symbol
    context.symbol = 'NIFTY50'

    # Define the strike price
    context.strike_price = 13000.0

    # Define the option type
    context.option_type = 'C'

    # Expiry dates are in YYYYMMDD format
    context.expiry = "20201231"

    # Option symbol
    context.option_sym = superSymbol(
        secType='OPT',
        symbol=context.symbol,
        exchange='NSE',
        currency='INR',
        expiry=context.expiry,
        strike=context.strike_price,
        right=context.option_type,
        includeExpired=True)

    # Future for the same underlying
    context.future_sym = superSymbol(
        secType='FUT',
        symbol=context.symbol,
        exchange='NSE',
        currency='INR',
        expiry=context.expiry,
        includeExpired=True)


# Function to change the retrain_flag
def retrain_model_flag(context, data):
    context.retrain_flag = 1


def rebalance(context, data):
    # Fetch the data
    option_data = data.history(context.option_sym,
                               ['close'], context.lookback, '1d')

    future_data = data.history(context.future_sym,
                               ['close'], context.lookback, '1d')

    option_data['Time_to_expiry'] = (pd.Timestamp(
        datetime.strptime(context.expiry, "%Y%m%d")) -
        pd.to_datetime(option_data.index)).days

    option_data['IV'] = 0
    option_data['Delta'] = 0
    option_data['Gamma'] = 0
    option_data['Theta'] = 0
    option_data['Vega'] = 0
    if context.option_type == 'C':
        for row in range(len(option_data)):
            option_data.iloc[row, option_data.columns.get_loc('IV')] = m.BS([future_data.iloc[row]['close'],
                                                            context.strike_price,
                                                            0,
                                                            option_data.iloc[row]['Time_to_expiry']],
                                                            callPrice=option_data.iloc[row]['close']).impliedVolatility
            option_model = m.BS([future_data.iloc[row]['close'],
                                context.strike_price,
                                0,
                                option_data.iloc[row]['Time_to_expiry']],
                                volatility=option_data.iloc[row]['IV'])

            option_data.iloc[row, option_data.columns.get_loc('Delta')] = option_model.callDelta
            option_data.iloc[row, option_data.columns.get_loc('Theta')] = option_model.callTheta
            option_data.iloc[row, option_data.columns.get_loc('Gamma')] = option_model.gamma
            option_data.iloc[row, option_data.columns.get_loc('Vega')] = option_model.vega
    else:
        for row in range(len(option_data)):
            option_data.iloc[row, option_data.columns.get_loc('IV')] = m.BS([future_data.iloc[row]['close'],
                                                            context.strike_price,
                                                            0,
                                                            option_data.iloc[row]['Time_to_expiry']],
                                                            putPrice=option_data.iloc[row]['close']).impliedVolatility
            option_model = m.BS([future_data.iloc[row]['close'],
                                context.strike_price,
                                0,
                                option_data.iloc[row]['Time_to_expiry']],
                                volatility=option_data.iloc[row]['IV'])

            option_data.iloc[row, option_data.columns.get_loc('Delta')] = option_model.putDelta
            option_data.iloc[row, option_data.columns.get_loc('Theta')] = option_model.putTheta
            option_data.iloc[row, option_data.columns.get_loc('Gamma')] = option_model.gamma
            option_data.iloc[row, option_data.columns.get_loc('Vega')] = option_model.vega

    predictors = option_data[['IV', 'Delta', 'Gamma', 'Theta', 'Vega']]

    # Actual Signals
    target = np.where(option_data['close'].shift(-1) > option_data['close'], 1, -1)

    # Number of days to train algo
    # Train dataset
    predictors_train = predictors[:context.split]
    target_train = target[:context.split]
    # Test dataset
    predictors_test = predictors[context.split:]
    target_test = target[context.split:]

    # Training the model
    if context.retrain_flag or context.cls is None:
        context.cls = DecisionTreeClassifier(max_depth=6,
                                             min_samples_split=2,
                                             max_leaf_nodes=8)
        context.cls.fit(predictors_train, target_train)

    # Getting the signal
    signal = context.cls.predict(predictors)[-1]

    # Getting the model accuracy
    accuracy = accuracy_score(target_test, context.cls.predict(predictors_test))

    # Taking position for options
    if signal == 1 and accuracy > 0.5 and context.position != 1:
        print("Placing a long order")
        order_target(context.option_sym, context.quantity)
        context.position = 1

    if signal == -1 and accuracy > 0.5 and context.position != -1:
        print("Placing a short order")
        order_target(context.option_sym, -context.quantity)
        context.position = -1

    if accuracy <= 0.5:
        print("Placing a square-off order")
        order_target(context.option_sym, 0)
        context.position = 0
