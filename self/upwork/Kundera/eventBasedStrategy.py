"""
Title :Event based Strategy
Author : Ankit rawat
Description : Relevance of trechnical integrator before and after the event.
"""

import datetime

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import yfinance as yf
import talib as ta
import matplotlib.pyplot as plt
desired_width=320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

from enum import Enum

# Define an enumeration class
class strategies(Enum):
    emaCrossOver = 1

def pullPrices( symbol, startDate, endDate):
    return yf.download(symbol, startDate, endDate)
def eventDetection(data, events, *args, **kwargs):
    print(events)
    for i in events:
        if i == 1:
            # emaCrossOver events
            short_period = kwargs.get('shortPeriod', 10)
            long_period = kwargs.get('longPeriod', 20)
            print(short_period,long_period)
            data['shortPeriodMean'] = data['Close'].ewm(span=short_period, adjust=False).mean()
            data['longPeriodMean'] = data['Close'].ewm(span=long_period, adjust=False).mean()
            data['emaCrossOver'] = 0
            data['emaCrossOver'] = np.where( data['shortPeriodMean'] > data['longPeriodMean'], 1, 0)
            data['crossover'] = data['emaCrossOver'].diff()
    return data[data['crossover'] == 1]


def eventAnalyser(TimeSeries, beforeEventFrame, afterEventFrame, events, count, *args, **kwargs):
    """
    :param TimeSeries:  Time Series to analyse : DataFrame - Date, Open, High, Low, Close, Volume,
    :param beforeEventFrame: days before event : Int
    :param afterEventFrame: : days after event : Int
    :param events:  type of event to analyse    : list with Enum number mentioned in function
    :param count:  Total number of times we need to analyze event    : Int
    :return: DataFrame with selected data for each event date
    """
    short_period = kwargs.get('shortPeriod',10)
    long_period = kwargs.get('longPeriod',20)

    if isinstance(TimeSeries, pd.DataFrame):
        # Verify dataframe has all the required data
        df = TimeSeries.reindex()
        for i in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if i not in df.columns:
                raise Exception("Column {} not found in dataframe".format(i))

        # Event analysis
        # Calculate identify events
        # Assuming eventDetection is a valid function
        data = eventDetection(df, events=[strategies.emaCrossOver.value], shortPeriod=short_period, longPeriod=long_period)
        # Create a new DataFrame to store the selected data
        result_df = pd.DataFrame()
        # Iterate through each event date
        for event_date in data.index:
            start_date = event_date - pd.Timedelta(days=beforeEventFrame)
            end_date = event_date + pd.Timedelta(days=afterEventFrame)

            # Check if start_date is in the index of df
            if start_date in df.index:
                event_index = df.index.get_loc(event_date)

                # Calculate the index positions for before and after frames
                start_index = max(0, event_index - beforeEventFrame)
                end_index = min(len(df) - 1, event_index + afterEventFrame)

                # Select close prices for the specified period
                selected_data = df.iloc[start_index:end_index + 1, df.columns.get_loc('Close')].reset_index(drop=True)

                # Divide each value by the event date close price for days before the event
                selected_data_before = (df.loc[event_date, 'Close']/selected_data.iloc[:beforeEventFrame + 1] - 1) * 100
                # Set the values after the event date to NaN
                selected_data_after = (selected_data.iloc[beforeEventFrame + 1:] / df.loc[event_date, 'Close'] - 1) * 100

                # Concatenate the two parts
                selected_data = pd.concat([selected_data_before, selected_data_after])

                # Create header names like '-5', '-3', '-2', '-1', '0' based on days before and after event
                headers = [str(i) for i in range(-beforeEventFrame, afterEventFrame + 1)]

                # Add the selected data with headers as a new row in the result_df
                result_df[event_date] = pd.Series(selected_data.values, index=headers)

        # Set the event dates as index
        result_df = result_df.T.rename_axis('Event Date').sort_index()

        #Number of events to consider
        result_df  =  result_df.iloc[:count,:]
        print(result_df)
        # Calculate mean of each column
        mean_values = result_df.mean()

        # Plot the mean values
        plt.figure(figsize=(10, 6))
        mean_values = pd.DataFrame(mean_values)
        mean_values.index = mean_values.index.astype(int)
        plt.plot(mean_values.index,mean_values)
        plt.title('Mean Values of Selected Data')
        plt.xlabel('Days Relative to Event Date')
        plt.ylabel('Mean Value')
        plt.show()


        return result_df
if __name__ == "__main__":
    df = pd.read_csv('./data/event_price_evolution.csv')
    print(df.head(2))
    #df = pullPrices("SBIN.NS", startDate="2010-01-01", endDate="2021-04-30")
    #data = eventAnalyser(df,5, 10, [strategies.emaCrossOver.value], 20,shortPeriod=20,longPeriod=50)
    #print(data)$