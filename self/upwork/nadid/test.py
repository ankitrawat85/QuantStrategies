import pandas
import pandas as pd
import numpy as np
portfolio =  pd.DataFrame(columns=["portfolioStocksPosition", "PNL", "MTM"])

df=pd.DataFrame(np.zeros([1,3]),columns=["portfolioStocksPosition", "PNL", "MTM"])

print(df)