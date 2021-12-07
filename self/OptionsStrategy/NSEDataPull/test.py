from pynse import *
nse=Nse()

#print(nse.market_status())
#nse.info('SBIN')
#print(nse.get_quote('TCS', segment=Segment.FUT, expiry=dt.date( 2020, 6, 30 )))
x= nse.get_quote('HDFC', segment=Segment.OPT, optionType=OptionType.PE, strike=1800.)
print(nse.option_chain('INFY'))
#print(nse.option_chain('infy',expiry=dt.date(2021,12,30)))
#nse.get_hist('NIFTY 50', from_date=dt.date(2020,1,1),to_date=dt.date(2020,6,26))

from nsepy import get_history
from datetime import date

def datapulloptions():
    BankNifty_Opt = get_history(symbol="BANKNIFTY",
                                start=date(2020, 11, 1),
                                end=date(2021, 11, 28),
                                futures=False,
                                index=True,
                                expiry_date=date(2021, 12, 30),
                                option_type='CE',
                                strike_price=36000,
                                )

    print(BankNifty_Opt.columns)
datapulloptions()