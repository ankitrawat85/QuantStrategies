# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 07:58:14 2023

@author: ABHIJIT BISWAS (Quant Qubit Pvt. Ltd.)
"""

# This is our Zerodha API Python wrapper 


import requests
import hashlib
import pandas as pd
#import urllib.parse
import sys


def get_access_token(api_key, api_secret, request_token, printerrormessage = False):
    # Access_token (i.e. Session_token)
    # Notes:
    # The authentication token that's used with every subsequent request Unless this is invalidated using the API, 
    # or invalidated by a master-logout from the Kite Web trading terminal.
    # It'll expire at 6 AM on the next day (regulatory requirement)
    
    try:
        access_token = None
        
        h = hashlib.sha256(api_key.encode("utf-8") + request_token.encode("utf-8") + api_secret.encode("utf-8"))
        checksum = h.hexdigest()
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0'
        }
        
        data = {
            'api_key': api_key,
            'request_token': request_token,
            'checksum': checksum,
        }
        
        URL = 'https://api.kite.trade/session/token'
        
        response = requests.post(URL, headers = hdrs, data=data)
        
        result = response.json()

        if (response.status_code == 200):
            if result['status'] == 'success':
                access_token = result['data']["access_token"]
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return access_token
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_quote(api_key, access_token, exchange, segment, tradesymbol, printerrormessage = False):
    # columns
    # exchange, segment, tradesymbol, instrument_token, timestamp, last_trade_time, last_price, last_quantity, buy_quantity, 
    # sell_quantity, volume, average_price, open, high, low, close, 
    # bid_price1, bid_qty1, bid_orders1, ask_price1, ask_qty1, ask_orders1, 
    
    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol = tradesymbol.upper()
        
        inst = None
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                inst = 'NSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'NFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'CDS:' + tradesymbol
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                inst = 'BSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'BFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'BCD:' + tradesymbol
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/quote?i=' + inst
#        URL = 'https://api.kite.trade/quote?i=' + urllib.parse.quote_plus(inst)
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        quote = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                try:
                    q = data[inst]
                    
                    try:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], q['last_trade_time'], q['last_price'], q['last_quantity'], q['buy_quantity'], q['sell_quantity'], q['volume'], q['average_price']]
                    except:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], None, q['last_price'], None, None, None, None, None]
                    
                    try:
                        ohlc = q['ohlc']
                        quote.extend( [ ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'] ])
                    except:
                        quote.extend( [ None, None, None, None ])
                    
                    try:
                        depth = q['depth']
                        bid = depth['buy']
                        ask = depth['sell']
                        
                        if (len(bid) > 0):
                            quote.extend( [ bid[0]['price'], bid[0]['quantity'], bid[0]['orders'] ])
                        else:
                            quote.extend( [ None, None, None ])
                            
                        if (len(ask) > 0):
                            quote.extend( [ ask[0]['price'], ask[0]['quantity'], ask[0]['orders'] ])
                        else:
                            quote.extend( [ None, None, None ])
                    except:
                        for i in range(2):
                            quote.extend( [ None, None, None ])
                        
                except:
                    quote = []
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return quote
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_quote_5depth(api_key, access_token, exchange, segment, tradesymbol, printerrormessage = False):
    # columns
    # exchange, segment, tradesymbol, instrument_token, timestamp, last_trade_time, last_price, last_quantity, buy_quantity, 
    # sell_quantity, volume, average_price, open, high, low, close, 
    # bid_price1, bid_qty1, bid_orders1, bid_price2, bid_qty2, bid_orders2, bid_price3, bid_qty3, bid_orders3, bid_price4, bid_qty4, bid_orders4, bid_price5, bid_qty5, bid_orders5, 
    # ask_price1, ask_qty1, ask_orders1, ask_price2, ask_qty2, ask_orders2, ask_price3, ask_qty3, ask_orders3, ask_price4, ask_qty4, ask_orders4, ask_price5, ask_qty5, ask_orders5
    
    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol = tradesymbol.upper()
        
        inst = None
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                inst = 'NSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'NFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'CDS:' + tradesymbol
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                inst = 'BSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'BFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'BCD:' + tradesymbol
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/quote?i=' + inst
#        URL = 'https://api.kite.trade/quote?i=' + urllib.parse.quote_plus(inst)
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        quote = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                try:
                    q = data[inst]
                    
                    try:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], q['last_trade_time'], q['last_price'], q['last_quantity'], q['buy_quantity'], q['sell_quantity'], q['volume'], q['average_price']]
                    except:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], None, q['last_price'], None, None, None, None, None]
                    
                    try:
                        ohlc = q['ohlc']
                        quote.extend( [ ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'] ])
                    except:
                        quote.extend( [ None, None, None, None ])
                    
                    try:
                        depth = q['depth']
                        bid = depth['buy']
                        ask = depth['sell']
                        
                        for i in range(len(bid)):
                            quote.extend( [ bid[i]['price'], bid[i]['quantity'], bid[i]['orders'] ])
                        
                        if (len(bid) < 5):
                            for i in range(5 - len(bid)):
                                quote.extend( [ None, None, None ])
                            
                        for i in range(len(ask)):
                            quote.extend( [ ask[i]['price'], ask[i]['quantity'], ask[i]['orders'] ])
                        
                        if (len(ask) < 5):
                            for i in range(5 - len(ask)):
                                quote.extend( [ None, None, None ])
                    except:
                        for i in range(10):
                            quote.extend( [ None, None, None ])
                        
                except:
                    quote = []
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return quote
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_market_data(api_key, access_token, exchange, segment, tradesymbol, printerrormessage = False):
    # columns
    # exchange, segment, tradesymbol, instrument_token, timestamp, last_trade_time, last_price, last_quantity, buy_quantity, 
    # sell_quantity, volume, average_price, open, high, low, close, 
    # bid_price1, bid_qty1, bid_orders1
    # ask_price1, ask_qty1, ask_orders1
    
    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol = tradesymbol.upper()
        
        inst = None
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                inst = 'NSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'NFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'CDS:' + tradesymbol
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                inst = 'BSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'BFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'BCD:' + tradesymbol
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/quote?i=' + inst
#        URL = 'https://api.kite.trade/quote?i=' + urllib.parse.quote_plus(inst)
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        quote = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                try:
                    q = data[inst]
                    
                    try:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], q['last_trade_time'], q['last_price'], q['last_quantity'], q['buy_quantity'], q['sell_quantity'], q['volume'], q['average_price']]
                    except:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], None, q['last_price'], None, None, None, None, None]
                    
                    try:
                        ohlc = q['ohlc']
                        quote.extend( [ ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'] ])
                    except:
                        quote.extend( [ None, None, None, None ])
                    
                    try:
                        depth = q['depth']
                        bid = depth['buy']
                        ask = depth['sell']
                        
                        if (len(bid) > 0):
                            quote.extend( [ bid[0]['price'], bid[0]['quantity'], bid[0]['orders'] ])
                        else:
                            quote.extend( [ None, None, None ])
                            
                        if (len(ask) > 0):
                            quote.extend( [ ask[0]['price'], ask[0]['quantity'], ask[0]['orders'] ])
                        else:
                            quote.extend( [ None, None, None ])
                    
                    except:
                        quote.extend( [ None, None, None, None, None, None ])
                    
                except:
                    quote = []
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return quote
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_ltp(api_key, access_token, exchange, segment, tradesymbol, printerrormessage = False):
    # columns
    # exchange, segment, tradesymbol, instrument_token, last_price 
    
    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol = tradesymbol.upper()
        
        inst = None
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                inst = 'NSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'NFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'CDS:' + tradesymbol
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                inst = 'BSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'BFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'BCD:' + tradesymbol
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/quote/ltp?i=' + inst
#        URL = 'https://api.kite.trade/quote/ltp?i=' + urllib.parse.quote_plus(inst)
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        ltp = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                try:
                    q = data[inst]
                    ltp = [exchange, segment, tradesymbol, q['instrument_token'], q['last_price']]
                    
                except:
                    ltp = []
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return ltp
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_ohlc(api_key, access_token, exchange, segment, tradesymbol, printerrormessage = False):
    # columns
    # exchange, segment, tradesymbol, instrument_token, last_price, open, high, low, close, 
    
    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol = tradesymbol.upper()
        
        inst = None
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                inst = 'NSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'NFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'CDS:' + tradesymbol
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                inst = 'BSE:' + tradesymbol
            elif (segment == 'FNO'):
                inst = 'BFO:' + tradesymbol
            elif (segment == 'CDS'):
                inst = 'BCD:' + tradesymbol
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/quote/ohlc?i=' + inst
#        URL = 'https://api.kite.trade/quote/ohlc?i=' + urllib.parse.quote_plus(inst)
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        quote = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                try:
                    q = data[inst]
                    quote = [exchange, segment, tradesymbol, q['instrument_token'], q['last_price']]
                    
                    ohlc = q['ohlc']
                    quote.extend( [ ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'] ])
                        
                except:
                    quote = []
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return quote
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_quote_list(api_key, access_token, exchange, segment, tradesymbol_list, printerrormessage = False):
    # todo
    # columns
    # exchange, segment, tradesymbol, instrument_token, timestamp, last_trade_time, last_price, last_quantity, buy_quantity, 
    # sell_quantity, volume, average_price, open, high, low, close, 
    # bid_price1, bid_qty1, bid_orders1, bid_price2, bid_qty2, bid_orders2, bid_price3, bid_qty3, bid_orders3, bid_price4, bid_qty4, bid_orders4, bid_price5, bid_qty5, bid_orders5, 
    # ask_price1, ask_qty1, ask_orders1, ask_price2, ask_qty2, ask_orders2, ask_price3, ask_qty3, ask_orders3, ask_price4, ask_qty4, ask_orders4, ask_price5, ask_qty5, ask_orders5
    
    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol_list = tradesymbol_list.upper()
        
        inst = None
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                inst = 'NSE:' + tradesymbol_list
            elif (segment == 'FNO'):
                inst = 'NFO:' + tradesymbol_list
            elif (segment == 'CDS'):
                inst = 'CDS:' + tradesymbol_list
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                inst = 'BSE:' + tradesymbol_list
            elif (segment == 'FNO'):
                inst = 'BFO:' + tradesymbol_list
            elif (segment == 'CDS'):
                inst = 'BCD:' + tradesymbol_list
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/quote?i=' + inst
#        URL = 'https://api.kite.trade/quote?i=' + urllib.parse.quote_plus(inst)
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        quote = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                try:
                    q = data[inst]
                    
                    try:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], q['last_trade_time'], q['last_price'], q['last_quantity'], q['buy_quantity'], q['sell_quantity'], q['volume'], q['average_price']]
                    except:
                        quote = [exchange, segment, tradesymbol, q['instrument_token'], q['timestamp'], q['last_price']]
                    
                    try:
                        ohlc = q['ohlc']
                        quote.extend( [ ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'] ])
                    except:
                        pass
                    
                    depth = q['depth']
                    bid = depth['buy']
                    ask = depth['sell']
                    
                    for i in range(len(bid)):
                        quote.extend( [ bid[i]['price'], bid[i]['quantity'], bid[i]['orders'] ])
                    
                    if (len(bid) < 5):
                        for i in range(5 - len(bid)):
                            quote.extend( [ None, None, None ])
                        
                    for i in range(len(ask)):
                        quote.extend( [ ask[i]['price'], ask[i]['quantity'], ask[i]['orders'] ])
                    
                    if (len(ask) < 5):
                        for i in range(5 - len(ask)):
                            quote.extend( [ None, None, None ])
                except:
                    quote = []
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return quote
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def place_order(api_key, access_token, exchange, segment, tradesymbol, trans_type, order_type, qty, price, product, validity, order_variety = 'REGULAR', trigger_price = 0, disclosed_quantity = 0, validity_ttl_minutes = '1', printerrormessage = False):
    # AssetClass = CASH / FNO
    # TransType = BUY / SELL
    # OrderType = LIMIT / MARKET / SL-M / SL
    # ProductType = NRML / MIS / CNC / CO
    # OrderValidity = DAY / IOC / TTL
    # Variety = regular/amo/co/iceberg/auction

    try:
        exchange = exchange.upper()
        segment = segment.upper()
        tradesymbol = tradesymbol.upper()
        trans_type = trans_type.upper()
        order_type = order_type.upper()
        if (type(qty) != str):
            qty = str(qty)
        if (type(price) != str):
            price = str(price)
        
        order_variety = order_variety.lower()
        product = product.upper()
        validity = validity.upper()
        if (type(validity_ttl_minutes) != str):
            validity_ttl_minutes = str(validity_ttl_minutes)
        
        
        if (exchange == 'NSE'):
            if (segment == 'CASH'):
                exchange = 'NSE'
            elif (segment == 'FNO'):
                exchange = 'NFO' 
            elif (segment == 'CDS'):
                exchange = 'CDS' 
        elif (exchange == 'BSE'):
            if (segment == 'CASH'):
                exchange = 'BSE' 
            elif (segment == 'FNO'):
                exchange = 'BFO' 
            elif (segment == 'CDS'):
                exchange = 'BCD' 
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        data = {
            'tradingsymbol': tradesymbol,
            'exchange': exchange,
            'transaction_type': trans_type,
            'order_type': order_type,
            'quantity': qty,
            'price' : price,
            'product': product,
            'validity': validity
#            'validity_ttl_minutes': validity_ttl_minutes
        }        
        
        URL = 'https://api.kite.trade/orders/' + order_variety
        
        response = requests.post(URL, headers = hdrs, data = data)
        
        result = response.json()

        order_id = None
        if (response.status_code == 200):
            if result['status'] == 'success':
                order_id = result['data']["order_id"]
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return order_id
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def modify_order(api_key, access_token, order_id, order_type, qty, price, validity, order_variety, trigger_price = 0, disclosed_quantity = 0, printerrormessage = False):
    try:
        order_type = order_type.upper()
        if (type(qty) != str):
            qty = str(qty)
        if (type(price) != str):
            price = str(price)
        
        order_variety = order_variety.lower()
        validity = validity.upper()
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        data = {
            'order_type': order_type,
            'quantity': qty,
            'price' : price,
            'validity': validity
#            'validity_ttl_minutes': validity_ttl_minutes
        }        
        
        URL = 'https://api.kite.trade/orders/' + order_variety + '/' + order_id
        
        response = requests.put(URL, headers = hdrs, data = data)
        
        result = response.json()
        
        order_id = None
        if (response.status_code == 200):
            if result['status'] == 'success':
                order_id = result['data']["order_id"]
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
        
        if (order_id == None):
            return False
        else:
            return True
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return False


def cancel_order(api_key, access_token, order_id, order_variety = 'REGULAR', printerrormessage = False):
    try:
        order_variety = order_variety.lower()
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/orders/' + order_variety + '/' + order_id
        
        response = requests.delete(URL, headers = hdrs)
        
        result = response.json()
        
        order_id = None
        if (response.status_code == 200):
            if result['status'] == 'success':
                order_id = result['data']["order_id"]
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        if (order_id == None):
            return False
        else:
            return True
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return False


def get_order_status_history(api_key, access_token, order_id, printerrormessage = False):
    # columns
    # exchange, tradingsymbol, instrument_token, order_type, validity, product, variety, transaction_type, quantity, disclosed_quantity, 
    # price, trigger_price, average_price, filled_quantity, pending_quantity, cancelled_quantity, order_id, exchange_order_id, 
    # placed_by, status, status_message, status_message_raw, order_timestamp, exchange_timestamp, exchange_update_timestamp, tag

    try:
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/orders/' + order_id
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        status = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                for i in range(len(data)):
                    s = data[i]
                    status.extend([[ s['exchange'], s['tradingsymbol'], s['instrument_token'], s['order_type'], s['validity'], s['product'], s['variety'], s['transaction_type'], s['quantity'], s['disclosed_quantity'], s['price'], s['trigger_price'], s['average_price'], s['filled_quantity'], s['pending_quantity'], s['cancelled_quantity'], s['order_id'], s['exchange_order_id'], s['placed_by'], s['status'], s['status_message'], s['status_message_raw'], str(s['order_timestamp']), str(s['exchange_timestamp']), str(s['exchange_update_timestamp']), s['tag'] ]])
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return status
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_order_status(api_key, access_token, order_id, printerrormessage = False):
    # columns
    # exchange, tradingsymbol, instrument_token, order_type, validity, product, variety, transaction_type, quantity, disclosed_quantity, 
    # price, trigger_price, average_price, filled_quantity, pending_quantity, cancelled_quantity, order_id, exchange_order_id, 
    # placed_by, status, status_message, status_message_raw, order_timestamp, exchange_timestamp, exchange_update_timestamp, tag

    try:
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/orders/' + order_id
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        status = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']

                s = data[len(data)-1]
                
                status.extend([ s['exchange'], s['tradingsymbol'], s['instrument_token'], s['order_type'], s['validity'], s['product'], s['variety'], s['transaction_type'], s['quantity'], s['disclosed_quantity'], s['price'], s['trigger_price'], s['average_price'], s['filled_quantity'], s['pending_quantity'], s['cancelled_quantity'], s['order_id'], s['exchange_order_id'], s['placed_by'], s['status'], s['status_message'], s['status_message_raw'], str(s['order_timestamp']), str(s['exchange_timestamp']), str(s['exchange_update_timestamp']), s['tag'] ])
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return status
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_order_status_all(api_key, access_token, printerrormessage = False):
    # columns
    # exchange, tradingsymbol, instrument_token, order_type, validity, product, variety, transaction_type, quantity, disclosed_quantity, 
    # price, trigger_price, average_price, filled_quantity, pending_quantity, cancelled_quantity, order_id, exchange_order_id, 
    # placed_by, status, status_message, status_message_raw, order_timestamp, exchange_timestamp, exchange_update_timestamp, tag

    try:
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/orders'
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        status = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                for i in range(len(data)):
                    s = data[i]
                    status.extend([[ s['exchange'], s['tradingsymbol'], s['instrument_token'], s['order_type'], s['validity'], s['product'], s['variety'], s['transaction_type'], s['quantity'], s['disclosed_quantity'], s['price'], s['trigger_price'], s['average_price'], s['filled_quantity'], s['pending_quantity'], s['cancelled_quantity'], s['order_id'], s['exchange_order_id'], s['placed_by'], s['status'], s['status_message'], s['status_message_raw'], str(s['order_timestamp']), str(s['exchange_timestamp']), str(s['exchange_update_timestamp']), s['tag'] ]])
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return status
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None



def get_trade(api_key, access_token, order_id, printerrormessage = False):
    # columns
    # exchange, tradingsymbol, instrument_token,  product, transaction_type, quantity, average_price, order_id, exchange_order_id, 
    # trade_id, order_timestamp, exchange_timestamp, fill_timestamp
    
    try:
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/orders/' + order_id + '/trades'
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        trade = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                s = result['data']
                
                trade.extend([ s['exchange'], s['tradingsymbol'], s['instrument_token'], s['product'], s['transaction_type'], s['quantity'], s['average_price'], s['order_id'], s['exchange_order_id'], s['trade_id'], s['order_timestamp'], s['exchange_timestamp'], s['fill_timestamp'] ])
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return trade
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def get_trade_all(api_key, access_token, printerrormessage = False):
    # columns
    # exchange, tradingsymbol, instrument_token,  product, transaction_type, quantity, average_price, order_id, exchange_order_id, 
    # trade_id, order_timestamp, exchange_timestamp, fill_timestamp
    
    try:
        
        hdrs = {
            'X-Kite-Version': '3',
            "User-Agent": 'Kiteconnect-python/4.2.0',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/trades'
        
        response = requests.get(URL, headers = hdrs)
        
        result = response.json()
        
        trade = []
        if (response.status_code == 200):
            if result['status'] == 'success':
                data = result['data']
                
                for i in range(len(data)):
                    s = data[i]
                    trade.extend([[ s['exchange'], s['tradingsymbol'], s['instrument_token'], s['product'], s['transaction_type'], s['quantity'], s['average_price'], s['order_id'], s['exchange_order_id'], s['trade_id'], s['order_timestamp'], s['exchange_timestamp'], s['fill_timestamp'] ]])
                
            elif result['status'] == 'error':
                if printerrormessage:
                    print(result['message'])
            else:
                if printerrormessage:
                    print(result['data'])
        else:
            if printerrormessage:
                if result['status'] == 'error':
                    print(result['message'])
                else:
                    print(result)
            
        return trade
    except Exception as ex:
        if printerrormessage:
            print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def download_masters(api_key, access_token, path=''):
    try:
        result = ''
        
        hdrs = {
            'X-Kite-Version': '3',
            'Authorization': 'token ' + api_key + ':' + access_token
        }
        
        URL = 'https://api.kite.trade/instruments'
        
        response = requests.get(URL, headers = hdrs)
        
        if (response.status_code == 200):
            try:
                data = response.text
                myfile = open(path + 'masters/allmasters.csv', 'w')
                myfile.write(data)
                myfile.close()
            except:
                result = 'NSE masters data write failed'
                return
            
            
            try:
                data = pd.read_csv(path + 'masters/allmasters.csv')
                data = data.set_index('exchange')
                
                # NSE cash master
                cm = data.loc['NSE']
                cm = cm.loc[cm['instrument_type'] == 'EQ']
                
                if (__sortdata__(cm, 'C')):
                    cm.to_csv(path + 'masters/NSE_CM.csv', index = False)
                    result = 'NSE Cash segment downloaded successfully'
                else:
                    result = 'NSE Cash segment SORTING FAILED'
            except:
                result = 'NSE Cash segment download failed'
            
                
            try:
                # NSE FNO master
                fo = data.loc['NFO']
                
                # NSE FUTURES master
                fut = fo.loc[(fo['segment'] == 'NFO-FUT')]
                
                if (__sortdata__(fut, 'F')):
                    fut.to_csv(path + 'masters/NSE_FUT.csv', index = False)
                    result = result + '\n' + 'NSE FUTURES segment downloaded successfully'
                else:
                    result = result + '\n' + 'NSE FUTURES segment SORTING FAILED'
                
                # NSE OPTIONS master
                opt = fo.loc[(fo['segment'] == 'NFO-OPT')]
                
                if (__sortdata__(opt, 'O')):
                    opt.to_csv(path + 'masters/NSE_OPT.csv', index = False)
                    result = result + '\n' + 'NSE OPTIONS segment downloaded successfully'
                else:
                    result = result + '\n' + 'NSE OPTIONS segment SORTING FAILED'
                
            except:
                result = result + '\n' + 'NSE FNO segment download failed'
                            
        else:
            result = 'Masters data download failed'
        
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
    


def __sortdata__(data, InstType):
    
    try:
        if (InstType == 'C'):
            data.sort_values(['segment','instrument_token'], axis=0, ascending=[True,True], inplace=True)
        elif (InstType == 'F'):
#            data['expiry'] = pd.to_datetime(data['expiry'], format = '%d-%m-%Y %H:%M:%S')
            data['expiry'] = pd.to_datetime(data['expiry'])
            data.sort_values(['name','expiry'], axis=0, ascending=[True,True], inplace=True)
            data['expiry'] = data['expiry'].dt.strftime('%d-%m-%Y %H:%M:%S')
        else:
#            data['expiry'] = pd.to_datetime(data['expiry'], format = '%d-%m-%Y %H:%M:%S')
            data['expiry'] = pd.to_datetime(data['expiry'])
            data.sort_values(['name','expiry', 'strike', 'instrument_type'], axis=0, ascending=[True,True,True,True], inplace=True)
            data['expiry'] = data['expiry'].dt.strftime('%d-%m-%Y %H:%M:%S')
        
        return True
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return False



