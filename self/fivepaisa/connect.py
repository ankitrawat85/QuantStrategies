import time

import pandas as pd
from py5paisa import FivePaisaClient

from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, AHPlaced
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)
'''
class Exchange(Enum):

    NSE = "N"
    BSE = "B"
    MCX = "M"

class ExchangeSegment(Enum):

    CASH = "C"
    DERIVATIVE = "D"
    CURRENCY = "U"

class OrderType(Enum):

    BUY = "BUY"
    SELL = "SELL"

class OrderValidity(Enum):

    DAY = 0
    GTD = 1
    GTC = 2
    IOC = 3
    EOS = 4
    FOK = 6


class AHPlaced(Enum):

    AFTER_MARKET_CLOSED = "Y"
    NORMAL_ORDER = "N"
'''
cred={
    "APP_NAME":"5P57885942",
    "APP_SOURCE":"8323",
    "USER_ID":"Rk1wbRWYJvN",
    "PASSWORD":"JV0TKyvofCD",
    "USER_KEY":"hCIPlIOuIjNuVJpo3nz5oOZlLqWpeQFe",
    "ENCRYPTION_KEY":"JEOoQHMs1EqhVUbiOXaK6Wcw2mrcde5L"
    }

## Historical data

class fivepaisa:
    def connection(self):
        return FivePaisaClient(email="ankit4685@gmail.com", passwd="Discover@1987", dob="19850604", cred=cred)
if __name__ == "__main__":
    client = fivepaisa().connection()
    client.login()
    #data = client.historical_data('N', 'C', 1594, '1m', '2022-01-04', '2022-01-05')
    data = client.historical_data('N', 'D', '119118', '1m', '2022-01-04', '2022-01-17')
    req_list_ = [{"Exch": 'N', "ExchType": 'D', "Symbol": 1594}]
    df_ = client.fetch_market_feed(req_list_)
    print(df_)

    data["Datetime"] = pd.to_datetime(data["Datetime"])
    data.set_index("Datetime", inplace=True)
    print(data)
    print("Derivaitve Data")
    ## FETCH Live Market Feed
    #119118 - 'INFY 27 Jan 2022 CE 1940.00'
    #119119 - 'INFY 27 Jan 2022 PE 1940.00'

    req_list_ = [{"Exch": "N", "ExchType": "D", "Symbol": "INFY 27 Jan 2022 CE 1940.00", "Expiry": "20220127",
                  "StrikePrice": "17600", "OptionType": "CE"},{"Exch": "N", "ExchType": "D", "Symbol": "INFY 27 Jan 2022 PE 1940.00", "Expiry": "20220127",
                  "StrikePrice": "17600", "OptionType": "PE"}]
    req_list_ = [{"Exch": "N", "ExchType": "C", "Symbol": "INFY"}]
    data1 = client.fetch_market_feed(req_list_)
    print(data1)

    ## FETCH Live Market Feed
    print (client.holdings())
    print(client.margin())
    print(client.positions())
    print(client.order_book())

    #client.cancel_order(order_type = 'B',script_code = '',exchange='N',exchange_segment='D',exch_order_id="625061081")
    client.cancel_order(exchange='N', exchange_segment='D',exch_order_id='1000000046733676')
    client.cancel_order(exchange='N', exchange_segment='D', exch_order_id="625061081")


    ## Fetch Data
    orderbook =  client.order_book()[-1]
    orderbook = pd.DataFrame.from_dict([orderbook])
    print(orderbook.columns)
    print(orderbook[["OrderStatus","Reason"]])
    try:
        tradebook = client.get_tradebook()[-1]
    except:
        tradebook = pd.DataFrame.from_dict([client.get_tradebook()])


    print(tradebook)

    ## placing Order
    ## Order Booking
    infy = Order(order_type='S', exchange='N', exchange_segment='D', scrip_code=119118, quantity=300, price=25.55,is_intraday=False,ioc_order=True,ahplaced= 'Y')
    #infy = Order(order_type='B', exchange='N', exchange_segment='C', scrip_code=1594, quantity=300, price=25.55,
            #    is_intraday=True, ioc_order=False, ahplaced='Y')

    response = client.place_order(infy)
    print(pd.DataFrame.from_dict([response]))
    print(client.positions())
    '''
    ## Order Book
    print(client.order_book())
    data_  = client.order_book()
    for i in range(0,1):
        columns = data_[i].keys()
        #values_ = data_[i].values()
        print(columns)
        #print(values_)
        #print(pd.DataFrame.from_dict(values_, orient='index',
                     #          columns=columns))

    ## Cancel order
    #client.cancel_order(exchange='N', exchange_segment='C',exch_order_id='1100000007313456')
    ## Order Status
    #print(pd.DataFrame.from(client.get_tradebook())
    req_list_ = [

        {
            "Exch": "N",
            "ExchType": "C",
            "ScripCode": 1594,
            "RemoteOrderID": "202201070151591"
        }]
    #print(client.fetch_order_status(req_list_))'''

