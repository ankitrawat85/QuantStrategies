"""
Technical Indicators Module
Contains classes for trend analysis, candle pattern recognition, and pivot point calculations
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Tuple

class TrendAnalyzer:
    """Class for analyzing market trends using various technical indicators"""
    
    @staticmethod
    def assess_trend(ohlc_df, n):
        """Assess the trend by analyzing each candle"""
        df = ohlc_df.copy()
        df["up"] = np.where(df["low"] >= df["low"].shift(1), 1, 0)
        df["dn"] = np.where(df["high"] <= df["high"].shift(1), 1, 0)
        
        if df["close"].iloc[-1] > df["open"].iloc[-1]:
            if df["up"][-1*n:].sum() >= 0.7*n:
                return "uptrend"
        elif df["open"].iloc[-1] > df["close"].iloc[-1]:
            if df["dn"][-1*n:].sum() >= 0.7*n:
                return "downtrend"
        return None
    
    @staticmethod
    def slope_with_trend(
            ohlc_df: pd.DataFrame,
            n: int,
            threshold: float = 5.0,
            price_type: str = "mid"
        ) -> Tuple[float, str, float]:
            """
            Calculate slope angle and classify trend direction with confidence.

            Args:
                ohlc_df (pd.DataFrame): DataFrame with columns: open, high, low, close
                n (int): Number of periods to analyze
                threshold (float): Angle threshold (in degrees) to classify trend direction
                price_type (str): Method for calculating price series. Options:
                                "mid"     = (open + close) / 2 [default]
                                "typical" = (high + low + close) / 3
                                "close"   = close price only

            Returns:
                Tuple[float, str, float]: 
                    - slope_angle (float): Slope angle in degrees
                    - trend_class (str): "Uptrend", "Downtrend", or "Sideways"
                    - confidence (float): R-squared value (0 to 1) indicating fit quality

            Example:
                slope, trend, r2 = slope_with_trend(df, 20, threshold=5.0, price_type="close")
                print(f"Slope: {slope:.2f}°, Trend: {trend}, R²: {r2:.2%}")
            """
            if len(ohlc_df) < n:
                raise ValueError(f"Need at least {n} periods, got {len(ohlc_df)}")

            df = ohlc_df.iloc[-n:].copy()

            # Choose y based on price_type
            if price_type == "mid":
                y = ((df["open"] + df["close"]) / 2).values
            elif price_type == "typical":
                y = ((df["high"] + df["low"] + df["close"]) / 3).values
            elif price_type == "close":
                y = df["close"].values
            else:
                raise ValueError("Invalid price_type. Choose from: 'mid', 'typical', 'close'.")

            x = np.arange(n)

            # Scale y (avoid division by zero for constant price)
            y_range = y.max() - y.min()
            y_scaled = np.zeros_like(y) if y_range == 0 else (y - y.min()) / y_range

            x_scaled = (x - x.min()) / (x.max() - x.min())
            x_scaled = sm.add_constant(x_scaled)  # Add intercept term

            # Linear regression
            model = sm.OLS(y_scaled, x_scaled)
            results = model.fit()

            slope_angle = np.rad2deg(np.arctan(results.params[-1]))
            confidence = results.rsquared

            # Classify trend
            if slope_angle > threshold:
                trend_class = "Uptrend"
            elif slope_angle < -threshold:
                trend_class = "Downtrend"
            else:
                trend_class = "Sideways"

            return slope_angle, trend_class, confidence

    @staticmethod
    def calculate_adx(df, n):
        """Calculate Average Directional Index (ADX)"""
        df2 = df.copy()
        df2['H-L'] = abs(df2['high'] - df2['low'])
        df2['H-PC'] = abs(df2['high'] - df2['close'].shift(1))
        df2['L-PC'] = abs(df2['low'] - df2['close'].shift(1))
        df2['TR'] = df2[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        
        # Calculate +DM and -DM
        df2['DMplus'] = np.where(
            (df2['high'] - df2['high'].shift(1)) > (df2['low'].shift(1) - df2['low']),
            df2['high'] - df2['high'].shift(1), 0)
        df2['DMplus'] = np.where(df2['DMplus'] < 0, 0, df2['DMplus'])
        
        df2['DMminus'] = np.where(
            (df2['low'].shift(1) - df2['low']) > (df2['high'] - df2['high'].shift(1)),
            df2['low'].shift(1) - df2['low'], 0)
        df2['DMminus'] = np.where(df2['DMminus'] < 0, 0, df2['DMminus'])
        
        # Calculate smoothed values
        TRn = []
        DMplusN = []
        DMminusN = []
        TR = df2['TR'].tolist()
        DMplus = df2['DMplus'].tolist()
        DMminus = df2['DMminus'].tolist()
        
        for i in range(len(df2)):
            if i < n:
                TRn.append(np.NaN)
                DMplusN.append(np.NaN)
                DMminusN.append(np.NaN)
            elif i == n:
                TRn.append(df2['TR'].rolling(n).sum().tolist()[n])
                DMplusN.append(df2['DMplus'].rolling(n).sum().tolist()[n])
                DMminusN.append(df2['DMminus'].rolling(n).sum().tolist()[n])
            elif i > n:
                TRn.append(TRn[i-1] - (TRn[i-1]/n) + TR[i])
                DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/n) + DMplus[i])
                DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/n) + DMminus[i])
        
        df2['TRn'] = np.array(TRn)
        df2['DMplusN'] = np.array(DMplusN)
        df2['DMminusN'] = np.array(DMminusN)
        
        # Calculate DI+ and DI-
        df2['DIplusN'] = 100 * (df2['DMplusN'] / df2['TRn'])
        df2['DIminusN'] = 100 * (df2['DMminusN'] / df2['TRn'])
        df2['DIdiff'] = abs(df2['DIplusN'] - df2['DIminusN'])
        df2['DIsum'] = df2['DIplusN'] + df2['DIminusN']
        df2['DX'] = 100 * (df2['DIdiff'] / df2['DIsum'])
        
        # Calculate ADX
        ADX = []
        DX = df2['DX'].tolist()
        
        for j in range(len(df2)):
            if j < 2*n-1:
                ADX.append(np.NaN)
            elif j == 2*n-1:
                ADX.append(df2['DX'][j-n+1:j+1].mean())
            elif j > 2*n-1:
                ADX.append(((n-1)*ADX[j-1] + DX[j])/n)
        
        df2['ADX'] = np.array(ADX)
        return df2['ADX']

    @staticmethod
    def calculate_atr(df, n):
        """Calculate Average True Range"""
        df = df.copy()
        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        df['ATR'] = df['TR'].ewm(com=n, min_periods=n).mean()
        return df['ATR']

    @staticmethod
    def calculate_supertrend(df, n, m):
        """Calculate Supertrend indicator"""
        df = df.copy()
        df['ATR'] = TrendAnalyzer.calculate_atr(df, n)
        df["B-U"] = ((df['high'] + df['low'])/2) + m*df['ATR'] 
        df["B-L"] = ((df['high'] + df['low'])/2) - m*df['ATR']
        df["U-B"] = df["B-U"]
        df["L-B"] = df["B-L"]
        
        ind = df.index
        for i in range(n, len(df)):
            if df['close'][i-1] <= df['U-B'][i-1]:
                df.loc[ind[i], 'U-B'] = min(df['B-U'][i], df['U-B'][i-1])
            else:
                df.loc[ind[i], 'U-B'] = df['B-U'][i]    
        
        for i in range(n, len(df)):
            if df['close'][i-1] >= df['L-B'][i-1]:
                df.loc[ind[i], 'L-B'] = max(df['B-L'][i], df['L-B'][i-1])
            else:
                df.loc[ind[i], 'L-B'] = df['B-L'][i]  
        
        df['Strend'] = np.nan
        for test in range(n, len(df)):
            if (df['close'][test-1] <= df['U-B'][test-1] and 
                df['close'][test] > df['U-B'][test]):
                df.loc[ind[test], 'Strend'] = df['L-B'][test]
                break
            if (df['close'][test-1] >= df['L-B'][test-1] and 
                df['close'][test] < df['L-B'][test]):
                df.loc[ind[test], 'Strend'] = df['U-B'][test]
                break
        
        for i in range(test+1, len(df)):
            if (df['Strend'][i-1] == df['U-B'][i-1] and 
                df['close'][i] <= df['U-B'][i]):
                df.loc[ind[i], 'Strend'] = df['U-B'][i]
            elif (df['Strend'][i-1] == df['U-B'][i-1] and 
                  df['close'][i] >= df['U-B'][i]):
                df.loc[ind[i], 'Strend'] = df['L-B'][i]
            elif (df['Strend'][i-1] == df['L-B'][i-1] and 
                  df['close'][i] >= df['L-B'][i]):
                df.loc[ind[i], 'Strend'] = df['L-B'][i]
            elif (df['Strend'][i-1] == df['L-B'][i-1] and 
                  df['close'][i] <= df['L-B'][i]):
                df.loc[ind[i], 'Strend'] = df['U-B'][i]
        
        return df['Strend']

    @staticmethod
    def calculate_macd(df, a=12, b=26, c=9):
        """Calculate Moving Average Convergence Divergence (MACD)"""
        df = df.copy()
        df["MA_Fast"] = df["close"].ewm(span=a, min_periods=a).mean()
        df["MA_Slow"] = df["close"].ewm(span=b, min_periods=b).mean()
        df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
        df["Signal"] = df["MACD"].ewm(span=c, min_periods=c).mean()
        df.dropna(inplace=True)
        return df

    @staticmethod
    def update_macd_crossover(macd, ticker):
        """Update MACD crossover status"""
        global macd_xover
        if macd["MACD"][-1] > macd["Signal"][-1]:
            macd_xover[ticker] = "bullish"
        elif macd["MACD"][-1] < macd["Signal"][-1]:
            macd_xover[ticker] = "bearish"

    @staticmethod
    def calculate_renko_brick_size(ohlc_data, atr_period=200, multiplier=1.5):
        """
        Calculate optimal brick size for Renko charts based on ATR (Average True Range).
        
        Parameters:
            ohlc_data (DataFrame): Pandas DataFrame containing OHLC data with columns:
                                ['open', 'high', 'low', 'close']
            atr_period (int): Period for ATR calculation (default: 200)
            multiplier (float): Multiplier for ATR to determine brick size (default: 1.5)
        
        Returns:
            int: The calculated brick size, constrained between 1 and 10
            
        Raises:
            ValueError: If input data is invalid or insufficient
            
        Notes:
            - Uses multiplier x the ATR as base calculation
            - Brick size is constrained between 1 and 10
            - Requires at least 'atr_period' number of data points
        """
        # Validate input data
        if not isinstance(ohlc_data, pd.DataFrame):
            raise ValueError("ohlc_data must be a pandas DataFrame")
        
        required_columns = {'open', 'high', 'low', 'close'}
        if not required_columns.issubset(ohlc_data.columns):
            missing = required_columns - set(ohlc_data.columns)
            raise ValueError(f"Missing required columns: {missing}")
        
        if len(ohlc_data) < atr_period:
            raise ValueError(f"Insufficient data points. Need at least {atr_period}, got {len(ohlc_data)}")
    
        try:
            # Calculate ATR
            atr_values = TrendAnalyzer.calculate_atr(ohlc_data, atr_period)
            
            if atr_values.empty or pd.isna(atr_values.iloc[-1]):
                raise ValueError("ATR calculation returned invalid results")
                
            # Get the most recent ATR value
            current_atr = atr_values.iloc[-1]
            
            # Calculate brick size with multiplier and rounding
            brick_size = round(multiplier * current_atr, 0)
            
            # Constrain between 1 and 10
            constrained_size = max(1, min(10, brick_size))
            
            return int(constrained_size)
            
        except Exception as e:
            raise ValueError(f"Error calculating Renko brick size: {str(e)}")

class CandlePatternRecognizer:
    """Class for recognizing various candlestick patterns"""
    
    @staticmethod
    def identify_maru_bozu(ohlc_df):    
        """Identify Maru Bozu (strong trend) candles"""
        df = ohlc_df.copy()
        avg_candle_size = abs(df["close"] - df["open"]).median()
        
        df["h-c"] = df["high"] - df["close"]
        df["l-o"] = df["low"] - df["open"]
        df["h-o"] = df["high"] - df["open"]
        df["l-c"] = df["low"] - df["close"]
        
        df["maru_bozu"] = np.where(
            (df["close"] - df["open"] > 2*avg_candle_size) & 
            (df[["h-c", "l-o"]].max(axis=1) < 0.005*avg_candle_size),
            "maru_bozu_green",
            np.where(
                (df["open"] - df["close"] > 2*avg_candle_size) & 
                (abs(df[["h-o", "l-c"]]).max(axis=1) < 0.005*avg_candle_size),
                "maru_bozu_red", 
                False
            )
        )
        
        df.drop(["h-c", "l-o", "h-o", "l-c"], axis=1, inplace=True)
        return df

    @staticmethod
    def identify_doji(ohlc_df):    
        """Identify Doji candles"""
        df = ohlc_df.copy()
        avg_candle_size = abs(df["close"] - df["open"]).median()
        df["doji"] = abs(df["close"] - df["open"]) <= (0.05 * avg_candle_size)
        return df

    @staticmethod
    def identify_hammer(ohlc_df):    
        """Identify Hammer candles"""
        df = ohlc_df.copy()
        df["hammer"] = (
            ((df["high"] - df["low"]) > 3*(df["open"] - df["close"])) & 
            ((df["close"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6) & 
            ((df["open"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6)) & (abs(df["close"] - df["open"]) > 0.1 * (df["high"] - df["low"]))
        return df

    @staticmethod
    def identify_shooting_star(ohlc_df):    
        """Identify Shooting Star candles"""
        df = ohlc_df.copy()
        df["sstar"] = (
            ((df["high"] - df["low"]) > 3*(df["open"] - df["close"])) & 
            ((df["high"] - df["close"])/(.001 + df["high"] - df["low"]) > 0.6) & 
            ((df["high"] - df["open"])/(.001 + df["high"] - df["low"]) > 0.6)) & (abs(df["close"] - df["open"]) > 0.1 * (df["high"] - df["low"]))
        return df

    @staticmethod
    def get_candle_type(ohlc_df, n: int = 7):
        """Get candle patterns from the last n rows of ohlc_df."""
        tail = ohlc_df.tail(n)
        patterns = {}

        for i, row in tail.iterrows():
            pats = []

            if CandlePatternRecognizer.identify_doji(tail).loc[i, "doji"]:
                pats.append("doji")

            maru = CandlePatternRecognizer.identify_maru_bozu(tail).loc[i, "maru_bozu"]
            if maru in ["maru_bozu_green", "maru_bozu_red"]:
                pats.append(maru)

            if CandlePatternRecognizer.identify_shooting_star(tail).loc[i, "sstar"]:
                pats.append("shooting_star")

            if CandlePatternRecognizer.identify_hammer(tail).loc[i, "hammer"]:
                pats.append("hammer")

            if pats:
                patterns[i] = pats

        return patterns


    @staticmethod
    def identify_pattern(shorter_df, long_period_df):
        """Identify candlestick patterns anchored to the date of the last detected pattern within last n bars."""
        try:
            ohlc_df = shorter_df
            ohlc_day = long_period_df

            # ---- 1) Detect patterns in last 5 rows ----
            candle_type_out = CandlePatternRecognizer.get_candle_type(ohlc_df, n=5)

            # ---- 2) Pick anchor date (latest pattern in window) ----
            anchor_ts = None
            anchor_patterns = []

            if isinstance(candle_type_out, dict) and len(candle_type_out) > 0:
                anchor_ts = max(candle_type_out.keys())
                val = candle_type_out[anchor_ts]
                anchor_patterns = [val] if isinstance(val, str) else list(val)
            elif isinstance(candle_type_out, (list, tuple, set)) and len(candle_type_out) > 0:
                anchor_ts = ohlc_df.index[-1]
                anchor_patterns = list(candle_type_out)
            elif isinstance(candle_type_out, str) and candle_type_out:
                anchor_ts = ohlc_df.index[-1]
                anchor_patterns = [candle_type_out]
            else:
                return {"date": None, "significance": "low", "pattern": None}

            if anchor_ts is None:
                anchor_ts = ohlc_df.index[-1]

            # ---- 3) Extract OHLC at anchor ----
            anchor_idx = ohlc_df.index.get_loc(anchor_ts)
            row = ohlc_df.iloc[anchor_idx]
            last_open, last_close, last_high, last_low = row["open"], row["close"], row["high"], row["low"]

            avg_candle_size = (ohlc_df["close"] - ohlc_df["open"]).abs().median()

            # ---- 4) Support/Resistance significance ----
            try:
                sup, res = PivotCalculator.calculate_support_resistance(ohlc_df.iloc[:anchor_idx+1], ohlc_day)
            except Exception:
                sup, res = None, None

            significance = "low"
            if sup is not None and (sup - 1.5 * avg_candle_size) < last_close < (sup + 1.5 * avg_candle_size):
                significance = "HIGH"
            if res is not None and (res - 1.5 * avg_candle_size) < last_close < (res + 1.5 * avg_candle_size):
                significance = "HIGH"

            # ---- 5) Trend prior to anchor ----
            try:
                trend = TrendAnalyzer.assess_trend(ohlc_df.iloc[:anchor_idx, :], 7) if anchor_idx > 0 else 0
            except Exception:
                trend = 0

            # ---- 6) Decide final pattern ----
            pats = set(anchor_patterns)
            pattern = None

            if "doji" in pats and anchor_idx > 0:
                prev_close = ohlc_df["close"].iloc[anchor_idx-1]
                if (last_close > prev_close) and (last_close > last_open):
                    pattern = "doji_bullish"
                elif (last_close < prev_close) and (last_close < last_open):
                    pattern = "doji_bearish"

            if pattern is None:
                if "maru_bozu_green" in pats: pattern = "maru_bozu_bullish"
                elif "maru_bozu_red" in pats: pattern = "maru_bozu_bearish"

            if pattern is None and "hammer" in pats:
                if trend == 1: pattern = "hanging_man_bearish"
                elif trend == -1: pattern = "hammer_bullish"

            if pattern is None and "shooting_star" in pats and trend == 1:
                pattern = "shooting_star_bearish"

            if pattern is None and "doji" in pats and anchor_idx > 0:
                prev = ohlc_df.iloc[anchor_idx-1]
                if (trend == 1 and last_high < prev["close"] and last_low > prev["open"]):
                    pattern = "harami_cross_bearish"
                elif (trend == -1 and last_high < prev["open"] and last_low > prev["close"]):
                    pattern = "harami_cross_bullish"

            if pattern is None and "doji" not in pats and anchor_idx > 0:
                prev = ohlc_df.iloc[anchor_idx-1]
                if trend == 1 and (last_open > prev["high"]) and (last_close < prev["low"]):
                    pattern = "engulfing_bearish"
                elif trend == -1 and (last_close > prev["high"]) and (last_open < prev["low"]):
                    pattern = "engulfing_bullish"

            return {"date": anchor_ts, "significance": significance, "pattern": pattern}

        except Exception as e:
            print(f"Error {e}")
            return {"date": None, "significance": "low", "pattern": None}


class PivotCalculator:
    """Class for calculating pivot points and support/resistance levels"""
    
    @staticmethod
    def calculate_pivot_levels(ohlc_day):    
        """Calculate pivot point and support/resistance levels"""
        high = round(ohlc_day["high"].iloc[-1], 2)
        low = round(ohlc_day["low"].iloc[-1], 2)
        close = round(ohlc_day["close"].iloc[-1], 2)
        
        pivot = round((high + low + close)/3, 2)
        r1 = round((2*pivot - low), 2)
        r2 = round((pivot + (high - low)), 2)
        r3 = round((high + 2*(pivot - low)), 2)
        s1 = round((2*pivot - high), 2)
        s2 = round((pivot - (high - low)), 2)
        s3 = round((low - 2*(high - pivot)), 2)
        
        return (pivot, r1, r2, r3, s1, s2, s3)

    @staticmethod
    def calculate_support_resistance(ohlc_df: pd.DataFrame, ohlc_day: dict):
        """
        Calculate the closest resistance (above) and support (below) levels,
        extrapolating synthetic levels when the current reference level lies outside
        the range of standard pivots.

        Args:
            ohlc_df: Intraday OHLC DataFrame with at least one row. Expected columns: ['open','high','low','close'].
            ohlc_day: Daily OHLC as a dict-like with keys 'open','high','low','close' (used for pivot calculation).

        Returns:
            (closest_resistance, closest_support): resistance is nearest level above the current level;
                support is nearest level below. If outside pivot extremes, synthetic levels are extrapolated.
        """
        if ohlc_df.empty:
            return None, None

        # Compute reference level from latest intraday candle
        try:
            latest = ohlc_df.iloc[-1]
            level = (
                (latest["close"] + latest["open"]) / 2
                + (latest["high"] + latest["low"]) / 2
            ) / 2
        except Exception as e:
            print(f"[SupportResistance] failed to compute base level: {e}")
            return None, None

        # Compute pivot levels
        try:
            p, r1, r2, r3, s1, s2, s3 = PivotCalculator.calculate_pivot_levels(ohlc_day)
            levels = {
                "p": p,
                "r1": r1,
                "r2": r2,
                "r3": r3,
                "s1": s1,
                "s2": s2,
                "s3": s3
            }
        except Exception as e:
            print(f"[SupportResistance] pivot level calculation error: {e}")
            return None, None

        # Differences: positive means pivot is below level (support candidate), negative means pivot is above level (resistance candidate)
        try:
            diff_series = pd.Series({k: level - v for k, v in levels.items()})

            support_candidates = diff_series[diff_series > 0]  # pivots below level
            resistance_candidates = diff_series[diff_series < 0]  # pivots above level

            closest_support = None
            closest_resistance = None

            if not support_candidates.empty:
                sup_key = support_candidates.idxmin()  # smallest positive diff => nearest below
                closest_support = levels[sup_key]

            if not resistance_candidates.empty:
                res_key = resistance_candidates.idxmax()  # largest negative (closest above)
                closest_resistance = levels[res_key]

            # Extrapolate synthetic resistance if level is above all pivots (no native resistance)
            if closest_resistance is None and closest_support is not None:
                gap = level - closest_support
                closest_resistance = level + gap  # symmetric projection above level

            # Extrapolate synthetic support if level is below all pivots (no native support)
            if closest_support is None and closest_resistance is not None:
                gap = closest_resistance - level
                closest_support = level - gap  # symmetric projection below level

            return closest_resistance, closest_support

        except Exception as e:
            print(f"[SupportResistance] error selecting nearest levels: {e}")
            return None, None

    @staticmethod
    def calculate_slope(ohlc_df, n):
        """Calculate the slope of regression line for n consecutive points"""
        df = ohlc_df.iloc[-1*n:,:]
        y = ((df["open"] + df["close"])/2).values
        x = np.array(range(n))
        
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        
        model = sm.OLS(y_scaled, x_scaled)
        results = model.fit()
        slope = np.rad2deg(np.arctan(results.params[-1]))
        
        return slope
