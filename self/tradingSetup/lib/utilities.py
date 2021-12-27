def main():
    import matplotlib.pyplot as plt
    import warnings
    import yfinance as yf
    import pandas as pd
    print("All Lib imported")

    #setup
    plt.style.use('seaborn')
    plt.rcParams['figure.figsize'] = [16, 9]
    plt.rcParams['figure.dpi'] = 300
    warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ == "__main__":
    import os
    root_DIR = os.path.dirname(os.path.abspath(__file__))
    main()