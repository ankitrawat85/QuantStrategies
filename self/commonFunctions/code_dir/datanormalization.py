import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class normalization():

    def __init__(self,df_ :pd.DataFrame):
        self.df_ = df_

    def normalize_z_Score(self):
        std_scaler = StandardScaler()
        return std_scaler.fit_transform(np.array(self.df_).reshape(-1,1))


