import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd

import sqlite3
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import pandas as pd

class Database:
    def __init__(self, db_path: str = "zerodha_data.db"):
        """
        Initialize the database connection
        
        Args:
            db_path: Path to SQLite database file (will be created if doesn't exist)
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database file and establish connection"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency

    def create_table(
        self,
        table_name: str,
        columns: Dict[str, Dict[str, Any]],
        primary_key: Union[str, List[str]] = None
    ) -> bool:
        """
        Create a new table with specified columns and composite primary key support
        
        Args:
            table_name: Name of the table to create
            columns: Dictionary where keys are column names and values are dicts with:
                    - 'type': SQLite data type (e.g., "TEXT", "REAL")
                    - 'default': Default value (optional)
                    - 'nullable': Whether column allows NULL (default True)
            primary_key: Either a single column name or list of columns for composite key
            
        Returns:
            bool: True if successful, False otherwise
        """
        column_defs = []
        for name, spec in columns.items():
            # Basic column definition
            col_def = f"{name} {spec['type']}"
            
            # NULL/NOT NULL constraint
            if not spec.get('nullable', True):
                col_def += " NOT NULL"
                
            # DEFAULT value if specified and column isn't primary key
            if 'default' in spec:
                default_val = spec['default']
                if isinstance(default_val, str) and default_val.upper() not in ('NULL', 'CURRENT_TIMESTAMP'):
                    col_def += f" DEFAULT '{default_val}'"
                else:
                    col_def += f" DEFAULT {default_val}"
            
            column_defs.append(col_def)
        
        # Handle primary key (single or composite)
        if primary_key:
            if isinstance(primary_key, str):
                # Find and modify the primary key column definition
                for i, col_def in enumerate(column_defs):
                    if col_def.startswith(f"{primary_key} "):
                        column_defs[i] = col_def + " PRIMARY KEY"
                        break
            else:
                # Add composite primary key constraint
                column_defs.append(f"PRIMARY KEY ({', '.join(primary_key)})")
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        
        try:
            with self.conn:
                self.conn.execute(query)
            print(f"✅ Table '{table_name}' created successfully")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error creating table: {e}")
            return False

    def insert_data(self, table_name: str, data: List[Dict], replace: bool = False):
        """
        Insert data into the specified table
        
        Args:
            table_name: Table to insert into
            data: List of dictionaries where keys match table columns
            replace: Whether to replace existing records (True) or ignore them (False)
        """
        if not data:
            return
        
        columns = list(data[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        action = "REPLACE" if replace else "INSERT OR IGNORE"
        
        query = f"{action} INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            with self.conn:
                self.conn.executemany(query, [tuple(d.values()) for d in data])
            print(f"✅ Inserted {len(data)} records into '{table_name}'")
        except sqlite3.Error as e:
            print(f"❌ Error inserting data: {e}")

    def fetch_data(
        self,
        table_name: str,
        columns: List[str] = None,
        where: str = None,
        params: tuple = None,
        limit: int = None
    ) -> List[Dict]:
        """
        Fetch data from the database
        
        Args:
            table_name: Table to query
            columns: List of columns to select (None for all)
            where: WHERE clause (without the WHERE keyword)
            params: Parameters for WHERE clause
            limit: Maximum number of records to return
            
        Returns:
            List of dictionaries containing the query results
        """
        cols = "*" if not columns else ", ".join(columns)
        query = f"SELECT {cols} FROM {table_name}"
        
        if where:
            query += f" WHERE {where}"
        if limit:
            query += f" LIMIT {limit}"
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            if columns:
                return [dict(zip(columns, row)) for row in rows]
            else:
                # Get column names from cursor description
                col_names = [d[0] for d in cursor.description]
                return [dict(zip(col_names, row)) for row in rows]
                
        except sqlite3.Error as e:
            print(f"❌ Error fetching data: {e}")
            return []

    def create_historical_data_table(self,table_name = "historical_data"):
        """Create optimized table structure for Zerodha historical data with composite primary key"""
        columns = {
            "instrument_token": {"type": "INTEGER", "nullable": False},
            "tradingsymbol": {"type": "TEXT", "nullable": False},
            "exchange": {"type": "TEXT", "nullable": False},
            "interval": {"type": "TEXT", "nullable": False},
            "timestamp": {"type": "TEXT", "nullable": False},
            "open": {"type": "REAL", "default": 0.0},
            "high": {"type": "REAL", "default": 0.0},
            "low": {"type": "REAL", "default": 0.0},
            "close": {"type": "REAL", "default": 0.0},
            "volume": {"type": "INTEGER", "default": 0},
            "oi": {"type": "INTEGER", "default": 0}
        }
        
        # Create table with composite primary key
        success = self.create_table(
            table_name=table_name,
            columns=columns,
            primary_key=["timestamp", "tradingsymbol", "exchange"]
        )
        
        if success:
            # Create indexes for better performance
            self._create_index(table_name, ["instrument_token", "timestamp"])
            self._create_index(table_name, ["tradingsymbol"])
            self._create_index(table_name, ["exchange"])
        
        return success

    def _create_index(self, table_name: str, columns: List[str]):
        """Create index on specified columns"""
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        try:
            with self.conn:
                self.conn.execute(
                    f"CREATE INDEX IF NOT EXISTS {index_name} "
                    f"ON {table_name} ({columns_str})"
                )
            print(f"✅ Created index {index_name}")
        except sqlite3.Error as e:
            print(f"❌ Error creating index: {e}")

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def dataframe_to_sql(self, table_name: str, df: pd.DataFrame, replace: bool = False):
        """
        Insert data from a pandas DataFrame into the database
        
        Args:
            table_name: Target table name
            df: DataFrame containing data to insert
            replace: Whether to replace existing records
        """
        try:
            with self.conn:
                df.to_sql(
                    table_name,
                    self.conn,
                    if_exists="replace" if replace else "append",
                    index=False
                )
            print(f"✅ Inserted {len(df)} records from DataFrame into '{table_name}'")
        except Exception as e:
            print(f"❌ Error inserting DataFrame: {e}")
