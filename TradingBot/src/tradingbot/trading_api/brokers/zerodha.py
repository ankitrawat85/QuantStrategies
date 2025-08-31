import requests
import hashlib
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any,Literal
from tradingbot.trading_api.brokers.base import TradingAPI
import time
import sys
import datetime
import pytz
import csv
import os
import pandas as pd


# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from Database.database import Database

class ZerodhaAPI(TradingAPI):
    """Complete Zerodha Kite Connect API implementation with configurable endpoints"""
    
    def __init__(self, config_path: str = "config/zerodha.cfg"):
        self.config_path = Path(config_path)
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.token_last_updated = 0
        self._configure_session()
        self.db = None
        
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

    def _make_request(self, method: str, endpoint: str, path_suffix: str = "", **kwargs) -> Optional[Dict]:
        """Universal request handler"""
        
        url = self._get_url(endpoint)
        # Append path suffix if provided
        if path_suffix:
            url = f"{url.rstrip('/')}/{path_suffix.lstrip('/')}"
        
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
        """Check token validity (expires after 24hrs OR daily at 6AM IST, whichever comes first)."""
        token = self.config.get('credentials', 'access_token', fallback=None)
        if not token:
            return False

        # Get last updated timestamp
        last_updated = float(self.config['credentials']['access_token_last_updated'])
        current_time = time.time()

        # Check 24-hour expiry
        is_within_24hrs = (current_time - last_updated) < 86400

        # Check 6 AM IST daily expiry
        ist = pytz.timezone('Asia/Kolkata')
        last_updated_dt = datetime.datetime.fromtimestamp(last_updated, tz=ist)
        now = datetime.datetime.now(ist)
        
        # Check if token was generated before today's 6 AM (and now is after 6 AM)
        today_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)
        is_after_6am_today = now >= today_6am
        was_generated_before_6am = last_updated_dt < today_6am

        # Token is invalid if:
        # - It's past 6 AM today AND the token was generated before 6 AM today
        is_expired_due_to_6am = is_after_6am_today and was_generated_before_6am

        # Final validity: Must be within 24hrs AND not expired due to 6 AM rule
        return is_within_24hrs and not is_expired_due_to_6am
        
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

    def get_quote_list(self, instruments: List[Dict[str, str]], batch_size: int = 50) -> List[Dict]:
        """
        Fetch multiple quotes in batches and return flattened data with instrument details.
        
        Args:
            instruments: List of instruments in format [{"exchange": "NSE", "tradingsymbol": "INFY"}]
            batch_size: Number of instruments per request (default: 50)
        
        Returns:
            List of flattened quote dictionaries with instrument details
        """
        symbol_to_instrument = {
            inst['tradingsymbol'].strip().upper().replace(' ', '+'): inst
            for inst in instruments
        }
        
        all_quotes = []
        
        # Process instruments in batches
        for i in range(0, len(instruments), batch_size):
            batch = instruments[i:i + batch_size]
            param_list = [
                f"i={inst['exchange'].strip().upper()}:{inst['tradingsymbol'].strip().upper().replace(' ', '+')}"
                for inst in batch
            ]
            query_string = "&".join(param_list)
            
            response = self._make_request("GET", "quote", params=query_string)
            
            if not response or not self._validate_response(response):
                continue  # Skip failed batches
                
            # Process each quote in the response
            for key, value in response["data"].items():
                symbol = key.split(":")[-1]
                instrument_data = symbol_to_instrument.get(symbol, {})
                
                quote_data = {
                    'exchange': instrument_data.get('exchange', ''),
                    'instrument_token': instrument_data.get('instrument_token', ''),
                    'tradingsymbol': instrument_data.get('tradingsymbol', ''),
                    'last_price': value.get('last_price'),
                    'volume': value.get('volume'),
                    'open': value.get('ohlc', {}).get('open'),
                    'high': value.get('ohlc', {}).get('high'),
                    'low': value.get('ohlc', {}).get('low'),
                    'close': value.get('ohlc', {}).get('close')
                }
                all_quotes.append(quote_data)
        
        return all_quotes


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
    # Historical Data
    # --------------------------

    def get_historical_data(
        self,
        instrument_token: Union[int, str],
        interval: str,
        from_date: str,
        to_date: str,
        continuous: bool = False,
        oi: bool = False,
        output_format: Literal['dict', 'dataframe'] = 'dict'
    ) -> Union[Optional[Dict], Optional[pd.DataFrame]]:
        """
        Fetch historical data for a single instrument
        
        Args:
            instrument_token: Instrument token (can be string or int)
            interval: One of ["minute", "day", "3minute", "5minute", "10minute", 
                            "15minute", "30minute", "60minute", etc.]
            from_date: Start date in "yyyy-mm-dd" format (or "yyyy-mm-dd HH:MM:SS" for intraday)
            to_date: End date in "yyyy-mm-dd" format (or "yyyy-mm-dd HH:MM:SS" for intraday)
            continuous: For futures contracts (default False)
            oi: Include OI data (default False)
            output_format: Return format - 'dict' (default) or 'dataframe'
            
        Returns:
            Dictionary or DataFrame containing historical data with columns:
            ['instrument_token', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
            or None if request fails
        """
        # Original function logic
        if len(from_date) == 10:
            from_date = f"{from_date} 09:15:00" if interval != "day" else f"{from_date} 00:00:00"
        if len(to_date) == 10:
            to_date = f"{to_date} 15:30:00" if interval != "day" else f"{to_date} 23:59:59"
            
        from_date_url = from_date.replace(' ', '+')
        to_date_url = to_date.replace(' ', '+')
        
        query_string = f"from={from_date_url}&to={to_date_url}"
        if continuous:
            query_string += "&continuous=1"
        if oi:
            query_string += "&oi=1"

        response = self._make_request(
            "GET", 
            "historical",
            params=query_string,
            path_suffix=f"{instrument_token}/{interval}"
        )
        
        data = response.get("data") if response else None
        
        # Convert to DataFrame if requested
        if data and output_format == 'dataframe':
            try:
                # Convert the dictionary to DataFrame
                df = pd.DataFrame(data['candles'],columns =['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
                
                # Rename columns and select only the ones we want
                df['instrument_token'] = str(instrument_token)
                
                # Ensure all required columns are present
                required_columns = ['instrument_token', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = None  # Add missing columns with None values
                
                # Reorder columns consistently
                df = df[required_columns]
                
                # Convert timestamp to datetime if it's not already
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                return df
                
            except Exception as e:
                print(f"Error converting to DataFrame: {str(e)}")
                return data if output_format == 'dict' else None
        
        return data

    def get_batch_historical_data(
        self,
        csv_path: str,
        save_to: str = "csv",  # "csv" or "db"
        output_path: Optional[str] = None,  # For CSV: file path, For DB: table name
        interval: str = "day",
        from_date: str = None,
        to_date: str = None,
        continuous: bool = False,
        oi: bool = False,
        max_requests_per_minute: int = 30,
        db_conn: Optional[Database] = None, 
        required_cols = ['instrument_token', 'tradingsymbol', 'exchange']
    ) -> bool:
        """
            Fetch historical data for multiple instruments and save to CSV or database
            
            Args:
                csv_path: Path to CSV file containing instrument tokens
                save_to: Destination type - "csv" or "db" or None if just want to resturn data in dataframe 
                output_path: For CSV: output file path, For DB: table name
                interval: Candlestick interval
                from_date: Start date (yyyy-mm-dd or yyyy-mm-dd HH:MM:SS)
                to_date: End date (yyyy-mm-dd or yyyy-mm-dd HH:MM:SS)
                continuous: For futures contracts
                oi: Include OI data
                max_requests_per_minute: API rate limit
                db_conn: ZerodhaDatabase instance (required for save_to="db")
                
            Returns:
                bool: True if all operations succeeded, False otherwise
        """
        try:
            import pandas as pd
            from pathlib import Path
            import time

            if save_to not in ["csv", "db"]:
                raise ValueError("save_to must be either 'csv' or 'db'")
            
            if save_to == "db" and db_conn is None:
                raise ValueError("db_conn parameter required when save_to='db'")
            
            if save_to == "csv" and output_path is None:
                output_path = "zerodha_historical_data.csv"
        
            # Read CSV file
            instruments_df = pd.read_csv(csv_path)
            
            
            if not all(col in instruments_df.columns for col in required_cols):
                raise ValueError(f"CSV must contain these columns: {required_cols}")
            
            # Prepare combined DataFrame
            combined_data = []
            request_count = 0
            start_time = time.time()
            all_success = True
            
            for _, row in instruments_df.iterrows():
                # Rate limiting
                if request_count >= max_requests_per_minute:
                    elapsed = time.time() - start_time
                    if elapsed < 60:
                        time.sleep(60 - elapsed)
                    request_count = 0
                    start_time = time.time()
                
                # Fetch data
                data = self.get_historical_data(
                    instrument_token=row['instrument_token'],
                    interval=interval,
                    from_date=from_date,
                    to_date=to_date,
                    continuous=continuous,
                    oi=oi
                )
                
                if data:
                    # Add instrument metadata to each row
                    for record in data['candles']:
                        enriched_record = {}  # Create a copy to avoid modifying original
                        enriched_record.update({
                            'instrument_token': row['instrument_token'],
                            'tradingsymbol': row['tradingsymbol'],
                            'exchange'     : row['exchange'],
                            'interval'     : interval,
                            'timestamp' :record[0],
                            'open': record[1],
                            'high': record[2],
                            'low': record[3],
                            'close': record[4],
                            'volume': record[5]
                        })
                        if len(record) == 7:
                            enriched_record.update({'OI': record[-1]})

                        combined_data.append(enriched_record)
                    print(f"✅ Fetched data for {row['tradingsymbol']} ({row['exchange']})")
                else:
                    print(f"❌ Failed to fetch data for {row['tradingsymbol']} ({row['exchange']})")
                    all_success = False
                
                request_count += 1
                time.sleep(0.1)  # Small delay between requests
            
            if combined_data:
                df = pd.DataFrame(combined_data)
                if save_to == "csv":
                    # Reorder columns to have metadata first
                    meta_cols = ['instrument_token', 'tradingsymbol', 'exchange', 'interval']
                    other_cols = [col for col in df.columns if col not in meta_cols]
                    df = df[meta_cols + other_cols]
                    
                    # Save to single file
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(output_path, index=False)
                    print(f"💾 Saved combined data to {output_path} ({len(df)} records)")
                
                elif save_to == "db":
                    # Save to database
                    db_conn.insert_data(
                        table_name=output_path,
                        data=combined_data,
                        replace=True
                    )
                else:
                    return df
            print(f"Data insertion completed")
            return all_success
            
        except Exception as e:
            print(f"❌ Error in batch processing: {str(e)}")
            return False

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
    def instrumentLookup(instrument_df,symbol):
        """Looks up instrument token for a given script from instrument dump"""
        try:
            return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
        except:
            return -1

    def download_masters(
        self,
        path: str = "./data/masters/",
        filters: Optional[Dict[str, Union[Any, Tuple[str, Any], Dict[str, Any]]]] = None,
        columns: Optional[List[str]] = None,
        ignore_tradingsymbols: Optional[List[str]] = None
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
            
            #ignore_tradingsymbols: List of strings to exclude from tradingsymbol column
            ignore_tradingsymbols=['BANK', 'FIN']
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
            if filters or columns or ignore_tradingsymbols:
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
                
                # Filter out tradingsymbols containing specified strings
                if ignore_tradingsymbols and 'tradingsymbol' in df.columns:
                    pattern = '|'.join(ignore_tradingsymbols)
                    df = df[~df['tradingsymbol'].str.contains(pattern, case=False, na=False)]
                
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

    def create_database(self,databaseName = 'zerodha.db'):
        self.db = Database(databaseName)

    def  create_historical_data_table(self,tableName = "timeseries_data"):
        #    Create historical data table with composite key
        self.db.create_historical_data_table(tableName)

    def insert_data(self,tableName="timeseries_data",data=None,replace=True):
        self.db.insert_data(tableName, data, replace)

    def fetch_data(self,table,where="exchange = ?",params=('NSE',)):
        return self.db.fetch_data(table,where=where,params=params)

    def save_quotes_to_csv(
        self,
        quotes: List[Dict],
        folder_path: str = "quotes_data",
        filename: str = "filtered_quotes.csv",
        filters: Optional[Dict[str, Union[Any, Tuple[str, Any], Dict[str, Any], Tuple[Any, Any]]]] = None,
    ) -> None:
        """
        Save quotes to CSV with dynamic column detection and flexible filtering including range support.
        
        Args:
            quotes: List of quote dictionaries.
            folder_path: Output directory. Default="quotes_data".
            filename: Output CSV filename. Supports strftime (e.g., "quotes_%Y%m%d.csv").
            filters: Dict of filtering rules. Examples:
                - Exact match: {"volume": 1000} → volume == 1000
                - Conditional: {"last_price": (">=", 50)} → last_price >= 50
                - Range: {"volume": (1000, 5000)} → 1000 <= volume <= 5000
                - Nested: {"ohlc": {"open": ("<", 2000)}} → ohlc["open"] < 2000
        """
        if not quotes:
            print("No quotes provided. CSV not created.")
            return

        # Apply filters if provided
        filtered_quotes = quotes if not filters else self._filter_quotes_with_range(quotes, filters)

        if not filtered_quotes:
            print("No quotes matched filters. CSV not created.")
            return

        # Auto-detect columns from the first quote
        fieldnames = list(filtered_quotes[0].keys())

        # Create folder if missing
        os.makedirs(folder_path, exist_ok=True)

        # Add timestamp to filename if strftime directives are present
        if any(f"%{c}" in filename for c in "YmdHMS"):
            filename = datetime.now().strftime(filename)

        file_path = os.path.join(folder_path, filename)

        # Write to CSV
        with open(file_path, mode="w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_quotes)

        print(f"✅ Saved {len(filtered_quotes)} quotes to {file_path}")

    def _filter_quotes_with_range(
        self,
        quotes: List[Dict],
        filters: Dict[str, Union[Any, Tuple[str, Any], Dict[str, Any], Tuple[Any, Any]]]
    ) -> List[Dict]:
        """
        Filter quotes with support for range conditions.
        
        Args:
            quotes: List of quote dictionaries.
            filters: Filter rules including range support.
        
        Returns:
            Filtered list of quotes.
        """
        filtered = []
        for quote in quotes:
            include = True
            for field, rule in filters.items():
                if field not in quote:
                    include = False
                    break

                # Handle nested filters
                if isinstance(rule, dict):
                    if not isinstance(quote[field], dict):
                        include = False
                        break
                    if not self._apply_nested_filter(quote[field], rule):
                        include = False
                        break

                # Handle range filter (tuple of two values)
                elif isinstance(rule, tuple) and len(rule) == 2 and not isinstance(rule[0], str):
                    min_val, max_val = rule
                    if not (min_val <= quote[field] <= max_val):
                        include = False
                        break

                # Handle operator-based filter (tuple with operator string)
                elif isinstance(rule, tuple) and len(rule) == 2 and isinstance(rule[0], str):
                    op, target = rule
                    if not self._compare_values(quote[field], op, target):
                        include = False
                        break

                # Handle exact match
                elif quote[field] != rule:
                    include = False
                    break

            if include:
                filtered.append(quote)
        return filtered

    def _apply_nested_filter(
        self,
        data: Dict[str, Any],
        filters: Dict[str, Union[Any, Tuple[str, Any], Tuple[Any, Any]]]
    ) -> bool:
        """Helper for nested filters with range support."""
        for field, rule in filters.items():
            if field not in data:
                return False

            # Handle range in nested filters
            if isinstance(rule, tuple) and len(rule) == 2 and not isinstance(rule[0], str):
                min_val, max_val = rule
                if not (min_val <= data[field] <= max_val):
                    return False
            elif isinstance(rule, tuple) and len(rule) == 2 and isinstance(rule[0], str):
                op, target = rule
                if not self._compare_values(data[field], op, target):
                    return False
            elif data[field] != rule:
                return False
        return True

    def _compare_values(self, value: Any, operator: str, target: Any) -> bool:
        """Helper for conditional comparisons."""
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "in": lambda a, b: a in b,
            "not in": lambda a, b: a not in b,
        }
        return ops.get(operator, ops["=="])(value, target)


    def read_csv_to_dataframe(self,
        file_path: str,
        parse_dates: Optional[list] = None,
        dtype: Optional[Dict[str, Union[str, type]]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Read a CSV file into a Pandas DataFrame with flexible parsing.

        Args:
            file_path (str): Path to the CSV file.
            parse_dates (list, optional): Columns to parse as dates. Default=None.
            dtype (dict, optional): Data types for columns (e.g., {"volume": int}). Default=None.
            **kwargs: Additional arguments for `pd.read_csv()`.

        Returns:
            pd.DataFrame: Data loaded from CSV.

        Example:
            >>> df = read_csv_to_dataframe(
            ...     "quotes_data/filtered_quotes.csv",
            ...     parse_dates=["timestamp"],
            ...     dtype={"volume": int, "last_price": float}
            ... )
        """
        try:
            df = pd.read_csv(
                file_path,
                parse_dates=parse_dates,
                dtype=dtype,
                **kwargs
            )
            print(f"✅ Successfully read {len(df)} rows from {file_path}")
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading CSV: {str(e)}")
        

    def read_csv_to_dicts(self,file_path: str) -> List[Dict]:
        """Read CSV into a list of dictionaries (no Pandas dependency)."""
        with open(file_path, mode="r") as f:
            return list(csv.DictReader(f))
        
    def fetch_and_prepare_zerodha(self,
        root_dir: str,
        from_date: str,
        to_date: str,
        instrument_token: str,
        interval: str = "day",                     # <-- NEW: interval param
    ) -> pd.DataFrame:
        cfg = os.path.join(root_dir, "config", "Broker", "zerodha.cfg")
        zerodha = ZerodhaAPI(cfg)
        raw = zerodha.get_historical_data(
            instrument_token=instrument_token,
            interval=interval,                     # <-- use it here
            from_date=from_date,
            to_date=to_date,
            output_format='dataframe'
        ).reset_index(drop=True)

        ts = 'timestamp' if 'timestamp' in raw.columns else 'date'
        raw[ts] = pd.to_datetime(raw[ts]).dt.tz_localize(None)
        df = raw.set_index(ts).sort_index()
        df = df.rename(columns={c: c.capitalize() for c in df.columns})
        need = ['Open', 'High', 'Low', 'Close','Volume']
        if not set(need).issubset(df.columns):
            raise ValueError("Missing OHLCV columns after fetch.")
        return df[need]

    def _estimate_start(self,end_dt: pd.Timestamp, n_bars: int, interval: str) -> pd.Timestamp:
        """
        Simple lookback estimator: pad by ~25% so Zerodha returns at least n_bars.
        Adjust if your market calendar requires more padding.
        """
        end_dt = pd.to_datetime(end_dt).to_pydatetime()
        mins = {"minute":1,"3minute":3,"5minute":5,"10minute":10,"15minute":15,"30minute":30,"60minute":60}
        if interval == "day":
            delta = datetime.timedelta(days=int(n_bars * 1.3))
        else:
            step = mins.get(interval, 15)
            delta = datetime.timedelta(minutes=int(n_bars * step * 1.25))
        return pd.Timestamp(end_dt - delta)

    def make_fetcher_zerodha_last_n(self,
        root_dir: str,
        instrument_token: str,
        end_dt   : str,
        n_bars   : int,
        default_interval: str = "day"
        ):
        """
        Returns a function: fetch_last_n(symbol, end_dt, n_bars, interval) -> DataFrame
        'symbol' is ignored (you already have instrument_token).
        """
        def fetch_last_n(_root_dir:str,symbol: str, end_dt: pd.Timestamp, n_bars: int, interval: str = None) -> pd.DataFrame:
            ivl = interval or default_interval
            start_ts = self._estimate_start(end_dt, n_bars, ivl)

            # Call your fetcher (now supports interval)
            df = self.fetch_and_prepare_zerodha(
                root_dir=_root_dir,
                from_date=start_ts.strftime("%Y-%m-%d %H:%M:%S"),
                to_date=pd.to_datetime(end_dt).strftime("%Y-%m-%d %H:%M:%S"),
                instrument_token=symbol,
                interval=ivl
            )
            # Return the last n bars exactly
            return df.tail(n_bars).reset_index().rename(columns={"index": "timestamp"})
        return fetch_last_n(root_dir,instrument_token,end_dt,n_bars,default_interval)


    