# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 12:02:01 2023

@author: User1
"""

def get_ltp(exchange, trdsymbol, symbol, broker, api_object):
    try:
        if (broker.upper() == 'ZERODHA'):
            result = api_object.ltp(exchange + ':' + trdsymbol)
            
            ltp = float(result[exchange + ':' + trdsymbol]['last_price'])
            
        elif (broker.upper() == 'KSEC'):
            pass
        else:
            pass
        
        return ltp
        
    except Exception as errmsg:
        print(errmsg)
        return None
    

def place_order(exchange, trdsymbol, symbol, transtype, validity, ordertype, IsCashMarket, IsIntraday, qty, price, variety, broker, api_object):
    try:
        orderid = ''
        
        if (broker.upper() == 'ZERODHA'):
            if (IsCashMarket):
                if (IsIntraday):
                    product = 'MIS'
                else:
                    product = 'CNC'
            else:
                if (IsIntraday):
                    product = 'MIS'
                else:
                    product = 'NRML'
            
            variety = variety.lower()
            
            qty = int(qty)
            
            orderid = api_object.place_order(variety, exchange, trdsymbol, transtype, str(qty), product, ordertype, str(price), validity)
            
        elif (broker.upper() == 'KSEC'):
            pass
        else:
            pass
        
        return orderid
        
    except Exception as errmsg:
        print(errmsg)
        return ''
    
def get_order_status(orderid, broker, api_object):
    try:
        status = []
        if (broker.upper() == 'ZERODHA'):
            oh = api_object.order_history(orderid)
            
            s = oh[len(oh)-1]
            
            status = [s['exchange'], s['tradingsymbol'], s['instrument_token'], s['order_type'], s['validity'], s['product'], s['variety'], s['transaction_type'],s['quantity'],s['disclosed_quantity'],s['price'],s['trigger_price'],s['average_price'],s['filled_quantity'],s['pending_quantity'],s['cancelled_quantity'],s['order_id'],s['exchange_order_id'],s['placed_by'],s['status'],s['status_message'],s['status_message_raw'],str(s['order_timestamp']),str(s['exchange_timestamp']),str(s['exchange_update_timestamp']), s['tag'] ]
            
        elif (broker.upper() == 'KSEC'):
            pass
        else:
            pass
        
        return status
        
    except Exception as errmsg:
        print(errmsg)
        return []
    
    
    