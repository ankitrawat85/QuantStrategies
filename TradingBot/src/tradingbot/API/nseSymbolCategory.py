"""

This script help to read  symbol from a file and write it to another file

"""
import pandas as pd
from pathlib import Path
import pandas as pd
import numpy as np
import re
import sys
import os

ROOT_DIR = os.path.abspath('/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot')

def read_symbol(ROOT_DIR=ROOT_DIR,file_path_from_root_directory = '/data/input',file_name = 'NSE_Market_List.csv'):
    if file_path_from_root_directory:
        ROOT_DIR = ROOT_DIR + file_path_from_root_directory + '/' + file_name
    
    return pd.read_csv( ROOT_DIR )


if __name__ == "__main__":
    x = read_symbol()
    print(x)