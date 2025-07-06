import requests
import hashlib
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from brokers.base import TradingAPI
import time

class ZerodhaAPI(TradingAPI):
    """Complete Zerodha Kite Connect API implementation with configurable endpoints"""
    
    def __init__(self, config_path: str = "config/zerodha.cfg"):
        self.config_path = Path(config_path)
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.token_last_updated = 0
        self._configure_session()
        
    def _load_config(self, path: str) -> configparser.ConfigParser:
        """Load configuration with validation"""
        config = configparser.ConfigParser()
        if not Path(path).exists():
            raise FileNotFoundError(f"Config file not found at {path}")
        config.read(path)
        return config
        
    def _configure_session(self):
        """Configure HTTP session with headers"""
        self.session.headers.update({
            "X-Kite-Version": self.config.get("api", "version", fallback="3"),
            "User-Agent": "Kiteconnect-python/4.2.0",
            "Authorization": f"token {self.config['credentials']['api_key']}:{self._get_valid_token()}"
        })
    
    def _get_url(self, endpoint: str) -> str:
        """Construct full endpoint URL"""
        base_url = self.config.get("api", "base_url").rstrip("/")
        route = self.config.get("api", f"routes.{endpoint}").lstrip("/")
        return f"{base_url}/{route}"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authorization headers"""
        return {
            "Authorization": f"token {self.config['credentials']['api_key']}:{self.config.get('credentials', 'access_token', fallback='')}"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Universal request handler"""
        url = self._get_url(endpoint)
        kwargs["headers"] = self._get_auth_headers()
        
        try:
            response = getattr(self.session, method.lower())(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None


    # --------------------------
    # Authentication
    # --------------------------
    def _get_valid_token(self) -> str:
        """Returns valid token, refreshes if expired"""
        if not self._is_token_valid():
            new_token = self._refresh_access_token()
            if not new_token:
                raise Exception("Failed to refresh access token")
            return new_token
        return self.config['credentials']['access_token']
    
    def _is_token_valid(self) -> bool:
        """Check token validity (expires daily at 6AM IST)"""
        token = self.config.get('credentials', 'access_token', fallback=None)
        if not token:
            return False
            
        # Check if token was refreshed in last 24 hours
        return (time.time() - float(self.config['credentials']['access_token_last_updated'])) < 86400
    
    def _refresh_access_token(self) -> Optional[str]:
        """Generate new token and update config"""
        new_token = self.get_access_token(
            api_key=self.config['credentials']['api_key'],
            api_secret=self.config['credentials']['api_secret'],
            request_token=self._get_request_token()
        )
        
        if new_token:
            self.config['credentials']['access_token'] = new_token
            self.config['credentials']['access_token_last_updated'] = str(time.time())
            self._save_config()
        return new_token
    
    def _get_request_token(self) -> str:
        """Get request token through login flow (implement your method)"""
        # Options:
        # 1. Manual input (for development)
        # 2. Selenium automation (for production)
        # 3. Read from external source
        api_key = self.config['credentials']['api_key']
        login_url = f"https://kite.trade/connect/login?api_key={api_key}"
        print("\n" + "="*50)
        print(f"Zerodha Login Required:")
        print(f"1. Visit this URL: {login_url}")
        print(f"2. Complete the login")
        print(f"3. Copy the 'request_token' from the redirect URL")
        print("="*50 + "\n")
        
        token = input("Enter new request token from Zerodha login: ")
        if not token:
            raise ValueError("Request token required for token refresh")
        return token
    
    def get_access_token(self, api_key: str, api_secret: str, request_token: str) -> Optional[str]:
        """Get session access token"""
        checksum = hashlib.sha256(
            f"{api_key}{request_token}{api_secret}".encode()
        ).hexdigest()
        
        response = self._make_request(
            "POST",
            "auth",
            data={
                "api_key": api_key,
                "request_token": request_token,
                "checksum": checksum
            }
        )
        return response.get("data", {}).get("access_token") if response else None
    

    def _save_config(self):
        """Only updates access token in config file without any validation checks"""
        try:
            # Ensure credentials section exists
            if 'credentials' not in self.config:
                self.config.add_section('credentials')
            # Atomic write operation
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
                
        except Exception as e:
            print(f"Config save failed: {str(e)}")
            raise

    # --------------------------
    # Market Data
    # --------------------------
    def get_quote_list(self, instruments: List[Dict[str, str]]) -> List[Dict]:
        """Fetch multiple quotes at once"""
        # Implement Zerodha-specific logic here
        param_list = []
        for inst in instruments:
            exchange = inst['exchange'].strip().upper()
            symbol = inst['tradingsymbol'].strip().upper().replace(' ', '+')
            param_list.append(f"i={exchange}:{symbol}")

        # Join parameters with & character
        query_string = "&".join(param_list)
   
        response = self._make_request(
            "GET",
            "quote",
            params=query_string
        )

        if not response or not self._validate_response(response):
            return {}

        return {key.split(":")[-1]:self._parse_quote(value) for key,value in response["data"].items()}



    def get_ltp(self, instruments: List[Dict[str, str]]) -> Dict[str, Union[float, str]]:
        """Get last traded price"""
        param_list = []
        for inst in instruments:
            exchange = inst['exchange'].strip().upper()
            symbol = inst['tradingsymbol'].strip().upper().replace(' ', '+')
            param_list.append(f"i={exchange}:{symbol}")

        # Join parameters with & character
        query_string = "&".join(param_list)

        response = self._make_request(
            "GET",
            "ltp",
            params=query_string
        )

        if not response or not self._validate_response(response):
            return {}
            
        # Process all instruments in response
        result = {}
        for inst_id, data in response["data"].items():
            exchange, tradingsymbol = inst_id.split(":")
            result[inst_id] = {
                "exchange": exchange,
                "tradingsymbol": tradingsymbol.replace('+', ' '),
                "last_price": data["last_price"],
                "instrument_token": data["instrument_token"]
            }
        
        return result

    def get_ohlc(self, exchange: str, symbol: str) -> Dict[str, Union[float, str]]:
        """Get OHLC data"""
        response = self._make_request(
            "GET",
            "ohlc",
            params={"i": f"{exchange}:{symbol}"}
        )
        if response and self._validate_response(response):
            data = response["data"].get(f"{exchange}:{symbol}")
            return {
                "exchange": exchange,
                "symbol": symbol,
                "open": data["ohlc"]["open"],
                "high": data["ohlc"]["high"],
                "low": data["ohlc"]["low"],
                "close": data["ohlc"]["close"],
                "last_price": data["last_price"]
            }
        return {}

    def get_quote(self, exchange: str, symbol: str) -> Dict:
        """Get full market snapshot"""
        response = self._make_request(
            "GET",
            "quote",
            params={"i": f"{exchange}:{symbol}"}
        )
        if response and self._validate_response(response):
            return self._parse_quote(response["data"][f"{exchange}:{symbol}"])
        return {}

    def _parse_quote(self,data) -> Dict:
        """Standardize quote format"""
        return {
            #"timestamp": data["timestamp"],
            #"instrument_token": data["instrument_token"],
            "last_price": data["last_price"],
            "volume": data.get("volume", 0),
            "ohlc": data["ohlc"],
            #"depth": {
            #    "buy": [{"price": o["price"], "qty": o["quantity"]} for o in data["depth"]["buy"][:5]],
            #    "sell": [{"price": o["price"], "qty": o["quantity"]} for o in data["depth"]["sell"][:5]]
            #}
        }

    # --------------------------
    # Order Management
    # --------------------------
    def place_order(
        self,
        exchange: str,
        symbol: str,
        transaction_type: str,
        order_type: str,
        quantity: int,
        price: Optional[float] = None,
        product: str = "MIS",
        validity: str = "DAY",
        **kwargs
    ) -> Optional[str]:
        """Place new order"""
        order_data = {
            "tradingsymbol": symbol,
            "exchange": exchange,
            "transaction_type": transaction_type,
            "order_type": order_type,
            "quantity": quantity,
            "product": product,
            "validity": validity,
            "price": str(price) if price else "0"
        }
        order_data.update(kwargs)
        
        response = self._make_request("POST", "place_order", data=order_data)
        return response.get("data", {}).get("order_id") if response else None

    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Modify existing order"""
        modify_data = {}
        if quantity: modify_data["quantity"] = quantity
        if price: modify_data["price"] = str(price)
        if order_type: modify_data["order_type"] = order_type
        modify_data.update(kwargs)
        
        response = self._make_request("PUT", f"modify_order/{order_id}", data=modify_data)
        return self._validate_response(response) if response else False

    def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        response = self._make_request("DELETE", f"cancel_order/{order_id}")
        return self._validate_response(response) if response else False

    # --------------------------
    # Order Book & History
    # --------------------------
    def get_order_status(self, order_id: str) -> Dict:
        """Get single order status"""
        response = self._make_request("GET", f"order_status/{order_id}")
        return response["data"][-1] if response and self._validate_response(response) else {}

    def get_order_book(self) -> List[Dict]:
        """Get all orders"""
        response = self._make_request("GET", "order_book")
        return response.get("data", []) if response and self._validate_response(response) else []

    def get_trade_book(self) -> List[Dict]:
        """Get trade history"""
        response = self._make_request("GET", "trade_book")
        return response.get("data", []) if response and self._validate_response(response) else []

    # --------------------------
    # Holdings & Positions
    # --------------------------
    def get_holdings(self) -> List[Dict]:
        """Get equity holdings"""
        response = self._make_request("GET", "holdings")
        return response.get("data", []) if response and self._validate_response(response) else []

    def get_positions(self) -> Dict[str, List[Dict]]:
        """Get derivative positions"""
        response = self._make_request("GET", "positions")
        if response and self._validate_response(response):
            return {
                "net": response["data"].get("net", []),
                "day": response["data"].get("day", [])
            }
        return {"net": [], "day": []}

    # --------------------------
    # Utility Methods
    # --------------------------
    def download_masters(
        self,
        path: str = "./data/masters/",
        filters: Optional[Dict[str, Union[Any, Tuple[str, Any], Dict[str, Any]]]] = None,
        columns: Optional[List[str]] = None
        ) -> bool:
        """
        Download instrument master files with advanced range filtering
        
        Args:
            path: Output directory path
            filters: {
                'column_name': value | (operator, value) | {
                    '>': value, 
                    '<': value,
                    '>=': value,
                    '<=': value,
                    '==': value
                }
            }
            columns: List of columns to keep
        
        Returns:
            bool: True if successful, False otherwise
        
        Examples:
            # Simple exact match
            {'segment': 'NSE'}
            
            # Price between 100 and 500
            {'last_price': {'>': 100, '<': 500}}
            
            # Either CE or PE options
            {'instrument_type': ['CE', 'PE']}
        """
        try:
            # Download data
            response = self.session.get(
                self._get_url("instruments"),
                headers=self._get_auth_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            # Setup paths
            Path(path).mkdir(parents=True, exist_ok=True)
            raw_path = Path(path) / "zerodha_master_all.csv"
            processed_path = Path(path) / "zerodha_master_processed.csv"
            
            # Save raw data
            with open(raw_path, "wb") as f:
                f.write(response.content)
            
            # Process data if filters/columns specified
            if filters or columns:
                import pandas as pd
                df = pd.read_csv(raw_path)
                
                # Apply filters
                if filters:
                    for col, condition in filters.items():
                        if col not in df.columns:
                            continue
                            
                        # Dictionary of multiple conditions (e.g. {'>':100, '<':500})
                        if isinstance(condition, dict):
                            for op, val in condition.items():
                                if op == '>':
                                    df = df[df[col] > val]
                                elif op == '<':
                                    df = df[df[col] < val]
                                elif op == '>=':
                                    df = df[df[col] >= val]
                                elif op == '<=':
                                    df = df[df[col] <= val]
                                elif op == '==':
                                    df = df[df[col] == val]
                        
                        # Tuple condition (e.g. ('>', 100))
                        elif isinstance(condition, tuple):
                            op, val = condition
                            if op == '>':
                                df = df[df[col] > val]
                            elif op == '<':
                                df = df[df[col] < val]
                            elif op == '>=':
                                df = df[df[col] >= val]
                            elif op == '<=':
                                df = df[df[col] <= val]
                            elif op == '==':
                                df = df[df[col] == val]
                        
                        # List of values (e.g. ['CE', 'PE'])
                        elif isinstance(condition, list):
                            df = df[df[col].isin(condition)]
                        
                        # Single exact match
                        else:
                            df = df[df[col] == condition]
                
                # Select columns
                if columns:
                    available_cols = [col for col in columns if col in df.columns]
                    df = df[available_cols]
                
                # Save processed data
                df.to_csv(processed_path, index=False)
                print(f"✅ Saved filtered data ({len(df)} rows) to {processed_path}")
                print(f"📊 Columns: {', '.join(df.columns)}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    