import requests
from io import StringIO
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import pandas as pd
import json


# 參考 twstock 取得需要的 URL
SESSION_URL = 'http://mis.twse.com.tw/stock/index.jsp'
STOCKINFO_URL = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={stock_id}&_={time}'


def get_realtime_quote(stockNo, ex='tse'):
    req = requests.Session()
    req.get(SESSION_URL)
    
    stock_id = '{}_{}.tw'.format(ex, stockNo)

    r = req.get(STOCKINFO_URL.format(stock_id=stock_id, time=int(time.time()) * 1000))

    try:
        return r.json()
    except json.decoder.JSONDecodeError:
        return {'rtmessage': 'json decode error', 'rtcode': '5000'}


def convert_date(x):
    year, month, day = x.split('/')
    return datetime(int(year)+1911, int(month), int(day))


def get_tw_stock_df(stockNo, date):
    url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv&date={}&stockNo={}"
    df = pd.read_csv(url.format(date.strftime("%Y%m%d"), stockNo), skipfooter=4, skiprows=1)
    # 因為 .csv 擋後面有多一個 comma，所以會產生一個叫做 Unnamed 的 column
    return df.loc[:, ~df.columns.str.contains("Unnamed")]


# def get_tw_stock(stockNo, date):
#     url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY"
#     params = {}
#     params['stockNo'] = stockNo
#     params['date'] = date.strftime("%Y%m%d")
#     params['response'] = "csv"
#     r = requests.get(url, params=params)
#     df = pd.read_csv(StringIO(r.text), skiprows=1, skip_footer=4, thousands=',')
#     df['日期'] = df['日期'].apply(convert_date)
#     return df.loc[:, ~df.columns.str.contains("Unnamed")].set_index('日期')

def get_tw_stock(stockNo, date):
    url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY"
    params = {}
    params['stockNo'] = stockNo
    params['date'] = date.strftime("%Y%m%d")
    data = requests.get(url, params=params).json()
    df = pd.DataFrame(data['data'], columns=data['fields'])
    df['日期'] = df['日期'].apply(convert_date)
    df['成交股數'] = pd.to_numeric(df['成交股數'].str.replace(",",""))
    df['成交金額'] = pd.to_numeric(df['成交金額'].str.replace(",",""))
    df['成交筆數'] = pd.to_numeric(df['成交筆數'].str.replace(",",""))
    df['開盤價'] = pd.to_numeric(df['開盤價'])
    df['最高價'] = pd.to_numeric(df['最高價'])
    df['最低價'] = pd.to_numeric(df['最低價'])
    df['收盤價'] = pd.to_numeric(df['收盤價'])
    return df.set_index('日期')


def get_historical_data(stockNo, start, end=None, delay=3):
    if not end:
        end = datetime.now()
    data = []
    while start <= end:
        data.append(get_tw_stock(stockNo, start))
        time.sleep(delay)
        start += relativedelta(months=1)
    return pd.concat(data)


def get_data_months(stockNo, months=3, delay=3):
    now = datetime.now()
    data = []
    while months > 0:
        data.append(get_tw_stock(stockNo, now))
        time.sleep(delay)
        now -= relativedelta(months=1)
        months -= 1
    return pd.concat(data).sort_index()


if __name__=="__main__":
    # df = get_tw_stock("2330", datetime(2016, 1, 1))
    # print(df.head())
    #df = get_historical_data("2330", datetime(2017, 8, 1))
    df = get_data_months("2330", months=2, delay=3)
    print(df)