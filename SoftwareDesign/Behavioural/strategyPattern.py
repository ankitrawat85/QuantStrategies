from abc import ABC, abstractmethod

class TradingStrategy(ABC):
    @abstractmethod
    def trade(self, market_data):
        pass

 #Concrete Strategies
class MomentumStrategy(TradingStrategy):
    def trade(self, market_data):
        print("Executing Momentum Strategy")
        # Logic: Buy if price is increasing, sell if decreasing
        if market_data[-1] > market_data[-2]:
            print("Momentum Strategy: BUY signal")
        else:
            print("Momentum Strategy: SELL signal")

class MeanReversionStrategy(TradingStrategy):
    def trade(self, market_data):
        print("Executing Mean Reversion Strategy")
        avg_price = sum(market_data) / len(market_data)
        if market_data[-1] < avg_price:
            print("Mean Reversion: BUY signal (price below average)")
        else:
            print("Mean Reversion: SELL signal (price above average)")

#Context: Trading Bot
class TradingBot:
    def __init__(self, strategy: TradingStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: TradingStrategy):
        self.strategy = strategy

    def execute_trade(self, market_data):
        self.strategy.trade(market_data)


# Example market data (price history)
market_data = [100, 102, 105, 107, 106, 108]

# Use Momentum Strategy first
momentum = MomentumStrategy()
bot = TradingBot(momentum)
bot.execute_trade(market_data)

# Switch to Mean Reversion Strategy at runtime
mean_reversion = MeanReversionStrategy()
bot.set_strategy(mean_reversion)
bot.execute_trade(market_data)
