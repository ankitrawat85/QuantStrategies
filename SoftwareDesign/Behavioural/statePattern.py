from abc import ABC, abstractmethod

class OrderState(ABC):
    @abstractmethod
    def handle(self, order):
        pass

    @abstractmethod
    def cancel(self, order):
        pass

class NewOrderState(OrderState):
    def handle(self, order):
        print("New Order placed. Waiting for execution.")
        # Transition to partially filled if some shares are executed
        order.set_state(PartiallyFilledOrderState())

    def cancel(self, order):
        print("Cancelling the new order...")
        order.set_state(CancelledOrderState())

class PartiallyFilledOrderState(OrderState):
    def handle(self, order):
        print("Order partially filled.")
        # If remaining shares are filled
        order.set_state(FilledOrderState())

    def cancel(self, order):
        print("Cancelling remaining shares in the order...")
        order.set_state(CancelledOrderState())

class FilledOrderState(OrderState):
    def handle(self, order):
        print("Order fully filled. No further action allowed.")

    def cancel(self, order):
        print("Cannot cancel. Order already filled.")

class CancelledOrderState(OrderState):
    def handle(self, order):
        print("Order is cancelled. No further action possible.")

    def cancel(self, order):
        print("Order already cancelled.")

class Order:
    def __init__(self):
        self.state = NewOrderState()

    def set_state(self, state: OrderState):
        self.state = state

    def process(self):
        self.state.handle(self)

    def cancel(self):
        self.state.cancel(self)


order = Order()

# New order placed
order.process()  # New Order placed. Waiting for execution.

# Partially filled, then move to fully filled
order.process()  # Order partially filled.

# Try to cancel a fully filled order
order.cancel()   # Cannot cancel. Order already filled.

# Process again on filled state
order.process()  # Order fully filled. No further action allowed.
