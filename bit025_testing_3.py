import pyupbit
import time

access = "3ne7DHtdIJmaEcP2lynfp7QXUF5gkM3NlQ3O6oj0"
secret = "3EpuiiMfJXDCE3LInUOgN3Txh3ANj0uYJEpWoBon"

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


def search_buy(cost, name, d):
    if cost < 1:
        return 0 
    df = pyupbit.get_ohlcv("{}".format(name), interval="minute10",count=5)
    dev = list(df[:-1]['close'] - df[:-1]['open']) #+,- 판별리스트 (10분봉 종가-시가)

    # #판별리스트 --++ 이면 구매
    d0,d1,d2,d3 = d
    
    if eval(f'{dev[0]}{d0}0 and {dev[1]}{d1}0 and {dev[2]}{d2}0 and {dev[3]}{d3}0'):
        cost = cost*0.9995
        print(upbit.buy_market_order("{}".format(name), cost))    

#판매함수#만약 판매 중이 5분이상 지속된다면 취소후 다시 판매함수실행
def sell(name, asset, minus, plus):
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
    if current_price <= buy_price*minus:  #손절가가 되면 전량 매도, 시간 기록
        print(upbit.sell_market_order("{}".format(name),volume=volume))
        sell_time = time.time()

    #익절
    elif current_price >= buy_price*plus:
        print(upbit.sell_market_order("{}".format(name), volume=volume))
        sell_time = time.time() 

coin_names = ['KRW-LSK','KRW-STRK']    
params = {'KRW-LSK':(0.875, 1.02, ['<','<','<','<']), 'KRW-STRK':(0.9, 1.02, ['<','<','<','<']), 'KRW-STRAX':(0.8, 1.025, ['>','>','<','<'])}

while True:
    for coin_name in (coin_names):
        minus, plus, d = params[coin_name]

        cost = upbit.get_balance_t() #현재 보유 원화
        asset = upbit.get_balances()
        
        #보유 코인 리스트 구하기
        chk_coin = []
        for a in asset[1:-1]:
            chk_coin.append('KRW-'+a['currency'])
        #코인 이름이 보유코인 리스트에 있으면 판매함수 실행
        if  coin_name in chk_coin:
            sell(coin_name,asset,minus,plus)
        
        else: #코인을 보유중이 아니라면 바로 구매
            if len(coin_names)-1 != len(chk_coin): #보유 코인 갯수에 따라 cost조절
                cost = cost/(len(coin_names)-len(chk_coin))
            search_buy(cost,coin_name,d)