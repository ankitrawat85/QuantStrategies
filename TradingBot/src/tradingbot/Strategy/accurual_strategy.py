import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

def get_financial_data(ticker):
    """Retrieve financial statements from Yahoo Finance with robust error handling"""
    stock = yf.Ticker(ticker)
    data = {'ticker': ticker}
    
    try:
        # Balance Sheet
        bs = stock.balance_sheet
        if bs is not None and not bs.empty:
            data['date'] = bs.columns[0]
            data['current_assets'] = bs.loc['Current Assets'].iloc[0] if 'Current Assets' in bs.index else np.nan
            data['cash'] = bs.loc['Cash And Cash Equivalents'].iloc[0] if 'Cash And Cash Equivalents' in bs.index else np.nan
            data['current_liabilities'] = bs.loc['Current Liabilities'].iloc[0] if 'Current Liabilities' in bs.index else np.nan
            data['short_term_debt'] = bs.loc['Current Debt'].iloc[0] if 'Current Debt' in bs.index else np.nan
            data['income_taxes_payable'] = bs.loc['Tax Payable'].iloc[0] if 'Tax Payable' in bs.index else np.nan
            data['total_assets'] = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else np.nan
            
            # Previous period data if available
            if len(bs.columns) > 1:
                data['prev_current_assets'] = bs.loc['Current Assets'].iloc[1] if 'Current Assets' in bs.index else np.nan
                data['prev_cash'] = bs.loc['Cash And Cash Equivalents'].iloc[1] if 'Cash And Cash Equivalents' in bs.index else np.nan
                data['prev_current_liabilities'] = bs.loc['Current Liabilities'].iloc[1] if 'Current Liabilities' in bs.index else np.nan
                data['prev_short_term_debt'] = bs.loc['Current Debt'].iloc[1] if 'Current Debt' in bs.index else np.nan
                data['prev_income_taxes_payable'] = bs.loc['Tax Payable'].iloc[1] if 'Tax Payable' in bs.index else np.nan
        
        # Income Statement
        is_ = stock.income_stmt
        if is_ is not None and not is_.empty:
            data['net_income'] = is_.loc['Net Income'].iloc[0] if 'Net Income' in is_.index else np.nan
        
        # Cash Flow Statement
        cf = stock.cashflow
        if cf is not None and not cf.empty:
            data['depreciation'] = cf.loc['Depreciation'].iloc[0] if 'Depreciation' in cf.index else np.nan
            data['operating_cash_flow'] = cf.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cf.index else np.nan
        
        return data
    
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def determine_calculation_method(data):
    """Determine which accrual calculation method to use based on data availability"""
    has_cf_method = all(pd.notna(data.get(x)) for x in ['operating_cash_flow', 'net_income', 'total_assets'])
    
    has_bs_method = all(pd.notna(data.get(x)) for x in [
        'current_assets', 'cash', 'current_liabilities', 
        'total_assets', 'depreciation',
        'prev_current_assets', 'prev_cash', 'prev_current_liabilities'
    ])
    
    if has_cf_method and has_bs_method:
        return 'both'
    elif has_bs_method:
        return 'balance_sheet'
    elif has_cf_method:
        return 'cash_flow'
    else:
        return None

def calculate_accruals(df):
    """Automatically calculate accruals using best available method"""
    results = []
    
    for _, row in df.iterrows():
        method = determine_calculation_method(row)
        accrual_data = {'ticker': row['ticker'], 'date': row['date']}
        
        if method in ('cash_flow', 'both'):
            accrual_data['accruals_cf'] = row['operating_cash_flow'] - row['net_income']
            accrual_data['accrual_ratio_cf'] = accrual_data['accruals_cf'] / row['total_assets']
        
        if method in ('balance_sheet', 'both'):
            delta_ca = row['current_assets'] - row['prev_current_assets']
            delta_cash = row['cash'] - row['prev_cash']
            delta_cl = row['current_liabilities'] - row['prev_current_liabilities']
            delta_std = row['short_term_debt'] - row['prev_short_term_debt'] if pd.notna(row['short_term_debt']) else 0
            delta_tp = row['income_taxes_payable'] - row['prev_income_taxes_payable'] if pd.notna(row['income_taxes_payable']) else 0
            
            accrual_data['accruals_bs'] = ((delta_ca - delta_cash) - 
                                         (delta_cl - delta_std - delta_tp) - 
                                         row['depreciation'])
            avg_assets = (row['total_assets'] + row.get('prev_total_assets', row['total_assets'])) / 2
            accrual_data['accrual_ratio_bs'] = accrual_data['accruals_bs'] / avg_assets
        
        accrual_data['calculation_method'] = method
        results.append(accrual_data)
    
    return pd.merge(df, pd.DataFrame(results), on=['ticker', 'date'])

