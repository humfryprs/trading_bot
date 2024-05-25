from keys import API, SECRET
from binance.um_futures import UMFutures
import ta
import time
import pandas as pd
from time import sleep
from binance.error import ClientError

client = UMFutures(key= API,secret=SECRET)

TP = 0.01 #close 1%
SL = 0.005 #close 0.5%
VOLUME = 50 
LEVERAGE = 10
type = 'ISOLATED'

# type isolated or cross

def get_balance_usdt():
    try:
        response = client.balance(recvWindow=6000)
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

# ngeluarin semua symbol yg available di market

def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

# print(get_tickers_usdt())

# set OHLC dari masing" symbol

def klines(symbol) : 
    try:
        resp = pd.DataFrame(client.klines(symbol, '1m'))
        resp = resp.iloc[:,:6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit= 'ms')
        resp = resp.astype(float)
        # print('Hasil Response klines ', resp)
        return resp
    except ClientError as error:
        print(
        "Found error in klines. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
        
# print(klines("XRPUSDT"))
        
# set leverage utk symbol tertentu pas mau trade
        
def set_leverage(symbol, level):
    try:
        response = client.change_leverage(
            symbol=symbol, leverage=level, recvWindow=6000
        )
        print('Hasil Response set_leverage ',response)
    except ClientError as error:
        print(
            "Found error in set_leverage. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        
# print(set_leverage("XRPUSDT",10))

# Set mode ISOLATED, CROSSED
    
def set_mode(symbol, type):
    try:
        response = client.change_margin_type(
            symbol=symbol, marginType=type, recvWindow=6000
        )
        print('Hasil Response set_mode ',response)
    except ClientError as error:
        print(
            "Found error in Set_Mode. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

#pengecekan jumlah angka dibelakang koma
def get_price_percision(symbol):
    resp = client.exchange_info()['symbols']
    # print(resp)
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['pricePrecision']
        
# print('price ', get_price_percision('BTCUSDT'))

# Min quantyty di blkng koma utk kita buy
        
def get_qty_percision(symbol):
    resp = client.exchange_info()['symbols']
    # print(resp)
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['quantityPrecision']
        
# print('qty ', get_qty_percision('BTCUSDT'))


#

def open_order(symbol, side):
    price = float(client.ticker_price(symbol)['price'])
    qty_percision = get_qty_percision(symbol)
    price_percision = get_price_percision(symbol)
    qty = round(VOLUME/price, qty_percision) #utk ngitung jumlah yg kita mau, disesuain sama minimum desimal buy yg bisa dibeli
    if side == 'buy':
        try:
            resp1 = client.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "placing order")
            print('Entry Price ',resp1)
            sleep(2)
            sl_price = round(price-price*SL, price_percision)
            resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print('SL Price ', resp2)
            
        except ClientError as error:
            print(
                "Found error in Open_Order_buy. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    if side == 'sell':
        try:
            resp1 = client.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "placing order")
            print('Entry Price ',resp1)
            sleep(2)
            sl_price = round(price+price*SL, price_percision)
            resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print('SL Price ',resp2)

        except ClientError as error:
            print(
                "Found error in Open_Order_sell. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
            
def tp_order(symbol, side):
    price = float(client.ticker_price(symbol)['price'])
    qty_percision = get_qty_percision(symbol)
    price_percision = get_price_percision(symbol)
    qty = round(VOLUME/price, qty_percision) #utk ngitung jumlah yg kita mau, disesuain sama minimum desimal buy yg bisa dibeli
    if side == 'buy':
        try:
            tp_price = round(price+price*TP, price_percision)
            resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print('TP Price ',resp3)
        except ClientError as error:
            print(
                "Found error in Open_Order_buy. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    if side == 'sell':
        try:
            tp_price = round(price-price*TP, price_percision)
            resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print('TP Price ',resp3)

        except ClientError as error:
            print(
                "Found error in Open_Order_sell. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

def check_positions():
    try:
        resp = client.get_position_risk()
        positions = 0
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                positions += 1
        return positions
    except ClientError as error:
        print(
            "Found error in Check_position. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        
def close_open_orders(symbol):
    try:
        response = client.cancel_open_orders(symbol="symbol", recvWindow=2000)
        print(response)
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

#simple indicator
        
def check_sma200_50(symbol):
    kl = klines(symbol)
    sma50 = ta.trend.sma_indicator(kl.Close, window=50)
    sma200 = ta.trend.sma_indicator(kl.Close, window=200)
    if sma50.iloc[-3] < sma200.iloc[-3] and sma50.iloc[-2] < sma200.iloc[-2] and sma50.iloc[-1] > sma200.iloc[-1]: #SMA 50 breakup SMA 200
        return 'up'
    if sma50.iloc[-3] > sma200.iloc[-3] and sma50.iloc[-2] > sma200.iloc[-2] and sma50.iloc[-1] < sma200.iloc[-1]: #SMA 50 breakdown SMA 200
        return 'down'
    else:
        return 'none'
    

order = False
symbol = ''
symbols = get_tickers_usdt()
price = client.klines("DOGEUSDT", "1d", limit=1)
first_kline = price[0]
first_index = first_kline[0]  # open time
third_element = first_kline[4]
# def get_latest_price_klines():
#     tickers = []
#     resp = client.klines("DOGEUSDT", "1d", limit=1)
#     for elem in resp:
#         if 'USDT' in elem['symbol']:
#             price2.append(elem['symbol'])
#     return price2



#looping scriptnya disini

while True:
    positions = check_positions()
    print(f'You have {positions} opened positions')
    time.sleep(2)
    print(third_element)
    
    # if positions == 0:
    #     order = False
    #     if symbol != '': #jika symbolnya tidak kosong
    #         close_open_orders(symbol)         
    #     if order == False:
    #         for elem in symbols:
    #             signal = check_sma200_50(elem)
    #             if signal == 'up':
    #                 print('Found BUY signal for', elem)
    #                 set_mode(elem, type)
    #                 sleep(1)
    #                 set_leverage(elem, LEVERAGE)
    #                 sleep(1)
    #                 open_order(elem, 'buy')
    #                 symbol = elem
    #                 order = True
    #                 break
    #             if signal == 'down':
    #                 print('Found SELL signal for', elem)
    #                 set_mode(elem, type)
    #                 sleep(1)
    #                 set_leverage(elem, LEVERAGE)
    #                 sleep(1)
    #                 open_order(elem, 'sell')
    #                 symbol = elem
    #                 order = True
    #                 break
    # exit()
    
    #looping ngecek terus ada pair yg match indicator kg
    print('Waiting 1 min')
    time.sleep(10)