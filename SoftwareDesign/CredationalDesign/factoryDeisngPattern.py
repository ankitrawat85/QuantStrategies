# The Factory Method Pattern is a creational design pattern that 
# provides an interface for creating objects in a superclass, 
# but allows subclasses to alter the type of objects that will be created.

# Scenario
#You need to create different order types depending on the trading strategy or client request.
#Instead of hard-coding the creation logic, you implement a factory method that decides which type of order to create.

from abc import ABC, abstractmethod

#Abstract Class 
class Order(ABC): 

    @abstractmethod  
    def execute(self):
        pass

class OrderBooking(ABC): 

    @abstractmethod  
    def createOrder(self):
        pass

    def placeOrder(self):
        order = self.createOrder()
        print(order.execute())


#Concrete Class
class MarketOrder(Order):
    def execute(self):
        return f'Execute market order'

class LimitOrder(Order):
     def execute(self):
        return f'Execute limit order'


class StopLossOrder(Order):
    def execute(self):
        return f'Execute stoploss order'
    

class PlaceMarketOrder(OrderBooking):
    def createOrder(self):
        return MarketOrder()


class PlaceLimitOrder(OrderBooking):
    def createOrder(self):
        return LimitOrder()

class PlaceStopLossOrder(OrderBooking):
    def createOrder(self):
        return StopLossOrder()
    
def client_code(creator):
    creator.placeOrder()

# Example Usage
market_creator = PlaceMarketOrder()
limit_creator = PlaceLimitOrder()
stop_creator = PlaceStopLossOrder()

client_code(market_creator)
client_code(limit_creator)
client_code(stop_creator)