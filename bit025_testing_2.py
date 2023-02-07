import pyupbit
import time

access = "3ne7DHtdIJmaEcP2lynfp7QXUF5gkM3NlQ3O6oj0"
secret = "3EpuiiMfJXDCE3LInUOgN3Txh3ANj0uYJEpWoBon"

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


def search_buy(cost, name):
    df = pyupbit.get_ohlcv("{}".format(name), interval="minute10",count=5)
    dev = list(df[:-1]['close'] - df[:-1]['open']) #+,- 판별리스트 (10분봉 종가-시가)
    # #판별리스트 --++ 이면 구매
    
    if dev[0]<0 and dev[1]<0 and dev[2]<0 and dev[3]<0:
        cost = cost*0.9995
        print(upbit.buy_market_order("{}".format(name), cost))    

#판매함수#만약 판매 중이 5분이상 지속된다면 취소후 다시 판매함수실행
def sell(name, asset):
    global sell_time
    miss = upbit.get_order(name) # 미체결건 조회
    if len(miss) > 0: #미체결건이 존재하면 
        if miss[0]['side'] == 'ask' and time.time() - sell_time > 300: #미체결건이 매도고 매도한지 5분이 지났다면
            uuid = miss[0]['uuid']
            upbit.cancel_order(uuid=uuid)   #미체결건 취소

    buy_price = float(upbit.get_balance(name,verbose=True)['avg_buy_price']) #평단가 확인
    current_price = pyupbit.get_current_price("{}".format(name))    #현재가 확인
    volume = upbit.get_balance(name)                                #코인 보유량 확인
    
    #손절
    if current_price <= buy_price*0.875:  #손절가가 되면 전량 매도, 시간 기록
        print(upbit.sell_market_order("{}".format(name),volume=volume))
        sell_time = time.time()

    #익절
    elif current_price >= buy_price*1.02:
        print(upbit.sell_market_order("{}".format(name), volume=volume))
        sell_time = time.time() 

                         
while True:
    coin_names = ['KRW-LSK','KRW-STRK']
    for coin_name in coin_names:
        
        cost = upbit.get_balance_t() #현재 보유 원화
        asset = upbit.get_balances()

        #만약 코인을 보유중이라면 보유 코인 이름 확인해서 판매 함수
        #아니라면 구매 함수
        if len(asset)>2:
            for a in asset[1:-1]:
                if a['currency'] == coin_name:
                    sell(asset,coin_name)
        
        #asset에 코인을 보유중 이라면 보유 코인 이름 확인 후 보유코인이 아닐시 구매 보유코인이면 continue
        #asset에 코인을 보유중이 아니라면 바로 구매
        chk_coin = []
        for a in asset[1:-1]:
            chk_coin.append(a['currency'])

        if coin_name in chk_coin:
            continue
        else:
            if len(chk_coin) == 0:
                cost = cost/2
            search_buy(cost,coin_name)