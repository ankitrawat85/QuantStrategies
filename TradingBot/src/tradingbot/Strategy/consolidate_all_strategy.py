# Imports
from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer, TrendAnalyzer
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
from tradingbot.Strategy.momentum import calculate_momentum
from tradingbot.API.nseSymbolCategory import read_symbol#

#strategy(symbol, shorter_df ,long_period_df)
#        (symbol, ohlc_day_df, min_df=None  )


def generate_trade_signal(symbol, shorter_df, long_period_df=None,
                          momentum_threshold=0.05, lookback_months=4, momentum_comparison=">"):
    """
    Consolidates candlestick, trend, and momentum logic into a single signal.

    Args:
        symbol: Stock symbol (str)
        ohlc_day_df: Daily OHLC DataFrame (minimum ~8 rows)
        min_df: Minute DataFrame (optional)
        momentum_threshold: float, for momentum
        lookback_months: int, for momentum lookback
        momentum_comparison: str, ">" or "<"

    Returns:
        int: 1 (Buy), -1 (Sell), 0 (Hold)
    """
    # --- 1. Candlestick pattern/trend logic ---
    if len(long_period_df) < 8:
        return 0

    pattern_info = CandlePatternRecognizer.identify_pattern(shorter_df, long_period_df)
    pattern = pattern_info.get("pattern")
    significance = pattern_info.get("significance")

    slope, trend, confidence = TrendAnalyzer.slope_with_trend(long_period_df, n=7)

    # --- 2. Momentum logic ---
    try:
        momentum_df = calculate_momentum(
            long_period_df[['close', 'timestamp']].set_index('timestamp'),
            lookback_months=lookback_months
        )
        if momentum_df.empty or 'close' not in momentum_df.columns:
            momentum = None
        else:
            momentum = momentum_df.iloc[-1].close
    except Exception as e:
        print(f"{symbol} - Momentum calculation error: {e}")
        momentum = None

    # --- 3. Signal rules (customize logic as needed) --


    # Buy: bullish candle, high significance, uptrend, AND strong momentum
    if (
        significance == "HIGH" and
        pattern in ("hammer_bullish", "maru_bozu_bullish", "engulfing_bullish", "doji_bullish", "harami_cross_bullish") and
        trend == "Uptrend" 
        and
        momentum is not None and
        (momentum > momentum_threshold)
        
    ):
        print(f" BUY ---> symbol : {symbol} , slope : {slope},trend : {trend},confidence : {confidence},pattern:{pattern} , momentum : {momentum}")
        return 1

    # Sell: bearish candle, high significance, downtrend, AND weak momentum
    if (
        significance == "HIGH" and
        pattern in ("shooting_star_bearish", "maru_bozu_bearish", "engulfing_bearish", "doji_bearish", "harami_cross_bearish", "hanging_man_bearish") and
        trend == "Downtrend" 
        and
        momentum is not None and
        (momentum < -momentum_threshold)
        
    ):
        print(f" SELL ---> symbol : {symbol} , slope : {slope},trend : {trend},confidence : {confidence},pattern:{pattern} , momentum : {momentum}")
        return -1
    #print(f"symbol : {symbol} , slope : {slope},trend : {trend},confidence : {confidence},pattern:{pattern}")
    return 0
