import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
'''
baseurl = "https://www.nseindia.com/"
url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) '
                         'Chrome/80.0.3987.149 Safari/537.36',
           'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
session = requests.Session()
request = session.get(baseurl, headers=headers, timeout=5)
cookies = dict(request.cookies)
response = session.get(url, headers=headers, timeout=5, cookies=cookies)
dajs = json.loads(response.text)
ce_values = [data['CE'] for data in dajs['records']['data'] if "CE" in data and data['expiryDate'] == "16-Dec-2021"]
print(pd.DataFrame(ce_values))
'''

"""def  optionchainstock(optionType ="PE",symbol= "SBIN",expiryDate="30-12-2021"):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    baseurl = "https://www1.nseindia.com/products/content/derivatives/equities/historical_fo.htm"
    url = f"https://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp?instrumentType=OPTSTK&symbol="+symbol+"&expiryDate="+expiryDate+"&optionType="+optionType+"&strikePrice=&dateRange=24month&fromDate=&toDate=&segmentLink=9&symbolCount="
    print(url)
    session = requests.Session()
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=5, cookies=cookies)
    soup = BeautifulSoup(response.text)
    df_list = pd.read_html(response.text)  # this parses all the tables in webpages to a list
    df = df_list[0]
    df.to_csv("stockoptions.csv")
    x = pd.read_csv("stockoptions.csv",skiprows=1,header =0,index_col="Date")
    x.drop(columns={"Unnamed: 0"}, inplace= True)
    print(x)
optionchainstock()
"""
