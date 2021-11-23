import pandas as pd
import numpy  as  np

## Import Data
class FX():

    def __init__(self,currency):
        self.currency = currency

    def PullcurrenyData(self):
        fx_df = pd.read_csv("G10_FX_HI_LO_CLOSE.csv", skiprows=0, header=None)
        i = 1
        print("list of Currencies:")
        while (i < fx_df.shape[1]):
            columns_list = [0]
            columns_list.append(i)
            for j in range(i + 1, fx_df.shape[1], 1):
                if (fx_df[i][0] == fx_df[j][0]):
                    columns_list.append(j)
                    if (j == fx_df.shape[1] - 1):
                        print(fx_df[i][0])
                        df_ = pd.read_csv('G10_FX_HI_LO_CLOSE.csv', usecols=columns_list, skiprows=1, header=0)
                        df_["Dates"] = pd.to_datetime(df_["Dates"])
                        df_.set_index("Dates")
                        df_.columns = ["Dates", "High", "Low", "Last"]
                        df_.to_csv(f'FX_{fx_df[i][0]}.csv')
                        break

                else:
                    print(fx_df [i][0])
                    df_ = pd.read_csv('G10_FX_HI_LO_CLOSE.csv', usecols=columns_list, skiprows=1, header=0)
                    df_["Dates"] = pd.to_datetime(df_["Dates"])
                    df_.set_index("Dates")
                    df_.columns = ["Dates", "High", "Low", "Last"]
                    df_.to_csv(f'FX_{fx_df [i][0]}.csv')
                    break

            if (j == fx_df .shape[1] - 1):
                break
            else:
                i = j
                columns_list.clear()

        FX_SEK = pd.read_csv("FX_SEK.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_DKK = pd.read_csv("FX_DKK.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_CHF = pd.read_csv("FX_CHF.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_NZD = pd.read_csv("FX_NZD.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_AUD = pd.read_csv("FX_AUD.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_CAD = pd.read_csv("FX_CAD.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_GBP = pd.read_csv("FX_GBP.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_JPY = pd.read_csv("FX_EUR.csv", skiprows=0, index_col="Dates").iloc[:, 1:]
        FX_EUR = pd.read_csv("FX_EUR.csv", skiprows=0, index_col="Dates").iloc[:, 1:]

