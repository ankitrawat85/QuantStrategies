# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:12:11 2023

@author: User1
"""


import zerodha

api_key = '5m9ou5xedykltphu'
api_secret = 'kk0p5dcd20ag7owct6z56qgmyil8kax1'

request_token = 'aviWfXj9W2Ffo7muNlRbOGP5aV59TFrS'

access_token = zerodha.get_access_token(api_key, api_secret, request_token)

