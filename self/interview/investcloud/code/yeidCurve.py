'''
Simple yield curve model implementation
'''

## import libraries
import os
import logging
import time
import pandas as pd
import numpy as np

class dataParsing:
 def __init__(self,*args,**kwargs,):
     pass

 def readCsv(self):
     return pd.read_csv(kwargs['path'])





class ratesCalculation:
    def __init__(self, *args, **kwargs, ):
        pass

class yieldCurve:
    def __init__(self, *args, **kwargs, ):
        pass

class priceSimulation:
    def __init__(self, *args, **kwargs, ):
        pass

class simulation:
    def __init__(self, *args, **kwargs, ):
        pass


if __name__ == "__main__":
    root_DIR = os.path.dirname(os.path.abspath(__file__))
    logging.debug( msg= f'root directory : {root_DIR}',stacklevel=4)
    print(root_DIR)