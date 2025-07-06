# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 14:47:29 2023

@author: User1
"""

import myutils

def GetScanList(Filename):
    return myutils.read_dataframe(Filename)
