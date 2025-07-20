"""
Identify growth and value stocks

"""
import sys
import os
# Add `src` to sys.path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(SRC_PATH)
print(SRC_PATH)
from utils.functions.yahooData import get_valuation_ratios 

def classify_by_valuation(pe, pb, pcf):
    """
    Classify a stock as 'value', 'growth', or 'blend' based on P/E, P/B, and P/CF ratios.

    Parameters:
        pe (float): Price-to-Earnings ratio
        pb (float): Price-to-Book ratio
        pcf (float): Price-to-Cash-Flow ratio

    Returns:
        str: 'value', 'growth', or 'blend'
    """

    # Define conservative thresholds (can be adjusted)
    value_thresholds = {
        'pe': 15,
        'pb': 1.5,
        'pcf': 10,
    }

    growth_thresholds = {
        'pe': 25,
        'pb': 3,
        'pcf': 20,
    }

    value_score = (
        (pe is not None and pe < value_thresholds['pe']) +
        (pb is not None and pb < value_thresholds['pb']) +
        (pcf is not None and pcf < value_thresholds['pcf'])
    )

    growth_score = (
        (pe is not None and pe > growth_thresholds['pe']) +
        (pb is not None and pb > growth_thresholds['pb']) +
        (pcf is not None and pcf > growth_thresholds['pcf'])
    )

    if value_score >= 2 and growth_score == 0:
        return 'value'
    elif growth_score >= 2 and value_score == 0:
        return 'growth'
    elif value_score == 1 and growth_score == 1:
        return 'blend'
    else:
        return 'unclear'

if __name__ == "__main__":
    x = get_valuation_ratios('AAPL')['AAPL']
    print(classify_by_valuation(x['pe_ratio'],x['pb_ratio'],x['pcf_ratio']))