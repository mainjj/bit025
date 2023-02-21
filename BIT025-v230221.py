import pyupbit
from datetime import datetime
from numba import jit
import numpy as np
import math
import time

access = "3ne7DHtdIJmaEcP2lynfp7QXUF5gkM3NlQ3O6oj0"
secret = "3EpuiiMfJXDCE3LInUOgN3Txh3ANj0uYJEpWoBon"

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

##############################################################################################################

#구매용 추세 전환
@jit(nopython=True)
def trend_reversal_buy1(df):
    if df[0,0] - df[0,3] == 0 or df[1,0] - df[1,3] == 0 or df[2,0] - df[2,3] == 0:
        return False
    if df[0,3] - df[0,0] < 0 and df[2,3] - df[2,0]>0: 
        if np.abs(df[1,3] - df[1,0])*2 <= min(df[1,3], df[1,0]) - df[1,2]:
            if max(df[1,3],df[1,0]) <= min(df[2,0], df[2,3]) :
                return True
@jit(nopython=True)
def trend_reversal_buy2(df):
    if df[0,0] - df[0,3] == 0 or df[1,0] - df[1,3] == 0 or df[2,0] - df[2,3] == 0:
        return False
    if df[0,3] - df[0,0]<0 and df[1,3] - df[1,0]>0 and df[2,3] - df[2,0]>0:
        if df[0,0] <df[1,3]:
            return True
@jit(nopython=True)
def trend_reversal_buy3(df):
    if df[0,0] - df[0,3] == 0 or df[1,0] - df[1,3] == 0 or df[2,0] - df[2,3] == 0:
        return False
    if df[0,3] - df[0,0]<0 and df[1,3] - df[1,0]>0 and df[2,3] - df[2,0]>0:
        if (df[0,3] + df[0,0])/2 >= df[1,3]:
            if df[2,3]>df[0,0]:
                return True

#판매용 추세 전환
@jit(nopython=True)
def trend_reversal_sell1(df):
    if df[0,0] - df[0,3] == 0 or df[1,0] - df[1,3] == 0 or df[2,0] - df[2,3] == 0:
        return False
    if df[0,3] - df[0,0] > 0 and df[2,3]-df[2,0] < 0:
        if np.abs(df[1,3]-df[1,0]) * 2 <= min(df[1,3],df[1,0]) - df[1,2]:
            if min(df[1,0],df[1,3]) >= max(df[2,0],df[2,3]):
                return True
@jit(nopython=True)
def trend_reversal_sell2(df):
    if df[0,0] - df[0,3] == 0 or df[1,0] - df[1,3] == 0 or df[2,0] - df[2,3] == 0:
        return False
    if df[0,3] - df[0,0]>0 and df[1,3] - df[1,0]<0 and df[2,3] - df[2,0]<0:
        if df[0,0]<df[1,3]:
            return True
@jit(nopython=True)
def  trend_reversal_sell3(df):
    if df[0,0] - df[0,3] == 0 or df[1,0] - df[1,3] == 0 or df[2,0] - df[2,3] == 0:
        return False
    if df[0,3] - df[0,0]>0 and df[1,3] - df[1,0]<0 and df[2,3] - df[2,0]<0:
        if (df[0,3] + df[0,0])/2 <= df[1,3]:
            if df[2,3]< df[0,0]:
                return True

##############################################################################################################

#파라미터 선언
#           name  :  minus, plus, pass_candle, limit_per, target_min
params = {'KRW-REP':(0.94,  1.01,   3,  0.9,    5),\
        'KRW-PUNDIX':(0.91, 1.01, 3, 0.9, 15),\
        'KRW-STRK':(0.97, 1.01, 3, 0.9, 3),\
        'KRW-BTG':(0.97, 1.01, 3, 0.9, 5)}

sell_prot = {'KRW-STRK':0,'KRW-PUNDIX':0,'KRW-REP':0,'KRW-BTG':0}
buy_time = {'KRW-STRK':0,'KRW-PUNDIX':0,'KRW-REP':0,'KRW-BTG':0}
sell_time = {'KRW-STRK':0,'KRW-PUNDIX':0,'KRW-REP':0,'KRW-BTG':0}

##############################################################################################################

