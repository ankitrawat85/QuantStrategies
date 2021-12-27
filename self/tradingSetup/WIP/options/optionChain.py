from self.OptionsStrategy.NSEDataPull.NseRealtimeData  import  nseRealTime
import datetime
import numpy as np
'''Option Chain  Real time data '''
print("Option Chain  Real time data of specific expiry")
RealTimeOption = nseRealTime().OptionChain("NIFTY", option_expiry=datetime.date(2021, 12, 30), instrument="OPIDX")
RealTimeOption = RealTimeOption[RealTimeOption["OPEN_INT"] != 0]
RealTimeOption = RealTimeOption.dropna(axis =0)
print(RealTimeOption.columns)
print(RealTimeOption.head(1).to_csv("optioncs.csv"))
data_ = RealTimeOption.head(1)
print(data_.columns)
RealTimeOption = RealTimeOption[["Date", "Strike Price", "Expiry", "underlying", "identifier", "OPEN_INT", "changeinOpenInterest",
                      "pchangeinOpenInterest", "totalTradedVolume",
                      "Close", "Option Type"]]
