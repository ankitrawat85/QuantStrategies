# Orserver pattern sends multiple notification to different moduels 

from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, price):
        pass

class TradingBot(Observer):
    def __init__(self, name):
        self.name = name

    def update(self, price):
        print(f"{self.name} received price update: {price}")
        # Add logic for trading decision

class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer):
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        pass

    @abstractmethod
    def notify(self):
        pass

class MarketDataFeed(Subject):
    def __init__(self):
        self._observers = []
        self._price = None

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self._price)

    def set_price(self, price):
        print(f"\nMarketDataFeed: New price is {price}")
        self._price = price
        self.notify()

# Create market data feed (subject)
market_data = MarketDataFeed()

# Create trading bots (observers)
bot1 = TradingBot("Bot Alpha")
bot2 = TradingBot("Bot Beta")

# Subscribe bots to market data
market_data.attach(bot1)
market_data.attach(bot2)

# Simulate market price changes
market_data.set_price(101.5)
market_data.set_price(102.3)

# Detach one observer
market_data.detach(bot2)

# Another market price change
market_data.set_price(103.0)
