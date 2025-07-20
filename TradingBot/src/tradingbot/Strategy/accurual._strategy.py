import pandas as pd
import numpy as np

def accrual_strategy(data, long_threshold=0.2, short_threshold=0.8):
    """
    Implements an accrual-based investment strategy:
    - Long stocks with low accruals (bottom 20%)
    - Short stocks with high accruals (top 20%)

    Parameters:
    -----------
    data : pd.DataFrame
        Must contain:
        - 'ticker' (stock identifier)
        - 'net_income' (Net Income)
        - 'cfo' (Cash Flow from Operations)
        - 'total_assets' (Total Assets, for scaling)
        - 'returns' (Future returns to evaluate strategy)
    
    long_threshold : float (default: 0.2)
        Percentile cutoff for low-accrual stocks (long portfolio).
    
    short_threshold : float (default: 0.8)
        Percentile cutoff for high-accrual stocks (short portfolio).

    Returns:
    --------
    dict
        - 'long_portfolio' (low-accrual stocks)
        - 'short_portfolio' (high-accrual stocks)
        - 'strategy_returns' (hypothetical long-short returns)
        - 'accruals' (accruals for all stocks)
    """
    # Calculate scaled accruals (Net Income - CFO) / Total Assets
    data['accruals'] = (data['net_income'] - data['cfo']) / data['total_assets']
    
    # Rank stocks by accruals (lowest = best)
    data['accrual_rank'] = data['accruals'].rank(pct=True)
    
    # Define long (low accruals) and short (high accruals) portfolios
    long_stocks = data[data['accrual_rank'] <= long_threshold]
    short_stocks = data[data['accrual_rank'] >= short_threshold]
    
    # Calculate equal-weighted portfolio returns
    long_return = long_stocks['returns'].mean()
    short_return = short_stocks['returns'].mean()
    strategy_return = long_return - short_return
    
    return {
        'long_portfolio': long_stocks,
        'short_portfolio': short_stocks,
        'strategy_returns': strategy_return,
        'accruals': data['accruals']
    }

# Example Usage
if __name__ == "__main__":
    # Generate sample data (replace with real data)
    np.random.seed(42)
    n_stocks = 100
    data = pd.DataFrame({
        'ticker': [f'STK{i}' for i in range(n_stocks)],
        'net_income': np.random.uniform(-10, 10, n_stocks),
        'cfo': np.random.uniform(-5, 15, n_stocks),
        'total_assets': np.random.uniform(100, 1000, n_stocks),
        'returns': np.random.normal(0.1, 0.2, n_stocks)  # Simulated future returns
    })
    
    # Run strategy
    results = accrual_strategy(data)
    
    # Print results
    print("Long Portfolio (Low Accruals):")
    print(results['long_portfolio'][['ticker', 'accruals', 'returns']].head())
    
    print("\nShort Portfolio (High Accruals):")
    print(results['short_portfolio'][['ticker', 'accruals', 'returns']].head())
    
    print(f"\nStrategy Return (Long-Short): {results['strategy_returns']:.2%}")