def accrual_strategy(df, preferred_method='auto', long_threshold=0.1, short_threshold=0.1):
    """
    Implement accrual strategy with automatic method selection
    
    Parameters:
    -----------
    preferred_method : str
        'auto' - uses best available method for each stock
        'cash_flow' - forces cash flow method when available
        'balance_sheet' - forces balance sheet method when available
        'both' - requires both methods available
    """
    df = df.copy()
    
    if preferred_method == 'auto':
        df['use_cf'] = df['calculation_method'].isin(['cash_flow', 'both'])
        df['use_bs'] = df['calculation_method'].isin(['balance_sheet', 'both'])
        
        # Calculate composite rank when both available
        df['accrual_rank_cf'] = df.groupby('date')['accrual_ratio_cf'].rank(pct=True)
        df['accrual_rank_bs'] = df.groupby('date')['accrual_ratio_bs'].rank(pct=True)
        
        # Weighted average where both available
        df['composite_rank'] = np.where(
            df['calculation_method'] == 'both',
            (df['accrual_rank_cf'] + df['accrual_rank_bs']) / 2,
            np.where(
                df['calculation_method'] == 'cash_flow',
                df['accrual_rank_cf'],
                df['accrual_rank_bs']
            )
        )
        rank_col = 'composite_rank'
    
    else:  # Use specified method
        if preferred_method == 'cash_flow':
            df = df[df['calculation_method'].isin(['cash_flow', 'both'])]
            rank_col = 'accrual_rank_cf'
            # Create the ranking column if it doesn't exist
            if 'accrual_rank_cf' not in df.columns:
                df['accrual_rank_cf'] = df.groupby('date')['accrual_ratio_cf'].rank(pct=True)
        elif preferred_method == 'balance_sheet':
            df = df[df['calculation_method'].isin(['balance_sheet', 'both'])]
            rank_col = 'accrual_rank_bs'
            # Create the ranking column if it doesn't exist
            if 'accrual_rank_bs' not in df.columns:
                df['accrual_rank_bs'] = df.groupby('date')['accrual_ratio_bs'].rank(pct=True)
        elif preferred_method == 'both':
            df = df[df['calculation_method'] == 'both']
            df['composite_rank'] = (df['accrual_rank_cf'] + df['accrual_rank_bs']) / 2
            rank_col = 'composite_rank'
    
    # Generate signals
    df['signal'] = 0
    df.loc[df[rank_col] <= long_threshold, 'signal'] = 1  # Long
    df.loc[df[rank_col] >= (1 - short_threshold), 'signal'] = -1  # Short
    
    return df

def main():
    # Example usage
    tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'JPM', 'JNJ', 'PG', 'V']
    
    # Get financial data
    print("Collecting financial data...")
    financial_data = []
    for ticker in tickers:
        data = get_financial_data(ticker)
        if data:
            financial_data.append(data)
    df = pd.DataFrame(financial_data)
    
    # Calculate accruals (auto-detects best method)
    print("\nCalculating accruals...")
    df = calculate_accruals(df)
    
    # Show calculation methods used
    print("\nAvailable columns in DataFrame:")
    print(df.columns.tolist())
    print("\nCalculation methods distribution:")
    print(df['calculation_method'].value_counts())

    """    
    # Run strategy with automatic method selection
    print("\nRunning strategy with auto method selection...")
    strategy_auto = accrual_strategy(df, preferred_method='auto')
    print(strategy_auto[['ticker', 'calculation_method', 'signal']])

    # Run strategy forcing balance sheet method when available
    print("\nRunning strategy with balance sheet method...")
    strategy_bs = accrual_strategy(df, preferred_method='balance_sheet')
    print(strategy_bs[['ticker', 'calculation_method', 'signal']])
    """


    # Run strategy forcing cash flow method when available
    print("\nRunning strategy with cash flow method...")
    strategy_cf = accrual_strategy(df, preferred_method='cash_flow')
    print(strategy_cf[['ticker', 'calculation_method', 'signal']])
    

if __name__ == "__main__":
    main()