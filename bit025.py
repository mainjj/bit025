import time
import pyupbit
import datetime

access = "3ne7DHtdIJmaEcP2lynfp7QXUF5gkM3NlQ3O6oj0"
secret = "3EpuiiMfJXDCE3LInUOgN3Txh3ANj0uYJEpWoBon"

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

def search_buy(cost, coin_list):
    for name in coin_list:
        temp_val = upbit.get_balance("{}".format(name),verbose=True)
        if temp_val == 0:
            continue
        
        df = pyupbit.get_ohlcv("{}".format(name), interval="minute10",count=5)[:-1]
        dev = list(df['close'] - df['open']) #+,- 판별리스트 (10분봉 종가-시가)
        #판별리스트 --++ 이면 구매
        if dev[0]<0 and dev[1]<0:
            if dev[2]>0 and dev[3]>0:
                print(upbit.buy_market_order("{}".format(name), cost))
                
def sell(asset):
    for i in asset[1:-1]:
        if float(i['locked']) > 0: #미체결건이 있으면 pass 
            continue

        name = "KRW-"+i['currency']
        buy_price = float(i['avg_buy_price'])
        current_price = pyupbit.get_current_price("{}".format(name))
        volume = upbit.get_amount(name)   
        #손절
        if current_price <= buy_price*0.95:
            upbit.sell_market_order("{}".format(name),volume=volume)
            continue

        #익절
        if current_price >= buy_price*1.025:
            upbit.sell_market_order("{}".format(name), volume=volume)

bad_coin = set(['KRW-BTC','KRW-ETH','KRW-XRP','KRW-ADA','KRW-DOGE','KRW-TON','KRW-AHT','KRW-GAS','KRW-','KRW-AQT','KRW-UPP','KRW-RFR','KRW-MOC','KRW-SBD','KRW-BTT','KRW-SHIB','KRW-XEC','KRW-WAVES','KRW-KAVA','KRW-NU'])
    
while True:
    coin_list = set(pyupbit.get_tickers(fiat="KRW")) #코인 종류 리스트
    coin_list = list(coin_list - bad_coin)
    
    asset = upbit.get_balances()
    wallet = int(upbit.get_balance_t()) #현재 보유 원화
    total_num = 10 #구매 한도 10개
    coin_num = len(asset)-2 #현재 보유 코인 갯수

    cost = int(wallet / (total_num - coin_num))

    sell(asset=asset)
    
    if coin_num == 10:
        continue

    search_buy(cost, coin_list)