#loop()
while True:
    try:
        for coin_name in params:

        
            #DATA SETTING        
            minus, plus, pass_candle, limit_per, target_min = params[coin_name]

            cost = upbit.get_balance_t() #현재 보유 원화
            asset = upbit.get_balances()
            
            chk_coin = []   #보유 코인 리스트
            for a in asset[1:-1]:
                chk_coin.append('KRW-'+a['currency'])
            
            if len(chk_coin)==0: #보유 코인이 0개면 cost 절반만 투자
                cost = cost/2

            
            #df는 추세 파악에 사용할 정도만 가져오기 
            df = pyupbit.get_ohlcv("KRW-REP",interval='minute{}'.format(target_min),count=4).to_numpy()[:-1]

    ##############################################################################################################

            #MAIN()
            #coin_name이 보유 코인에 있으면 판매함수 실행 (판매 함수란, 손절 익절 포함임)
            if coin_name in chk_coin: 
                
            ##############################################################################################################
                
                #coin_name에 맞는 coin 별 데이터 가져오기
                buy_price = float(upbit.get_balance(coin_name,verbose=True)['avg_buy_price']) #평단가 확인
                current_price = pyupbit.get_current_price("{}".format(coin_name))    #현재가 확인
                volume = upbit.get_balance(coin_name)                                #코인 보유량 확인

            ##############################################################################################################
                print('-'*50)
                print(coin_name,'\t',round(current_price/buy_price*100 - 100,2),'\t',sell_prot[coin_name])
                #미체결건 취소
                buy_time = {'KRW-STRK':0,'KRW-PUNDIX':0,'KRW-REP':0,'KRW-BTG':0}
                
                miss = upbit.get_order(coin_name) # 미체결건 조회
                if len(miss) > 0: #미체결건이 존재하면 
                    if time.time() - sell_time[coin_name] >60:
                        uuid = miss[0]['uuid']
                        upbit.cancel_order(uuid=uuid)   #미체결건 취소
                        
            ##############################################################################################################

                #손절 함수, 매 loop 돌아가야함
                if current_price <= buy_price*minus:  #손절가가 되면 전량 매도, 시간 기록
                    print(upbit.sell_market_order("{}".format(coin_name),volume=volume))
                    sell_time[coin_name] = time.time()
                    continue
            ##############################################################################################################
                #익절

                #sell prot == 0 일때 plus를 넘으면 1로 변경
                if sell_prot[coin_name] == 0:
                    if current_price >= buy_price*plus:
                        sell_prot[coin_name] = 1
                
                #sell prot == 1 일때
                else:
                    #target_min봉 pass_candel개 기다림
                    if time.time() - buy_time[coin_name] > 60*pass_candle*target_min: ### 15분만큼 기다림
                    #plus보다 떨어지면 판매
                        if buy_price * plus >= current_price:
                            print(upbit.sell_market_order("{}".format(coin_name), volume=volume))
                            sell_prot[coin_name] = 0
                            sell_time[coin_name] = time.time()
                            continue

                    #최고가 대비 limit per만큼 떨어지면 판매
                        temp_cnt = math.ceil((time.time() - buy_time[coin_name])/60/target_min)
                        temp_df = pyupbit.get_ohlcv("KRW-REP",interval='minute{}'.format(target_min),count=temp_cnt).to_numpy()[:,1]

                        if ((max(temp_df) - buy_price) * limit_per) + buy_price>=current_price:
                            print(upbit.sell_market_order("{}".format(coin_name), volume=volume))
                            sell_prot[coin_name] = 0
                            sell_time[coin_name] = time.time()
                            continue
                    
                    #추세전환 나오면 판매
                        if trend_reversal_sell1(df=df) or trend_reversal_sell2(df=df) or trend_reversal_sell3(df=df):
                            print(upbit.sell_market_order("{}".format(coin_name), volume=volume))
                            sell_prot[coin_name] = 0
                            sell_time[coin_name] = time.time()
                            continue
                
            ########################################################################################################################
            #구매함수 실행
            else:
                    
                #돈이 없으면 판매함수만 실행시키기 (cost define해주기)
                if cost < 1:
                    continue 
                # #추세전환 확인 시 구매
                # if trend_reversal_buy1(df=df) or trend_reversal_buy2(df=df) or trend_reversal_buy3(df=df):
                #     cost = cost*0.9995
                #     print(upbit.buy_market_order("{}".format(coin_name), cost))   
                #     buy_time[coin_name] = time.time()
                print('do buy ',coin_name)
                #추세전환 확인 시 구매
                if trend_reversal_buy1(df=df):
                    cost = cost*0.9995
                    print(upbit.buy_market_order("{}".format(coin_name), cost))   
                    buy_time[coin_name] = time.time()

                    print(trend_reversal_buy1)
                    continue
                if trend_reversal_buy2(df=df):
                    cost = cost*0.9995
                    print(upbit.buy_market_order("{}".format(coin_name), cost))   
                    buy_time[coin_name] = time.time()

                    print(trend_reversal_buy2)
                    continue
                if trend_reversal_buy3(df=df):
                    cost = cost*0.9995
                    print(upbit.buy_market_order("{}".format(coin_name), cost))   
                    buy_time[coin_name] = time.time()

                    print(trend_reversal_buy3)
                    continue
            ########################################################################################################################

    except Exception as e:
        if '{}'.format(e) == 'Expecting value: line 1 column 1 (char 0)' or '{}'.format(e) == "'NoneType' object is not subscriptable" or '{}'.format(e) == 'JSONDecodeError':
            time.sleep(1)
        else:
            print(f'{datetime.now()} [에러 발생] COIN-NAME: {coin_name}')
            print(e)
            time.sleep(1)
