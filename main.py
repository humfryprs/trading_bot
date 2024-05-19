from keys import API, SECRET
from binance.um_futures import UMFutures
import ta
import pandas as pd
from time import sleep
from binance.error import ClientError

client = UMFutures(key= API,secret=SECRET)

TP = 0.01 #close 1%
SL = 0.01 #close 1%
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

# set OHLC dari masing" symbol

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
        
# set OHLC dari masing" symbol
        
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
        
def open_order(symbol, side):
    price = float(client.ticker_price(symbol)['Price'])
    qty_percision = get_qty_percision(symbol)
    price_percision = get_price_percision(symbol)
    qty = round(VOLUME/price, qty_percision)
    if side == 'buy':
        try:
            resp1 = client.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "placing order")
            print(resp1)
            sleep(2)
            sl_price = round(price-price*SL, price_percision)
            resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(resp2)
            sleep(2)
            tp_price = round(price+price*TP, price_percision)
            resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(resp3)

        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    if side == 'sell':
        try:
            resp1 = client.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
            print(symbol, side, "placing order")
            print(resp1)
            sleep(2)
            sl_price = round(price+price*SL, price_percision)
            resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(resp2)
            sleep(2)
            tp_price = round(price-price*TP, price_percision)
            resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(resp3)

        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

def check_positions():
    try:
        resp = client.get_position_risk()
        POSITIONS = 0
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                POSITIONS += 1
        return POSITIONS
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
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
        
def check_ema200_50(symbol):
    kl = klines(symbol)
    ema200 = ta.trend.ema_indicator(kl.Close, window=100)
    ema50 = ta.trend.ema_indicator(kl.Close, window=50)
    if ema50.iloc[-3] < ema200.iloc[-3] and ema50.iloc[-2] < ema200.iloc[-2] and ema50.iloc[-1] > ema200.iloc[-1]:
        return 'up'
    if ema50.iloc[-3] > ema200.iloc[-3] and ema50.iloc[-2] > ema200.iloc[-2] and ema50.iloc[-1] < ema200.iloc[-1]:
        return 'down'
    else:
        return 'none'
    

order = False
symbol = ''
symbols = get_tickers_usdt()

while True:
    POSITIONS = check_positions()
    print(f'You have {POSITIONS} opened positions')
    if POSITIONS == 0:
        order = False
        if symbol != '':
            close_open_orders(symbol)
            
    if order == False:
        for elem in symbols:
            signal = check_ema200_50(elem)
            if signal == 'up':
                print('Found BUY signal for', elem)
                set_mode(elem, type)
                sleep(1)
                set_leverage(elem, LEVERAGE)
                sleep(1)
                open_order(elem, 'buy')
                symbol = elem
                order = True
                break
            if signal == 'down':
                print('Found SELL signal for', elem)
                set_mode(elem, type)
                sleep(1)
                set_leverage(elem, LEVERAGE)
                sleep(1)
                open_order(elem, 'sell')
                symbol = elem
                order = True
                break
    print('Waiting 60 sec')
    sleep(60)