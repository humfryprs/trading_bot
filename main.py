from keys import api, secret
from binance.um_futures import UMFutures
import ta
import pandas as pd
from time import sleep
from binance.error import ClientError

client = UMFutures(key= api,secret=secret)

tp = 0.01
sl = 0.01
volume = 50
leverage = 10
type = 'ISOLATED'

# type isolated or cross

def get_balance_usdt():
    try:
        response = client.balance(recvWindow=100000000)
        for elem in response:
            if elem['asset']=='USDT':
                return float(elem['balance'])
    except ClientError as error:
        print(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
        
print("My balance is: ", get_balance_usdt()," USDT")

def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

# print(get_tickers_usdt())

def klines(symbol) :
    try:
        resp = pd.DataFrame(client.klines(symbol, '1h'))
        resp = resp.iloc[:,:6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit= 'ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
        
print(klines('XRPUSDT'))

def set_leverage(symbol, level):
    try:
        response = client.change_leverage(
            symbol=symbol, leverage=level, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
    
def set_mode(symbol, type):
    try:
        response = client.change_margin_type(
            symbol=symbol, marginType=type, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

def get_price_percision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['pricePrecision']
        
def get_qty_percision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['quantityPrecision']