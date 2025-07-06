# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 09:36:31 2023

@author: User1
"""

import myutils

def GetAPIPara():
    try:
        # todo some more API para to add
        data = myutils.read_dataframe('APISettings.csv')
        
        if (len(data) == 0):
            return None, None, None, None, None, None
        
        userid = data['UserID'][0]
        password = data['Password'][0]
        api_key = data['APIKey'][0]
        api_secret = data['APISecret'][0]
        access_token = data['AccessToken'][0]
        access_token_date = data['AccessTokenTimeStamp'][0]
        
        return userid, password, api_key, api_secret, access_token, access_token_date
    
    except Exception as errmsg:
        print(errmsg)
        return None, None, None, None, None, None, None


def SaveAPIPara(userid, password, api_key, api_secret, access_token, access_token_date):
    try:
        # todo some more API para to add
        data = [['UserID','Password','APIKey','APISecret','AccessToken','AccessTokenTimeStamp'],[userid, password, api_key, api_secret, access_token, access_token_date]]
        
        myutils.write_list_to_csv('APISettings.csv', data)
        
        return True
    
    except Exception as errmsg:
        print(errmsg)
        return False
