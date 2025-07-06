from abc import ABC, abstractmethod

class ExchangeMediator(ABC):
    @abstractmethod
    def notify(self, sender, event, data=None):
        pass


class ExchangeEngine(ExchangeMediator):
    def __init__(self):
        self.order_book = None
        self.risk_engine = None
        self.trade_executor = None

    def register_order_book(self, order_book):
        self.order_book = order_book

    def register_risk_engine(self, risk_engine):
        self.risk_engine = risk_engine

    def register_trade_executor(self, trade_executor):
        self.trade_executor = trade_executor

    def notify(self, sender, event, data=None):
        if event == "NewOrder":
            print(f"[ExchangeEngine] Received new order: {data}")
            if self.risk_engine and self.risk_engine.check_risk(data):
                self.order_book.add_order(data)
                self.trade_executor.execute_order(data)
            else:
                print("[ExchangeEngine] Order rejected by risk engine.")
        elif event == "CancelOrder":
            print(f"[ExchangeEngine] Cancel order request: {data}")
            self.order_book.cancel_order(data)
        else:
            print(f"[ExchangeEngine] Unknown event: {event}")


class OrderBook:
    def __init__(self, mediator):
        self.mediator = mediator
        self.orders = []

    def send_order(self, order):
        print("[OrderBook] Sending new order to mediator...")
        self.mediator.notify(self, "NewOrder", order)

    def add_order(self, order):
        print(f"[OrderBook] Adding order: {order}")
        self.orders.append(order)

    def cancel_order(self, order_id):
        print(f"[OrderBook] Cancelling order: {order_id}")
        self.orders = [order for order in self.orders if order["id"] != order_id]

class RiskEngine:
    def __init__(self, mediator):
        self.mediator = mediator

    def check_risk(self, order):
        print(f"[RiskEngine] Checking risk for order {order['id']}")
        # Dummy logic: reject if quantity > 1000
        if order["quantity"] > 1000:
            print("[RiskEngine] Order exceeds risk limits!")
            return False
        print("[RiskEngine] Order passed risk checks.")
        return True

class TradeExecutor:
    def __init__(self, mediator):
        self.mediator = mediator

    def execute_order(self, order):
        print(f"[TradeExecutor] Executing order: {order}")


# Create mediator (Exchange Engine)
engine = ExchangeEngine()

# Create components and register them
order_book = OrderBook(engine)
risk_engine = RiskEngine(engine)
trade_executor = TradeExecutor(engine)

engine.register_order_book(order_book)
engine.register_risk_engine(risk_engine)
engine.register_trade_executor(trade_executor)

# Send a new order
order = {"id": 1, "symbol": "AAPL", "quantity": 500, "price": 150}
order_book.send_order(order)

# Try sending a risky order
large_order = {"id": 2, "symbol": "GOOG", "quantity": 5000, "price": 2800}
order_book.send_order(large_order)

# Cancel an order
engine.notify(order_book, "CancelOrder", 1)