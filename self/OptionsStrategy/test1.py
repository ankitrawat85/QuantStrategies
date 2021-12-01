import requests
import json
import pandas as pd

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


def fetch_oi(expiry_dt):
    ce_values = [data['CE'] for data in dajs['records']['data'] if "CE" in data and data['expiryDate'] == expiry_dt]
    print(ce_values)
    pe_values = [data['PE'] for data in dajs['records']['data'] if "PE" in data and data['expiryDate'] == expiry_dt]


    #print(ce_dt[['strikePrice', 'lastPrice']])


def main():
    expiry_dt = '27-Aug-2020'
    fetch_oi(expiry_dt)


if __name__ == '__main__':
    main()