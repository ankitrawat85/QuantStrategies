import pandas as pd

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)


class strategyParamAnalysis:

    def printTradeAnalysis(self,analyzer):
        '''
        Function to print the Technical Analysis results in a nice format.
        '''
        # Get the results we are interested in
        total_open = analyzer.total.open
        total_closed = analyzer.total.closed
        total_won = analyzer.won.total
        total_lost = analyzer.lost.total
        win_streak = analyzer.streak.won.longest
        lose_streak = analyzer.streak.lost.longest
        pnl_net = round(analyzer.pnl.net.total, 2)
        strike_rate = (total_won / total_closed) * 100
        # Designate the rows
        h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
        h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
        r1 = [total_open, total_closed, total_won, total_lost]
        r2 = [strike_rate, win_streak, lose_streak, pnl_net]
        # Check which set of headers is the longest.
        if len(h1) > len(h2):
            header_length = len(h1)
        else:
            header_length = len(h2)
        # Print the row
        data = [total_open, total_closed, total_won, total_lost, strike_rate, win_streak, lose_streak, pnl_net]
        return pd.DataFrame([data], columns=['total_open', 'total_closed', 'total_won', 'total_lost', 'strike_rate',
                                             'win_streak', 'lose_streak', 'pnl_net'])

    def rsi(self,backtest_result):
        output_ = pd.DataFrame(columns = ['RSI_long','RSI_short','profit_mult','devfactor','Sell_stop_loss','profit_mult','return','drawdown', 'sharpe',
                                          'total_open' , 'total_closed' , 'total_won' ,
                                            'total_lost' , 'strike_rate' ,
                                            'win_streak' , 'lose_streak' , 'pnl_net'])
        for x in backtest_result:
            df_ = self.printTradeAnalysis(x[0].analyzers.ta.get_analysis())
            df_ = pd.DataFrame(df_)
            par_list = [x[0].params.RSI_long,
                        x[0].params.RSI_short,
                        x[0].params.profit_mult,
                        x[0].params.devfactor,
                        x[0].params.Sell_stop_loss,
                        x[0].params.profit_mult,
                        x[0].analyzers.returns.get_analysis()['rnorm100'],
                        x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                        x[0].analyzers.sharpe.get_analysis()['sharperatio']]
            df = pd.DataFrame([par_list],columns=['RSI_long','RSI_short','profit_mult','devfactor','Sell_stop_loss','profit_mult','return','drawdown', 'sharpe'])

            result_ = pd.concat([df,df_],axis=1)
            output_ = pd.concat([output_,result_],axis=0)

        output_.to_csv("backtrader_optimization_RSI.csv")
        return output_


    def mv(self,backtest_result):
        output_ = pd.DataFrame(columns=['length_fast', 'length_slow', 'devfactor', 'return',
                                            'drawdown','sharpe', 'total_open', 'total_closed',
                                            'total_won',
                                            'total_lost', 'strike_rate',
                                            'win_streak', 'lose_streak', 'pnl_net'])
        for x in backtest_result:
            df_ = self.printTradeAnalysis(x[0].analyzers.ta.get_analysis())
            df_ = pd.DataFrame(df_)
            par_list = [x[0].params.fast,
                        x[0].params.slow,
                        x[0].params.devfactor,
                        x[0].params.Sell_stop_loss,
                        x[0].analyzers.returns.get_analysis()['rnorm100'],
                        x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                        x[0].analyzers.sharpe.get_analysis()['sharperatio']]
            df = pd.DataFrame([par_list],
                              columns=['length_fast', 'length_slow', 'devfactor','Sell_stop_loss','return',
                                       'drawdown','sharpe'])

            result_ = pd.concat([df, df_], axis=1)
            output_ = pd.concat([output_, result_], axis=0)

        output_.to_csv("backtrader_optimization_mv.csv")
        return output_

