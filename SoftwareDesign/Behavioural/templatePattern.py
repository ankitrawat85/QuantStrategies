#Imagine you have a trading workflow that looks like this:
#Collect Market Data
#Analyze Data (Strategy Specific)
#Generate Signal (Strategy Specific)
#Execute Order
#Log the Trade
from abc import ABC, abstractmethod

class TradingTemplate(ABC):

    def execute_trade(self):
        self.collect_market_data()
        self.analyze_data()
        signal = self.generate_signal()
        self.execute_order(signal)
        self.log_trade(signal)

    def collect_market_data(self):
        print("[Template] Collecting market data...")

    @abstractmethod
    def analyze_data(self):
        pass

    @abstractmethod
    def generate_signal(self):
        pass

    def execute_order(self, signal):
        print(f"[Template] Executing order: {signal}")

    def log_trade(self, signal):
        print(f"[Template] Logging trade: {signal}")


class MomentumTrading(TradingTemplate):

    def analyze_data(self):
        print("[Momentum] Analyzing data using momentum indicators...")

    def generate_signal(self):
        print("[Momentum] Generating BUY signal (price > moving avg)")
        return "BUY"


class MeanReversionTrading(TradingTemplate):

    def analyze_data(self):
        print("[MeanReversion] Analyzing data for mean reversion...")

    def generate_signal(self):
        print("[MeanReversion] Generating SELL signal (price > mean + threshold)")
        return "SELL"


# Momentum strategy workflow
momentum = MomentumTrading()
momentum.execute_trade()

print("\n--------------------\n")

# Mean reversion strategy workflow
mean_reversion = MeanReversionTrading()
mean_reversion.execute_trade()
