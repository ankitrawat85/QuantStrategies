import pandas as pd
from tradingbot.DataMapping.financialDataMapping import *

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