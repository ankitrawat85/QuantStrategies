"""
This Module identify momentum stocks
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ======================
# 1. DATA PREPARATION
# ======================
def load_and_preprocess_data(filepath):
    """
    Load daily price data and convert to monthly returns.
    Assumes CSV with columns: 'date', 'ticker1', 'ticker2', ...
    """
    # Load data
    daily_prices = pd.read_csv(filepath, parse_dates=['date'], index_col='date')
    
    # Resample to month-end prices
    monthly_prices = daily_prices.resample('M').last()
    
    # Calculate monthly returns (percentage change)
    monthly_returns = monthly_prices.pct_change().dropna()
    
    return monthly_returns

# ======================
# 2. MOMENTUM SIGNAL
# ======================
import pandas as pd

def calculate_momentum(daily_prices, lookback_months=12, skip_months=1, return_type='arithmetic'):
    """
    Calculate momentum from daily prices by first converting to monthly returns.
    
    Parameters:
        daily_prices (pd.Series/DataFrame): Daily price data (must have DateTimeIndex)
        lookback_months (int): Number of months for momentum calculation (default 12)
        skip_months (int): Months to skip at end (default 1)
        return_type (str): 'arithmetic' or 'log' returns (default 'arithmetic')
    
    Returns:
        pd.Series: Momentum values indexed by month-end dates
    """
    # Validate inputs
    if not isinstance(daily_prices.index, pd.DatetimeIndex):
        raise ValueError("Input must have DateTimeIndex")
    
    # Resample to monthly prices (using last trading day of month)
    monthly_prices = daily_prices.resample('M').last()
    
    # Calculate monthly returns
    if return_type == 'arithmetic':
        monthly_returns = monthly_prices.pct_change().dropna()
    elif return_type == 'log':
        monthly_returns = np.log(monthly_prices/monthly_prices.shift(1)).dropna()
    else:
        raise ValueError("return_type must be 'arithmetic' or 'log'")
    
    # Calculate momentum (sum of returns over lookback period)
    momentum = monthly_returns.rolling(lookback_months).sum().shift(skip_months)
    
    return momentum

# ======================
# 3. PORTFOLIO CONSTRUCTION
# ======================
def build_tsmom_portfolio(monthly_returns, momentum, 
                         long_threshold=0.8, short_threshold=0.2):
    """
    Constructs TSMOM portfolio:
    - Long top 20% momentum assets
    - Short bottom 20% momentum assets
    """
    # Rank assets by momentum (1=best)
    ranked = momentum.rank(axis=1, pct=True)
    
    # Create long/short masks
    long_positions = (ranked >= long_threshold).astype(int)
    short_positions = (ranked <= short_threshold).astype(int)
    
    # Calculate strategy returns
    long_returns = (long_positions.shift(1) * monthly_returns).mean(axis=1)
    short_returns = (short_positions.shift(1) * monthly_returns).mean(axis=1)
    strategy_returns = long_returns - short_returns
    
    return {
        'returns': strategy_returns,
        'long_positions': long_positions,
        'short_positions': short_positions,
        'momentum': momentum
    }

# ======================
# 4. PERFORMANCE ANALYSIS
# ======================
def analyze_performance(strategy_returns):
    """Calculates key performance metrics"""
    # Cumulative returns
    cumulative_returns = (1 + strategy_returns).cumprod()
    
    # Annualized Sharpe ratio
    sharpe = np.sqrt(12) * strategy_returns.mean() / strategy_returns.std()
    
    # Max drawdown
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    
    return {
        'cumulative_returns': cumulative_returns,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'annual_return': (cumulative_returns.iloc[-1] ** (12/len(cumulative_returns))) - 1
    }

# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    # 1. Load and preprocess data (replace with your file)
    # Example file format: CSV with 'date' column and price columns for each asset
    returns = load_and_preprocess_data('daily_prices.csv')
    
    # 2. Calculate momentum signals
    momentum = calculate_momentum(returns, lookback=12, skip_month=1)
    
    # 3. Build TSMOM portfolio
    results = build_tsmom_portfolio(returns, momentum)
    
    # 4. Analyze performance
    performance = analyze_performance(results['returns'])
    
    # ======================
    # OUTPUT RESULTS
    # ======================
    print(f"\nStrategy Performance:")
    print(f"Annualized Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {performance['max_drawdown']:.1%}")
    print(f"Annualized Return: {performance['annual_return']:.1%}")
    
    # Plot cumulative returns
    plt.figure(figsize=(10, 6))
    performance['cumulative_returns'].plot(title='TSMOM Strategy Cumulative Returns')
    plt.ylabel('Cumulative Return')
    plt.xlabel('Date')
    plt.grid(True)
    plt.show()