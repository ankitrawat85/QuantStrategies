2. Behavioral Design Patterns

➡️ What they deal with: Communication between objects.
➡️ Goal: Manage responsibilities and communication between objects.
➡️ Problem they solve: How to assign responsibility between objects and how they interact.

---

## Observer Notifies dependent objects automatically when a state changes (publish/subscribe).

The Observer Pattern is a behavioral design pattern where an object (called the Subject)
maintains a list of dependents (called Observers) and notifies them automatically of any state changes,
typically by calling one of their methods.

Scenario:
You have multiple trading bots (observers) listening to market data feeds (subject).
Whenever market data changes, all bots are notified, so they can decide whether to trade, hedge, or alert someone.

---

## Strategy Enables selecting an algorithm at runtime (plug-and-play behaviors).

Eliminates conditional logic (if/else chains).
Algorithms are independent and interchangeable.
Open/Closed Principle: Add new strategies without changing existing code.
Easier to test and maintain individual strategies.

#State Allows an object to change its behavior when its state changes. - this is good when we have diffent states to follow . Like order - Full , partial, cancel - Order lifecycles (New → Partial → Filled → Cancelled). - Connection states (Connected, Disconnected, Reconnecting). - Market regimes (Bull Market, Bear Market, Sideways). - Risk management states (Active, Suspended, Breach Detected).

Chain of Responsibility Passes requests along a chain of handlers.
Mediator Centralizes complex communication between related objects.

---

## Template Method Defines a skeleton of an algorithm and lets subclasses fill in the steps.

--
You define the skeleton of an algorithm in a base class (abstract class).
Subclasses can override specific steps of the algorithm without changing the overall structure.
Follows the Hollywood Principle: “Don’t call us, we’ll call you.” (The base class controls the flow, subclasses fill in details.)

Visitor Adds operations to objects without changing their classes.
Iterator Provides a way to access elements of a collection sequentially.
Memento Captures and restores an object's internal state (undo functionality).
