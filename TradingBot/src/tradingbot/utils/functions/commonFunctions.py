from __future__ import annotations
import pandas as pd
from tradingbot.DataMapping.financialDataMapping import *
import pandas as pd
import numpy as np

def remove_duplicate_columns(df):
    """
    Remove duplicate columns from a DataFrame, keeping the first occurrence
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with duplicate columns removed
    """
    # Check for duplicated column names (case insensitive)
    cols = pd.Series(df.columns)
    duplicates = cols.map(lambda x: x.lower()).duplicated()
    
    if duplicates.any():
        duplicate_names = cols[duplicates].unique()
        print(f"Removing duplicate columns: {', '.join(duplicate_names)}")
        return df.loc[:, ~df.columns.duplicated(keep='first')]
    return


def trim_dataframe(df):
    """
    Trim whitespace from both column names and string values in a DataFrame
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    df = df.copy()
    
    # 1. Trim column names
    df.columns = df.columns.str.strip()
    
    # 2. Remove duplicate columns (case insensitive)
    df = remove_duplicate_columns(df)
    
    # 3. Trim string values in all string columns
    string_columns = df.select_dtypes(['object']).columns
    for col in string_columns:
        df[col] = df[col].str.strip()
    
    # 4. Clean numeric columns that might be strings
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col].str.strip())
            except:
                pass
    
    return df


def standardize_sales_columns(df):
    """
    Standardize sales-related columns across quarterly/annual data
    
    Args:
        df: DataFrame with mixed 'Net Sales' (quarterly) and 'Sales' (annual)
    
    Returns:
        DataFrame with consistent 'Revenue' column
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Standardize column names
    if 'Net Sales' in df.columns:
        df['Revenue'] = df['Net Sales']
    elif 'Sales' in df.columns:
        df['Revenue'] = df['Sales']
    
    # Drop original columns if they exist
    df = df.drop(columns=['Net Sales', 'Sales'], errors='ignore')
    
    return df

def ensure_datetime_index(df: pd.DataFrame, date_col: str='date') -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        if date_col in df.columns:
            df = df.copy()
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.set_index(date_col)
        else:
            raise ValueError("DataFrame must have a DatetimeIndex or a 'date' column.")
    return df

def compute_atr(ohlc: pd.DataFrame, length: int=14) -> pd.Series:
    o = ohlc['open'].astype(float).values
    h = ohlc['high'].astype(float).values
    l = ohlc['low'].astype(float).values
    c = ohlc['close'].astype(float).values
    prev_c = np.roll(c, 1); prev_c[0] = c[0]
    tr = np.maximum.reduce([h - l, np.abs(h - prev_c), np.abs(l - prev_c)])
    atr = pd.Series(tr).rolling(length, min_periods=1).mean().values
    return pd.Series(atr, index=ohlc.index, name=f'atr_{length}')

def _zscore(x: pd.Series) -> pd.Series:
    mu = x.mean()
    sd = x.std(ddof=0) or 1.0
    return (x - mu) / sd

def _minmax(x: pd.Series, lo=None, hi=None) -> pd.Series:
    if lo is None: lo = x.min()
    if hi is None: hi = x.max()
    rng = (hi - lo) or 1.0
    return (x - lo) / rng

def _cap01(x):
    return np.minimum(1.0, np.maximum(0.0, x))
