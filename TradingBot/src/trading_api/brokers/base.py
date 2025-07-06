from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

class TradingAPI(ABC):
    """Abstract base class for all trading broker APIs.
    All child classes MUST implement these methods."""
    
    # --------------------------
    # Authentication
    # --------------------------
    @abstractmethod
    def get_access_token(self, api_key: str, api_secret: str, request_token: str) -> Optional[str]:
        """Authenticate and return access token."""
        pass

    # --------------------------
    # Market Data
    # --------------------------
    @abstractmethod
    def get_ltp(self, exchange: str, symbol: str) -> Dict[str, Union[float, str]]:
        """Get last traded price."""
        pass

    @abstractmethod
    def get_ohlc(self, exchange: str, symbol: str) -> Dict[str, Union[float, str]]:
        """Get OHLC data."""
        pass

    @abstractmethod
    def get_quote(self, exchange: str, symbol: str) -> Dict:
        """Get full market quote."""
        pass

    @abstractmethod
    def get_quote_list(self, instruments: List[Dict[str, str]]) -> List[Dict]:
        """Bulk fetch quotes for multiple instruments."""
        pass

    # --------------------------
    # Order Management
    # --------------------------
    @abstractmethod
    def place_order(
        self,
        exchange: str,
        symbol: str,
        transaction_type: str,  # BUY/SELL
        order_type: str,        # MARKET/LIMIT/SL/etc.
        quantity: int,
        price: Optional[float] = None,
        product: str = "MIS",   # MIS/CNC/NRML
        validity: str = "DAY",  # DAY/IOC
        **kwargs
    ) -> Optional[str]:
        """Place an order. Returns order_id if successful."""
        pass

    @abstractmethod
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Modify an existing order."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        pass

    # --------------------------
    # Order Book & History
    # --------------------------
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """Fetch single order status."""
        pass

    @abstractmethod
    def get_order_book(self) -> List[Dict]:
        """Fetch all orders."""
        pass

    @abstractmethod
    def get_trade_book(self) -> List[Dict]:
        """Fetch all trades."""
        pass

    # --------------------------
    # Holdings & Positions
    # --------------------------
    @abstractmethod
    def get_holdings(self) -> List[Dict]:
        """Fetch equity holdings."""
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, List[Dict]]:
        """Fetch derivative positions (net/day)."""
        pass

    # --------------------------
    # Utility Methods
    # --------------------------
    @abstractmethod
    def download_masters(self, path: str = "./data/masters/") -> bool:
        """Download instrument master files."""
        pass

    @staticmethod
    def _validate_response(response: Dict) -> bool:
        """Helper to validate API responses."""
        return response.get("status") == "success"