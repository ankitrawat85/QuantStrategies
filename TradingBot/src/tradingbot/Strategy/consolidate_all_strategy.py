# Imports
from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer, TrendAnalyzer
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
from tradingbot.Strategy.momentum import calculate_momentum
from tradingbot.API.nseSymbolCategory import read_symbol#

#strategy(symbol, shorter_df ,long_period_df)
#        (symbol, ohlc_day_df, min_df=None  )


def generate_minute_trade_signal(symbol, shorter_df, long_period_df=None,monthly_period=None,
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

    # Buy: bullish candle, high significance, uptrend, AND strong momentum
    if (
        significance == "HIGH" and
        pattern in ("hammer_bullish", "maru_bozu_bullish", "engulfing_bullish", "doji_bullish", "harami_cross_bullish") 
        #and
        #trend == "Uptrend" 
        
    ):
        print(f"    [Lowest TimeFrame] : BUY ---> symbol : {symbol} , slope : {slope},trend : {trend},confidence : {confidence},pattern:{pattern} ")
        return 1,pattern,significance 

    # Sell: bearish candle, high significance, downtrend, AND weak momentum
    if (
        significance == "HIGH" and
        pattern in ("shooting_star_bearish", "maru_bozu_bearish", "engulfing_bearish", "doji_bearish", "harami_cross_bearish", "hanging_man_bearish")
        
    ):
        print(f"    [Lowest TimeFrame] : SELL ---> symbol : {symbol} , slope : {slope},trend : {trend},confidence : {confidence},pattern:{pattern} ")
        return -1,pattern,significance
    return 0,None,None



def generate_trade_signal_stage(
    symbol,
    short_win,          # equivalent to your `shorter_df`
    long_win,           # equivalent to `long_period_df`
    monthly_win,        # equivalent to `monthly_period`
    momentum_threshold: float = 0.05,
    lookback_months: int = 4,
    momentum_comparison: str = ">",
    significaneRequired  : bool = False,
    **kwargs
):
    """
    Pipeline-style wrapper. Returns (signal, pattern, significance, pass_symbol).
    pass_symbol is True when the symbol survives to next stage (here: any non-zero signal).
    """
    signal = 0
    pattern = None
    significance = None
    pass_symbol = False

    # Require enough history
    if long_win is None or len(long_win) < 8:
        return 0, None, None, False

    # --- 1. Candlestick / trend logic ---
    try:
        
        Monthly_slope, Monthly_trend, Monthly_confidence = TrendAnalyzer.slope_with_trend(monthly_win, threshold=6, n=6)
        weekly_slope, weekly_trend, weekly_confidence = TrendAnalyzer.slope_with_trend(long_win, n=4)

        weekly_pattern_info = CandlePatternRecognizer.identify_pattern(long_win, monthly_win)
        weekly_pattern = weekly_pattern_info.get("pattern")
        weekly_significance = weekly_pattern_info.get("significance")
        
        daily_pattern_info = CandlePatternRecognizer.identify_pattern(short_win, long_win)
        daily_pattern = daily_pattern_info.get("pattern")
        daily_significance = daily_pattern_info.get("significance")
    
    except Exception as e:
        print(f"Error in generate_trade_signal_stage: {e}")
        pass

    # --- 2. Momentum logic ---
    momentum = None
    try:
        momentum_df = calculate_momentum(
            long_win[["close", "timestamp"]].set_index("timestamp"),
            lookback_months=lookback_months
        )
        if not momentum_df.empty and "close" in momentum_df.columns:
            momentum = momentum_df.iloc[-1].close
    except Exception as e:
        print(f"{symbol} - Momentum calculation error: {e}")
        momentum = None

    # --- 3. Signal rules ---
    bullish_patterns = (
        "hammer_bullish",
        "maru_bozu_bullish",
        "engulfing_bullish",
        "doji_bullish",
        "harami_cross_bullish",
    )
    bearish_patterns = (
        "shooting_star_bearish",
        "maru_bozu_bearish",
        "engulfing_bearish",
        "doji_bearish",
        "harami_cross_bearish",
        "hanging_man_bearish",
    )

    if (
        weekly_significance == "HIGH" and
        Monthly_trend == "Uptrend"and
        Monthly_slope > 45 and
        weekly_trend == "Uptrend"
        and weekly_pattern in bullish_patterns
        #and momentum is not None
        and ((momentum > momentum_threshold) if momentum_comparison == ">" else (momentum < momentum_threshold))
    ):
        signal = 1
        pattern = None
        significance = None
        pass_symbol = True
        return signal, pattern, significance, pass_symbol

    if (
        Monthly_trend == "Downtrend" and
        weekly_trend == "Downtrend"and
        Monthly_slope < -30
        and daily_pattern in bearish_patterns
        and momentum is not None
        and (momentum < -momentum_threshold)
    ):
        signal = -1
        pattern = None
        significance = None
        pass_symbol = True
        return signal, pattern, significance, pass_symbol

    # No signal
    return 0, None, None, False
