import sys
import websocket
import _thread
import urllib.request       #kabusapi_sendorder_margin_pay_ClosePositionOrder
import json
import pprint
import datetime
import configparser

#----------------------------------------------------------
import KABUPOSI
# import KABUCANCEL
# import kabu_CancelOrder
import kabu_CheckOrders
#----------------------------------------------------------
# AccessURL = 'http://localhost:18080/kabusapi/sendorder'
AccessURL = 'http://localhost:18081/kabusapi/sendorder'

# AccessURLwebsocket = 'ws://localhost:18080/kabusapi/websocket'
# AccessURLwebsocket = 'ws://localhost:18081/kabusapi/websocket'
#----------------------------------------------------------

conf = configparser.ConfigParser()
# conf = configparser.ConfigParser()
# conf.sections()
# conf.read('./settings.ini')
conf.read('./settings.ini')

# APIPassword = conf['kabuAPI']['APIPassword']
Password = conf['kabuAPI']['Password']
Token = conf['kabuAPI']['Token']

Issue1 = conf['kabuAPI']['Issue1']
Issue2 = conf['kabuAPI']['Issue2']
Issue3 = conf['kabuAPI']['Issue3']

LONG0 = conf['kabuAPI']['LONG0']
LONG1st = conf['kabuAPI']['LONG1st']
LONG2nd = conf['kabuAPI']['LONG2nd']
LONG3rd = conf['kabuAPI']['LONG3rd']
LONG4th = conf['kabuAPI']['LONG4th']

LONGLOSS = conf['kabuAPI']['LONGLOSS']
FrontOrderType = conf['kabuAPI']['FrontOrderType']      # 執行条件  10:成行 20:指値
# SMACounts = conf['kabuAPI']['SMACounts']

LogLevel1 = conf['kabuAPI']['LogLevel1']
LogLevel2 = conf['kabuAPI']['LogLevel2']
LogLevel3 = conf['kabuAPI']['LogLevel3']
LogLevel4 = conf['kabuAPI']['LogLevel4']
LogLevel5 = conf['kabuAPI']['LogLevel5']

# LONGSimulate = conf['kabuAPI']['LONGSimulate']
PauseTime = conf['kabuAPI']['PauseTime']
#------------------------------------------------------------------------------
#							＊
#							＊					        profit_taking = 1   ( Profit・強制終了)
#						＊		＊	LONG3rd				D_LONGLOSS == 0 ? 買値までHold
#						＊		＊
#					＊	LONG2nd     ＊	
#					＊				＊    LONG4th       (Top - LONG3rd)>LONG4th で利益確定
#				＊	LONG1st				＊
#				＊						＊
#	＊		＊	LONG0						＊
#	＊		＊								＊
#		＊									＊
#												＊	LONGLOSS			Loss-cut(
# 	SMACounts：移動平均カウント
#------------------------------------------------------------------------------
D_LONG0 = int(LONG0)
D_LONG1st = int(LONG1st)
D_LONG2nd = int(LONG2nd)
# F_LONG3rd = float(LONG3rd)
D_LONG3rd = int(LONG3rd)
D_LONG4th = int(LONG4th)

D_LONGLOSS = int(LONGLOSS)

D_LogLevel1 = int(LogLevel1)
D_LogLevel2 = int(LogLevel2)
D_LogLevel3 = int(LogLevel3)
D_LogLevel4 = int(LogLevel4)
D_LogLevel5 = int(LogLevel5)

S_long_simulate = ''
D_long_simulate = 0
S_short_simulate = ''
D_short_simulate = 0

S_long_position_mask = ''
D_long_position_mask = 0
S_short_position_mask = ''
D_short_position_mask = 0

S_profit_taking = ''
D_profit_taking = 0
S_short_covering = ''
D_short_covering = 0
#----------------------------------------------------------
d_TopLast = int(0)
D_TopBidPrice = int(0)
d_BottomPrice = int(0)
d_LosscutPrice = int(0)
D_TargetPrice = int(0)
D_Current = 0
D_CurrentLast = int(0)
D_BidPrice = int(0)

#----------------------------------------------------------
S_BidResult = ''
S_BidOrderId = ''
D_CancelSt = int(0)

T_Now = datetime.datetime.now().time()
T_BidTime = datetime.datetime.now().time()      #T_Now                       #Purchase time
S_CurrentTime = T_Now.strftime("%H:%M:%S:%f")

SimulateTime = ""   #S_CurrentTime""                    # for simurate

# d_TopLast1 = int(0)
# D_TopBidPrice1 = int(0)
# d_BottomPrice1 = int(0)
# d_LosscutPrice1 = int(0)
# D_TargetPrice1 = int(0)
# D_CurrentLast1 = int(0)
# D_BidPrice1 = int(0)
# # T_Now = datetime.datetime.now().time()
# T_BidTime1 = datetime.datetime.now().time()      #T_Now                       #Purchase time

# d_TopLast2 = int(0)
# D_TopBidPrice2 = int(0)
# d_BottomPrice2 = int(0)
# d_LosscutPrice2 = int(0)
# D_TargetPrice2 = int(0)
# D_CurrentLast2 = int(0)
# D_BidPrice2 = int(0)
# # T_Now = datetime.datetime.now().time()
# T_BidTime2 = datetime.datetime.now().time()      #T_Now                       #Purchase time
# MessageList = {}

#----------------------------------------------------------
s_DateTime = T_Now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
WritefileName = './Result' + s_DateTime + '.csv'
# s_DateTime = T_Now.strftime("result")  #YYYY-MM-DDTHH:MM:SS
# WritefileName = './Result' + s_DateTime + '.csv'
F_Write = False;
WriteCsvFile = open(WritefileName, 'w')     #, newline='')
if (WriteCsvFile):
    F_Write = True;
    if(F_Write):
        s_dsp = "True = %s" % (WritefileName)
        WriteCsvFile.write(s_dsp + '\n')
    else:
        s_dsp = "False = %s" % (WritefileName)
    print(s_dsp)



#----------------------------------------------------------
# ３．注文発注（信用）
# （２）返済（決済順序）
# コマンド：python kabusapi_sendorder_margin_pay_ClosePositionOrder.pyより
def Ttrading_Stop(ws, message, Symbol):

    global F_Write
    global WriteCsvFile
    global Password
    global Token
    global PauseTime
    global D_long_simulate

    # global D_LONG0
    # global D_LONG1st
    # Use Sub Module --------------------------------------
    global d_TopLast
    global D_TopBidPrice
    global d_BottomPrice
    global d_LosscutPrice
    global D_TargetPrice
    global D_CurrentLast
    global D_BidPrice
    
    global S_CurrentTime
    global T_Now
    global S_SellTime
    #------------------------------------------------------
    # except simulation
    if(ws is not None and message is not None):
        # global T_BidTime
        T_Now = datetime.datetime.now().time()
        s_Time = T_Now.strftime("%H:%M:%S:%f")

    else:
        s_Time = SimulateTime
        S_CurrentTime = SimulateTime
        s_BidTime = SimulateTime        

    S_SellTime = s_Time
    s_dsp = "Ttrading_Stop(S ,%s),%s" % (Symbol, S_SellTime)
    # if(D_LogLevel4 > 0):
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')
    s_dsp = ''
    #------------------------------------------------------
    # 成行で終了
    obj = { 'Password': Password,
        'Symbol': Symbol,           #銘柄
        'Exchange': 1,              #市場コード 1:東証
        'SecurityType': 1,          #商品種別   1:株式
        'Side': '1',                #売買区分   1:売, 2:買
        'CashMargin': 3,            #信用区分   1:現物, 2:新規, 3:返済
        'MarginTradeType': 3,       #信用取引区分   1:制度信用, 2:一般信用（長期）, 3:一般信用（デイトレ）
        'DelivType': 2,     #受渡区分   0:指定なし, 1:自動振替, 2:お預り金(信用返済は指定必須)          #0:0010 不明なエラー(ERROR_CD_000_001_007)
        'AccountType': 4,           #口座種別       4:特定, 2:一般, 12:法人                          2:一般 時の時エラー
        'Qty': 100,                 #注文数量(信用一括返済の場合、返済したい合計数量を入力)
        'ClosePositionOrder': 1,    #決済順序   (1:日付（古い順）、損益（低い順）)
        'FrontOrderType': 10,       #執行条件   10:成行, 30:逆指値, 20:指値(発注したい金額)
        'Price': 0,                 #注文価格(FrontOrderTypeで成行を指定した場合、0を指定)
        'ExpireDay': 0,     #注文有効期限(yyyyMMdd形式 「0」を指定すると、kabuステーション上の発注画面の「本日」に対応する日付として扱います)
        'ReverseLimitOrder': {  #逆指値条件 (FrontOrderTypeで逆指値を指定した場合のみ必須)
                               'TriggerSec': 1,         #1.発注銘柄 2.NK225指数 3.TOPIX指数
                               'TriggerPrice': 0,
                               'UnderOver': 1,          #1.以下 2.以上
                               'AfterHitOrderType': 1,  #1.成行 2.指値 3. 不成
                               'AfterHitPrice': 0
                               }
    }
    # if(D_LogLevel4 > 0):
    pprint.pprint(obj)
  
    json_data = json.dumps(obj).encode('utf-8')
    # if(D_LogLevel5 > 0):
    pprint.pprint(json_data)

    #------------------------------------------------------
    # except simulation
    if(ws is not None and message is not None and D_long_simulate == 0):
        # Errorで発行できなかった
        # s_dsp = "Ttrading_Stop(),Symbol:%s,Qty:%s,FrontOrderType:%s," % (json_data["Symbol"], json_data["Qty"], json_data["FrontOrderType"])
        # print(s_dsp)
        # if(F_Write):
        #     WriteCsvFile.write(s_dsp + '\n')

        url = 'http://localhost:18080/kabusapi/sendorder'
        req = urllib.request.Request(url, json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', Token);

        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                s_dsp = "Ttrading_Stop(),res.status,%s,res.reason::%s," % (res.status, res.reason)
                for header in res.getheaders():
                    print(header)

                content = json.loads(res.read())

                pprint.pprint(content)

                # if(F_Write):            #print(res.status, res.reason)
                #     WriteCsvFile.write(s_dsp + '\n')
                # Errorで発行できなかった
                # s_dsp = "Ttrading_Stop(),Symbol:%s,Qty:%s,FrontOrderType:%s," % (content["Symbol"], content["Qty"], content["FrontOrderType"])
                # print(s_dsp)
                # if(F_Write):
                #     WriteCsvFile.write(s_dsp + '\n')

        except urllib.error.HTTPError as e:
            print("----- urllib.error.HTTPError ------------------------------------------")
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
            if(F_Write):
                s_dsp = content
                WriteCsvFile.write(s_dsp + '\n')

            ws.close()

        except Exception as e:
            print("----- Exception Error ------------------------------------------")
            print(e)
            if(F_Write):
                s_dsp = e
                WriteCsvFile.write(s_dsp + '\n')

            ws.close()

    else:
        # else --------------------------------------------
        s_dsp = "D_long_simulate:%d ----- Simulation -----" % (D_long_simulate)
        print(s_dsp)

    #------------------------------------------------------
    if(F_Write):            #print(res.status, res.reason)
        WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------
    # except simulation
    if(ws is not None and message is not None):
        # global T_BidTime
        T_Now = datetime.datetime.now().time()
        s_Time = T_Now.strftime("%H:%M:%S:%f")

    else:
        s_Time = SimulateTime
        S_CurrentTime = SimulateTime
        s_BidTime = SimulateTime        

    S_SellTime = s_Time
    s_dsp = "Ttrading_Stop(E ,%s),%s" % (Symbol, s_Time)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')    
    #------------------------------------------------------


#----------------------------------------------------------
# ３．注文発注（信用）  新規新規買い
def LongOrder(ws, message, Symbol):
    global Password
    global Token
    global S_CurrentTime 
    global PauseTime
    # global LONG1st
    global LONGLOSS
    global FrontOrderType
    global D_long_simulate

    global D_CurrentLast
    global D_BidPrice
    global S_BidResult
    global S_BidOrderId
    #------------------------------------------------------
    global T_Now
    global T_BidTime
    global F_Write
    global WriteCsvFile
    #------------------------------------------------------
    s_FrontOrderType = '20'
    if(FrontOrderType == '10'):         # 執行条件       10:成行 20:指値 
        s_FrontOrderType = '10'
        BidPrice = '0'
    else:
        BidPrice = str(D_BidPrice)
    #------------------------------------------------------
    global T_Now
    global T_BidTime

    T_Now = datetime.datetime.now().time()
    s_Time = T_Now.strftime("%H:%M:%S:%f")
    T_BidTime = T_Now
    s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
    S_SellTime = T_Now.strftime("%H:%M:%S:%f")
    s_dsp = " LongOrder --- %s, BidTime:%s, SellTime:%s" % (s_Time, s_BidTime, S_SellTime)
    print(s_dsp)
    
    d_profit = 0
    s_dsp = "800 LONG,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, D_Current-D_CurrentLast, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------
    obj = { 'Password': Password,
        'Symbol': Symbol,        #銘柄          'Symbol': '6521',       #6521：オキサイド
        'Exchange': 1,          #1:東証
        'SecurityType': 1,      #1:株式
        'Side': '2',            #2:買
        'CashMargin': 2,        #信用区分       2:新規
        'MarginTradeType': 3,   #信用取引区分   1:制度信用, 2:一般信用（長期）, 3:一般信用（デイトレ）
        'DelivType': 0,         #受渡区分       0:指定無し
        # 'AccountType': 2,       #口座種別       2：一般 
        'AccountType': 4,       #口座種別       4:特定, 2:一般, 12:法人
        'Qty': 100,             #注文数量       100

        'FrontOrderType': s_FrontOrderType,     #執行条件       10:成行 20:指値 
        'Price': BidPrice,                      #注文価格
        # 'FrontOrderType': 20,   #執行条件       20:指値 10:成行
        # 'Price': BidPrice,      #注文価格

        'ExpireDay': 0,         #注文有効期限   0:today     yyyyMMdd
        # 'ReverseLimitOrder': {}     #逆指値条件
        'ReverseLimitOrder': {  #逆指値条件
                            #    'TriggerSec': 2, #1.発注銘柄 2.NK225指数 3.TOPIX指数
                            #    'TriggerPrice': 30000,
                            #    'UnderOver': 2, #1.以下 2.以上
                            #    'AfterHitOrderType': 2, #1.成行 2.指値 3. 不成
                            #    'AfterHitPrice': 8435
                               'TriggerSec': 1,         #1.発注銘柄 2.NK225指数 3.TOPIX指数
                               'TriggerPrice': BidPrice,
                               'UnderOver': 2,          #1.以下 2.以上
                               'AfterHitOrderType': 2,  #1.成行 2.指値 3. 不成
                               'AfterHitPrice': BidPrice
                               }
    }
    if(ws is not None and message is not None):
        json_data = json.dumps(obj).encode('utf-8')    
    #------------------------------------------------------
    pprint.pprint(json_data)
    s_dsp = "801 D_long_simulate:%d,%s,%s,,,%d,----- Long Order json_data -----" % (D_long_simulate, Symbol, S_CurrentTime, D_BidPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')

    if(ws is not None and message is not None and D_long_simulate == 0):
        url = 'http://localhost:18080/kabusapi/sendorder'
        req = urllib.request.Request(url, json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', Token)
        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                print("-----------------------------------------------")
                content = json.loads(res.read())
                pprint.pprint(content)
                #----- {'OrderId': '20210708A01N28692121', 'Result': 0} -----
                S_BidResult = content["Result"]
                S_BidOrderId = content["OrderId"]
                s_dsp = "----- Result:%s/OrderId:%s  (BidPrice:%6d,Symbol:%s, D_CurrentLast:%6d) -----" % (content["Result"], content["OrderId"], BidPrice, Symbol, D_CurrentLast)
                print(s_dsp)
        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
        except Exception as e:
            print(e)
    else:
        # else --------------------------------------------
        print("D_long_simulate:%d ----- 発行マスク -----", D_long_simulate)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------
    T_Now = datetime.datetime.now().time()
    s_Time = T_Now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(201),----- LongOrder -----" % (s_Time,s_BidTime, S_SellTime)
    print(s_dsp)
    #------------------------------------------------------


#----------------------------------------------------------
# ３．注文発注（信用）逆指値 新規買い
def LongReverseLimitOrder(ws, message, Symbol):
    global D_LONG1st
    global Password
    global Token
    global S_CurrentTime 
    global PauseTime
    global LONGLOSS
    global FrontOrderType
    global D_long_simulate
    global D_CurrentLast
    global D_BidPrice
    global S_BidResult
    global S_BidOrderId
    #------------------------------------------------------
    global T_Now
    global T_BidTime
    global F_Write
    global WriteCsvFile
    #------------------------------------------------------
    s_FrontOrderType = '20'
    if(FrontOrderType == '10'):         # 執行条件       10:成行 20:指値 
        s_FrontOrderType = '10'
        s_BidPrice = '0'
    else:
        s_BidPrice = str(D_BidPrice)
    #------------------------------------------------------
    global T_Now
    global T_BidTime

    T_Now = datetime.datetime.now().time()
    s_Time = T_Now.strftime("%H:%M:%S:%f")
    T_BidTime = T_Now
    s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
    S_SellTime = T_Now.strftime("%H:%M:%S:%f")
    s_dsp = " LongOrder --- %s, BidTime:%s, SellTime:%s" % (s_Time, s_BidTime, S_SellTime)
    print(s_dsp)
    
    d_profit = 0
    s_dsp = "800 LongReverseLimitOrder,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, D_Current-D_CurrentLast, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------

    d_TriggerPrice = D_BidPrice + D_LONG1st

    obj = { 'Password': Password,
        'Symbol': Symbol,       #銘柄
        'Exchange': 1,          #1:東証
        'SecurityType': 1,      #1:株式
        'Side': '2',            #2:買
        'CashMargin': 2,        #信用区分       2:新規
        'MarginTradeType': 3,   #信用取引区分   3:一般信用（デイトレ）, 1:制度信用, 2:一般信用（長期）
        'DelivType': 0,         #受渡区分       0:指定無し
        'AccountType': 4,       #口座種別       4:特定, 2:一般, 12:法人
        'Qty': 100,             #注文数量       100

        # 'FrontOrderType': s_FrontOrderType,     #執行条件       10:成行 20:指値 
        'FrontOrderType': 20,   #執行条件       10:成行 20:指値 
        'Price': s_BidPrice,                    #注文価格

        'ExpireDay': 0,         #注文有効期限   0:today     yyyyMMdd
        # 'ReverseLimitOrder': {}     #逆指値条件
        'ReverseLimitOrder': {  #逆指値条件
                            #    'TriggerSec': 2, #1.発注銘柄 2.NK225指数 3.TOPIX指数
                            #    'TriggerPrice': 30000,
                            #    'UnderOver': 2, #1.以下 2.以上
                            #    'AfterHitOrderType': 2, #1.成行 2.指値 3. 不成
                            #    'AfterHitPrice': 8435
                               'TriggerSec': 1,         #1.発注銘柄 2.NK225指数 3.TOPIX指数
                               'TriggerPrice': d_TriggerPrice,
                               'UnderOver': 2,          #1.以下 2.以上
                               'AfterHitOrderType': 2,  #1.成行 2.指値 3. 不成
                               'AfterHitPrice': d_TriggerPrice
                               }
    }

    if(ws is not None and message is not None):
        json_data = json.dumps(obj).encode('utf-8')    
    #------------------------------------------------------
    pprint.pprint(json_data)
    s_dsp = "801 d_TriggerPrice:%d,%s,%s,,,%d,----- Long Order json_data -----" % (d_TriggerPrice, Symbol, S_CurrentTime, D_BidPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')

    # if(ws is not None and message is not None and D_long_simulate == 0):
    if(D_long_simulate == 0):
        url = AccessURL     #'http://localhost:18080/kabusapi/sendorder'
        req = urllib.request.Request(url, json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', Token)
        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                print("-----------------------------------------------")
                content = json.loads(res.read())
                pprint.pprint(content)
                #----- {'OrderId': '20210708A01N28692121', 'Result': 0} -----
                S_BidResult = content["Result"]
                S_BidOrderId = content["OrderId"]
                s_dsp = "----- Result:%s/OrderId:%s  (BidPrice:%s,Symbol:%s, D_CurrentLast:%6d) -----" % (content["Result"], content["OrderId"], s_BidPrice, Symbol, D_CurrentLast)
                print(s_dsp)
        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
        except Exception as e:
            print(e)
    else:
        # else --------------------------------------------
        print("LongReverseLimitOrder:%d - %d ---- 発行マスク -----", D_BidPrice, d_TriggerPrice)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------
    T_Now = datetime.datetime.now().time()
    s_Time = T_Now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(201),----- LongOrder -----" % (s_Time,s_BidTime, S_SellTime)
    print(s_dsp)
    #------------------------------------------------------



#----------------------------------------------------------
# ３．注文発注（信用）
#  売り　買い戻し
def ShortSelling(ws, message, Symbol):
    global Password
    global Token
    global S_CurrentTime 
    global PauseTime
    # global LONG1st
    # global LONGLOSS
    global FrontOrderType
    global D_long_simulate

    global D_CurrentLast
    global D_BidPrice
    global S_BidResult
    global S_BidOrderId
    #------------------------------------------------------
    global T_Now
    global T_BidTime
    global F_Write
    global WriteCsvFile
    #------------------------------------------------------
    s_FrontOrderType = '20'
    if(FrontOrderType == '10'):         # 執行条件       10:成行 20:指値 
        s_FrontOrderType = '10'
        BidPrice = '0'
    else:
        BidPrice = str(D_BidPrice)
    #------------------------------------------------------
    global T_Now
    global T_BidTime

    T_Now = datetime.datetime.now().time()
    s_Time = T_Now.strftime("%H:%M:%S:%f")
    T_BidTime = T_Now
    s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
    S_SellTime = T_Now.strftime("%H:%M:%S:%f")
    s_dsp = " ShortSelling --- %s, BidTime:%s, SellTime:%s" % (s_Time, s_BidTime, S_SellTime)
    print(s_dsp)
    
    d_profit = 0
    s_dsp = "800 LONG,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, D_Current-D_CurrentLast, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------
    obj = { 'Password': Password,
        'Symbol': Symbol,       #銘柄
        'Exchange': 1,          #1:東証
        'SecurityType': 1,      #1:株式
        'Side': '1',            #1:売, 2:買
        'CashMargin': 2,        #信用区分       2:新規
        'MarginTradeType': 3,   #信用取引区分   1:制度信用, 2:一般信用（長期）, 3:一般信用（デイトレ）
        'DelivType': 0,         #受渡区分       0:指定無し
        'AccountType': 4,       #口座種別       4:特定, 2:一般, 12:法人
        'Qty': 100,             #注文数量       100
        # 'FrontOrderType': 20,   #執行条件       20:指値 10:成行
        'FrontOrderType': s_FrontOrderType,     #執行条件       10:成行 20:指値 
        'Price': BidPrice,                      #注文価格

        'ExpireDay': 0,         #注文有効期限   0:today     yyyyMMdd
        # 'ReverseLimitOrder': {}     #逆指値条件
        'ReverseLimitOrder': {  #逆指値条件
                            #    'TriggerSec': 2, #1.発注銘柄 2.NK225指数 3.TOPIX指数
                            #    'TriggerPrice': 30000,
                            #    'UnderOver': 2, #1.以下 2.以上
                            #    'AfterHitOrderType': 2, #1.成行 2.指値 3. 不成
                            #    'AfterHitPrice': 8435
                               'TriggerSec': 1,         #1.発注銘柄 2.NK225指数 3.TOPIX指数
                               'TriggerPrice': BidPrice,
                               'UnderOver': 2,          #1.以下 2.以上
                               'AfterHitOrderType': 2,  #1.成行 2.指値 3. 不成
                               'AfterHitPrice': BidPrice
                               }
    }
    if(ws is not None and message is not None):
        json_data = json.dumps(obj).encode('utf-8')    
    #------------------------------------------------------
    pprint.pprint(json_data)
    s_dsp = "801 D_short_simulate:%d, %s,%s,,,%d,----- Long Order json_data -----" % (D_short_simulate, Symbol, S_CurrentTime, D_BidPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')

    if(ws is not None and message is not None and D_long_simulate == 0):
        url = AccessURL     #'http://localhost:18080/kabusapi/sendorder'
        req = urllib.request.Request(url, json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', Token)
        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                print("-----------------------------------------------")
                content = json.loads(res.read())
                pprint.pprint(content)
                #----- {'OrderId': '20210708A01N28692121', 'Result': 0} -----
                S_BidResult = content["Result"]
                S_BidOrderId = content["OrderId"]
                s_dsp = "----- Result:%s/OrderId:%s  (BidPrice:%6d,Symbol:%s, D_CurrentLast:%6d) -----" % (content["Result"], content["OrderId"], BidPrice, Symbol, D_CurrentLast)
                print(s_dsp)
        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
        except Exception as e:
            print(e)
    else:
        # else --------------------------------------------
        print("D_long_simulate:%d ----- 発行マスク -----", D_long_simulate)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')
    #------------------------------------------------------
    T_Now = datetime.datetime.now().time()
    s_Time = T_Now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(201),----- ShortSelling -----" % (s_Time,s_BidTime, S_SellTime)
    print(s_dsp)
    #------------------------------------------------------



#----- 株価が変わった場合に呼ばれる関数 ----------------------
def Long_Symbol1(ws, message, Symbol, WriteCsvFile):

    global Password         # Use cancel
    global S_BidOrderId
    global D_CancelSt

    global Token
    global LONG0
    global LONG1st
    global LONG2nd
    global LONG3rd
    global LONG4th

    global LONGLOSS
    global D_LONGLOSS

    global D_LogLevel1
    global D_LogLevel2
    global D_LogLevel3
    global D_LogLevel4
    global D_LogLevel5
    # global SMACounts
    # global D_SMACounts

    global S_long_simulate
    global D_long_simulate
    global S_short_simulate
    global D_short_simulate

    global S_long_position_mask
    global D_long_position_mask
    global S_short_position_mask
    global D_short_position_mask

    global S_profit_taking
    global D_profit_taking
    global S_short_covering
    global D_short_covering

    global PauseTime

    global S_CurrentTime 
    global PauseTime

    global D_Current
    global PauseTime

    global d_TopLast
    global D_TopBidPrice
    global d_BottomPrice
    global d_LosscutPrice
    global D_TargetPrice
    global D_CurrentLast
    global D_BidPrice
    global T_Now
    global T_BidTime
    #------------------------------------------------------
    # global S_CurrentTime
    global F_Write
    # global WriteCsvFile

    #------------------------------------------------------
    # Get Long Position Setting
    conf = configparser.ConfigParser()
    conf.read('./TradeSymbol.ini')
    # conf.read('./settings.ini')
    # Callback message
    LogLevel1 = conf['kabuAPI']['LogLevel1']
    LogLevel2 = conf['kabuAPI']['LogLevel2']
    LogLevel3 = conf['kabuAPI']['LogLevel3']
    LogLevel4 = conf['kabuAPI']['LogLevel4']
    LogLevel5 = conf['kabuAPI']['LogLevel5']
    D_LogLevel1 = int(LogLevel1)
    D_LogLevel2 = int(LogLevel2)
    D_LogLevel3 = int(LogLevel3)
    D_LogLevel4 = int(LogLevel4)
    D_LogLevel5 = int(LogLevel5)

    Issue1 = conf['kabuAPI']['Issue1']
    Issue2 = conf['kabuAPI']['Issue2']
    Issue3 = conf['kabuAPI']['Issue3']
    # LONGSimulate = conf['kabuAPI']['LONGSimulate']
    PauseTime = conf['kabuAPI']['PauseTime']

    LONG0 = conf['kabuAPI']['LONG0']
    LONG1st = conf['kabuAPI']['LONG1st']
    LONG2nd = conf['kabuAPI']['LONG2nd']
    LONG3rd = conf['kabuAPI']['LONG3rd']
    LONG4th = conf['kabuAPI']['LONG4th']
    LONGLOSS = conf['kabuAPI']['LONGLOSS']
    D_LONG0 = int(LONG0)
    D_LONG1st = int(LONG1st)
    D_LONG2nd = int(LONG2nd)
    # F_LONG3rd = float(LONG3rd)
    D_LONG3rd = int(LONG3rd)
    D_LONG4th = float(LONG4th)

    D_LONGLOSS = int(LONGLOSS)
    #-------------------------------------------------------
    #　Event driven ----------------------------------------
    try:
        
        config = configparser.ConfigParser()            # ConfigParserクラスをインスタンス化
        config.read('.\TradeEvent.ini')
        S_long_simulate         = config['OrderEvent']['long_simulate']
        S_long_position_mask    = config['OrderEvent']['long_position_mask']
        D_long_simulate         = int(S_long_simulate)

        d_long_position_mask_last = D_long_position_mask
        D_long_position_mask    = int(S_long_position_mask)

        S_short_simulate        = config['OrderEvent']['short_simulate']
        S_short_position_mask   = config['OrderEvent']['short_position_mask']
        D_short_simulate        = int(S_short_simulate)
        D_short_position_mask   = int(S_short_position_mask)

        # buy_order         # 買い
        buy_order               = config['OrderEvent']['buy_order']
        d_buy_order             = int(buy_order)
        # lowest_buy_order  # 底値確認後の買い
        lowest_buy_order        = config['OrderEvent']['lowest_buy_order']
        d_lowest_buy_order      = int(lowest_buy_order)

        # highest_short_selling     # 高値確認後の空売り
        highest_short_selling   = config['OrderEvent']['highest_short_selling']
        d_highest_short_selling = int(highest_short_selling)
        # short_selling     # 空売り
        short_selling           = config['OrderEvent']['short_selling']         # short_selling : 即時売り
        d_short_selling         = int(short_selling)
        # profit_taking     # 利食い (利益確定売り)
        S_profit_taking         = config['OrderEvent']['profit_taking']
        D_profit_taking         = int(S_profit_taking) 
        # short_covering    # 空売りの買戻し
        S_short_covering        = config['OrderEvent']['short_covering']
        D_short_covering        = int(S_short_covering)

        change_ini_file         = config['kabuAPI']['change_ini_file']
        reset_bottom            = config['kabuAPI']['reset_bottom']

        # 空売りの買戻し short covering
        # Event値は'0'に戻す
        # if(buy_order != '0' or lowest_buy_order != '0' or highest_short_selling != '0' or short_selling != '0' or change_ini_file != '0'):
        if(buy_order != '0' or short_selling != '0' or change_ini_file != '0' or reset_bottom != '0'):
            s_dsp = "100 Event driven   buy:%d  L_buy:%d  H_short:%d  short:%d change_ini_file:%s" % (d_buy_order, d_lowest_buy_order, d_highest_short_selling, d_short_selling, change_ini_file)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            config['OrderEvent']['buy_order'] = '0'
            config['OrderEvent']['short_selling'] = '0'
            config['kabuAPI']['change_ini_file'] = '0'
            config['kabuAPI']['reset_bottom'] = '0'
            # config['OrderEvent']['long_simulate'] = '0' 保持
            # config['OrderEvent']['long_position_mask'] = '0' 保持
            # config['OrderEvent']['lowest_buy_order'] = '0' 保持
            # config['OrderEvent']['short_simulate'] = '0' 保持
            # config['OrderEvent']['highest_short_selling'] = '0' 保持        
            # INIファイルの生成・書き込み # 書き込みモードでオープン
            with open('.\TradeEvent.ini', 'w') as configfile:
                print('INIファイルの書き込み')                      #print()->'無しで出力
                # 指定したconfigファイルを書き込み
                # conf.optionxform = setstr
                config.write(configfile)        # 指定したconfigファイルを書き込み
            print('TradeEvent.INIファイルの書き込み')                      #print()->'無しで出力

    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        pprint.pprint(content)
    except Exception as e:
        print(e)
    #　Event driven ----------------------------------------
    #-------------------------------------------------------
    # except simulation
    if(ws is not None and message is not None):
        T_Now = datetime.datetime.now().time()
        s_Time = T_Now.strftime("%H:%M:%S:%f")
        S_CurrentTime = T_Now.strftime("%H:%M:%S:%f")
        s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
        now = datetime.datetime.now()
        # %d	10進数で月の始めから何日目かを表示。
        # %y	10進数で上2桁のない西暦年を表示。
        # %Y	10進数で上2桁が付いている西暦年を表示。
        # %m	10進数で月を表示。
        # &S	10進数で秒を表示。
        # %H	10進数で24時間計での時を表示。
        # %I	10進数で12時間計での時を表示。
        # %m	10進数で月を表示。
        # %M	10進数で分を表示。
        # s_Updtime = now.strftime("%Y%m%d")      # yyyyMMddHHmmss
        # print(s_Updtime)
        # s_Updtime = now.strftime("%I%M%S")
        # print(s_Updtime)
        s_Updtime = now.strftime("%Y%m%d%I%M%S")      # yyyyMMddHHmmss
        # print('=================' , s_Updtime)

        # s_Updtime = T_Now.strftime("%y/%M/%d%H%m%s")      # yyyyMMddHHmmss
        # print(s_Updtime)
        # s_Updtime.replace('/', '')
        # # s_Updtime = now.strftime("%y%M%d %H%m%s")      # yyyyMMddHHmmss
        # print(s_Updtime)
    # For simulation
    else:
        s_Time = SimulateTime
        S_CurrentTime = SimulateTime
        s_BidTime = SimulateTime
    #------------------------------------------------------
    # 利幅
    d_profit = 0
    if(D_BidPrice > 0):
        d_profit = D_Current - D_BidPrice
    # d_currentDiff <0:下げ相場 / >0:上げ相場
    d_currentDiff = 0
    if(D_CurrentLast != D_Current):
        d_currentDiff = D_Current - D_CurrentLast
    #------------------------------------------------------
    #======================================================
    # INIファイル切り替え =========================================
    if (change_ini_file != '0'):
        time = T_Now.strftime("%H%M%S")
        s_dsp = "110一時停止,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        print(s_dsp)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')

        s_DateTime = T_Now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
        WritefileName = './Result' + s_DateTime + '.csv'
        F_Write = False;
        WriteCsvFile = open(WritefileName, 'w')     #, newline='')
        if (WriteCsvFile):
            F_Write = True;
    # INIファイル切り替え =========================================

    # 銘柄１
    if(Symbol == Issue1 and Symbol is not None):
        if(reset_bottom != '0'):
            d_BottomPrice = D_Current
        #-------------------------------------------------------
        if(D_long_position_mask > 0 and d_long_position_mask_last == 0):
            s_dsp = "long_position_mask:%d (%s)" % (D_long_position_mask, d_long_position_mask_last)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            s_dsp = "--------------------"
            # Reset Diff
            D_TopBidPrice = D_Current
            # d_BottomPrice = D_Current
            d_TopLast = D_Current

        s_Time = S_CurrentTime
        #----------------------------------------------------------
        s_dsp = "200,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        if(D_LogLevel2 > 0):
            print(s_dsp)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')            
        #----- Position無し ----------
        d_profit = D_Current - d_BottomPrice
        if(D_BidPrice == 0):
            s_dsp = "211 No Position,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')

            #下げ相場　Bottom == Top
            if(D_CurrentLast > D_Current):
                D_TopBidPrice = D_Current
                if(d_BottomPrice > D_Current):
                    d_BottomPrice = D_Current
                # D_CurrentLast = D_Current
            #上げ相場　Keep Bottom AND Update Top
            else:
                # Position無し Top上げ
                if (D_TopBidPrice < D_Current):
                    D_TopBidPrice = D_Current
                    s_dsp = "212 Up Top,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                # "W"
                elif(D_TopBidPrice > D_Current):
                    s_dsp = "213 Top > Cur,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')

            d_topBottom = 0
            if(d_BottomPrice > 0):
                d_topBottom = D_TopBidPrice - d_BottomPrice
            else:
                d_BottomPrice = D_Current

            if(d_topBottom != 0):
                s_dsp = "DIFF:%d,%s,,---,%d,(Top:%d - Bottom:%d), L_0:%d, L_1st:%d, L_2nd:%d, L_Loss:%d, L_3rd:%d, L_4th:%d" % (d_topBottom, Symbol, D_Current, D_TopBidPrice , d_BottomPrice,D_LONG0, D_LONG1st, D_LONG2nd, D_LONGLOSS, D_LONG3rd, D_LONG4th)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

            if(d_currentDiff > 0):
                s_dsp = "214 UP,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            elif(d_currentDiff < 0):
                s_dsp = "215 Down,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            # else:
                # s_dsp = "216 Partial,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                # print(s_dsp)
                # if(F_Write):
                #     WriteCsvFile.write(s_dsp + '\n')
            # LONG
            # Profit taking or loss-cut
            # -----------------------------------------------------------------
            f_Long = False
            # Enabled LONG Position Check
            
            s_dsp = "9999 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d T2B:%d Crt:%d"  % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS, d_topBottom, d_currentDiff)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')

            # lowest_buy_order from TradeEvent.ini ----------------------------
            if(d_lowest_buy_order > 0):
                # LONG Position 1st Stepを超える
                # if(d_topBottom >= D_LONG1st and d_currentDiff > 0):
                if(d_topBottom >= D_LONG2nd and d_currentDiff > 0):
                    f_Long = True
            # buy_order from TradeEvent.ini -----------------------------------
            if(d_buy_order > 0):        # 即時買い指示
                f_Long = True
                s_dsp = "buy_order,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            # -----------------------------------------------------------------

            # LONG 発行のマスク
            if(D_long_position_mask > 0):
                if(f_Long):
                    f_Long = False
                    s_dsp = "long_position_mask,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    s_dsp = "--------------------"
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
            # -----------------------------------------------------------------

            if(f_Long):
                D_BidPrice = D_Current                          # LONG Price保存
                d_profit = 0
                T_BidTime = datetime.datetime.now().time()      # global変数に保存
                s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
                s_dsp = "220 + Long,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

                #----- LONG発注 -------------------------
                # except simulation
                if(ws is not None and message is not None):
                    LongOrder(ws, message, Symbol)                   # ３．注文発注（信用）新規買い
                    # S_BidResult = content["Result"]
                    # S_BidOrderId = content["OrderId"]

                    T_Now = datetime.datetime.now().time()
                    s_Time = T_Now.strftime("%H:%M:%S:%f")
                    # s_dsp = "221 + LONG %s, %s, LongOrder(), (LONG0:%d, L_1st:%d, L_2nd:%d, SMA:%d) " % (s_Time,s_BidTime, D_LONG0, D_LONG1st, D_LONG2nd, D_SMACounts)
                    s_dsp = "221 + LONG %s, %s, LongOrder(), (LONG0:%d, L_1st:%d, L_2nd:%d, L_4th:%d) " % (s_Time,s_BidTime, D_LONG0, D_LONG1st, D_LONG2nd, D_LONG4th)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    # Check for Long Position
                    # checkSt = KABUPOSI.kabu_positions.APIPosition.check_position(product='0',symbol=Symbol, side='2', Token=Token)
                    s_dsp = "222 + LONG Check_Order(%s, %s, %s, %s) " % (Symbol, S_BidOrderId, s_Updtime, Token)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    # checkSt = kabu_CheckOrders.Check_Order(Symbol=Symbol, OrderId=S_BidOrderId, UpdateTime=s_Updtime, Token=Token)
                    checkSt = kabu_CheckOrders.Check_Order(Symbol, S_BidOrderId, s_Updtime, Token)

                    s_dsp = "222 + LONG %d=Check_Order(),%s,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (checkSt, Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    
                    # checkSt = 1   for simuration
                    # if(checkSt == 0):
                    #     if(D_LONGSimulate == 0):      # !=0:for simurate
                    #         D_BidPrice = 0
                    #         d_profit = 0
                    #         s_dsp = "222 LONG NG,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    #         D_CancelSt = kabu_CancelOrder.APICancel.cancel_position(Password=Password, OrderID=S_BidOrderId, Token=Token)
                    #         s_dsp = "223 + CANCEL %s, %s, %d=cancel_position(), (LONG0:%d, L_1st:%d, L_2nd:%d,) " % (s_Time,s_BidTime, D_CancelSt, D_LONG0, D_LONG1st, D_LONG2nd)
                    #         print(s_dsp)
                    #         if(F_Write):
                    #             WriteCsvFile.write(s_dsp + '\n')
       
                    #     else:                       # for simurate
                    #         s_dsp = "222 + LONG NG->simurate,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)

                    #     print(s_dsp)
                    #     if(F_Write):
                    #         WriteCsvFile.write(s_dsp + '\n')
                    # else:
                    #     # d_BottomPrice = D_Current
                    #     s_dsp = "224 LONG OK,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    #     print(s_dsp)
                    #     if(F_Write):
                    #         WriteCsvFile.write(s_dsp + '\n')
                #----- END LONG発注 -------------------------
                # else:
                #     LongReverseLimitOrder(ws, message, Symbol)      # for DEBUG

            #----- END LONG Position 1st Stepを超える
            D_CurrentLast = D_Current
            if(d_currentDiff != 0):    # Other than no change
                s_dsp = "229,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
        #----- END Position無し ----------
        #----- Position有り ----------
        else:       #if(D_BidPrice > 0):
            #----- TopPrice -----
            # UP    (Top < message."CurrentPrice")
            # Pos有り中の高値
            if(D_TopBidPrice < D_Current):
                D_TopBidPrice = D_Current

            if(d_BottomPrice == 0):
                d_BottomPrice = D_Current
            #------------------------------------------------------------------
            d_profit = D_Current - D_BidPrice
            if(d_currentDiff > 0):
                s_dsp = "230 UP With Position,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            elif(d_currentDiff < 0):
                s_dsp = "231 Down With Position,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            #------------------------------------------------------------------
            # 損切り価格 Top-Minus
            d_LosscutPrice = D_BidPrice - D_LONGLOSS            # Loss-Cut Transactions (Entry - LossCut)
            #------------------------------------------------------------------
            d_profitMax = D_TopBidPrice - D_Current
            #------------------------------------------------------------------
            # Profit > 0 
            # if(D_LONG1st > 0 and d_profit > 0):     
            #     D_TargetPrice =  D_BidPrice + D_LONG1st         # TargetPrice = 買値+L1st

            # 3rd Target Price
            # el
            s_dsp = "9999 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d" % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            if(D_LONG3rd > 0 and D_LONG4th > 0):
                D_TargetPrice = D_BidPrice + D_LONG4th          # 4th：利幅, 3rd：Topからの下げ幅
                # d_4thPrise =    D_BidPrice + D_LONG4th 
                d_3rdLossPrise = D_TopBidPrice - D_LONG3rd         # D_BidPrice - LONG3rd で利益確定

                s_dsp = "9999 3rd4th 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d Bid:%d target:%d" % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS, D_BidPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

                # if(D_TopBidPrice > D_LONG4th and )
                # if(d_profit > 0 and D_LONG4th < d_profitMax):
                #     # d_profit3rd = int((float(d_profit) * F_LONG3rd / float(100)) + 0.5)          # D_BidPriceは>0 利益＊LONG3rd[%]で利益確定
                #     # s_dsp = "232 d_profit3rd:%d = (d_profit:%d * L_3rd:%d )" % (d_profit3rd, d_profit, F_LONG3rd)

                #     d_profit3rd = D_TopBidPrice - D_LONG3rd         # D_BidPrice - LONG3rd で利益確定
                #     s_dsp = "232 d_profit3rd:%d = (d_profit:%d * L_3rd:%d )" % (d_profit3rd, d_profit, D_LONG3rd)
                #     # s_dsp = "232 3rd[%] Target Price,,,,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,%f" % (D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, F_LONG3rd)
                #     print(s_dsp)
                #     if(F_Write):
                #         WriteCsvFile.write(s_dsp + '\n')

                #     if(d_profit3rd > d_profit):                         # illegal
                #         d_profit3rd = d_profit
                #     # D_TargetPrice =  D_BidPrice + d_profit3rd  
                #     D_TargetPrice = D_TopBidPrice - d_profit3rd
                #     d_Target =  D_BidPrice + D_LONG4th                  # D_LONG0
                #     if(D_TargetPrice <=  d_Target):                     # LON0値以下はLosscut値
                #         D_TargetPrice =  d_LosscutPrice
                    
                #     if(D_TargetPrice <=  D_BidPrice):                   # 買値以下はLosscut値
                #         D_TargetPrice =  d_LosscutPrice
                
                #     s_dsp = "233 Down With Position D_TopBidPrice:%d d_profit:%d d_profit3rd:%d D_TargetPrice:%d d_Target:%d" % (D_TopBidPrice, d_profit, d_profit3rd, D_TargetPrice, d_Target)
                #     print(s_dsp)
                #     #     s_dsp = "232 3rd[%] Target Price,,,,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,%f" % (D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, F_LONG3rd)
                #     #     print(s_dsp)
                #     if(F_Write):
                #         WriteCsvFile.write(s_dsp + '\n')
                #     s_dsp = ""
                # else:
                #     D_TargetPrice =  d_LosscutPrice

            elif(D_LONG2nd > 0):
                D_TargetPrice =  D_BidPrice + D_LONG2nd         # TargetPrice = 買値+L2nd

                s_dsp = "9999 2nd 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d Bid:%d target:%d" % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS, D_BidPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            # Loss-cut
            # elif(D_LONG2nd == 0):
            #     D_TargetPrice =  D_BidPrice - (D_LONGLOSS / 2)         #D_BidPrice では次のイベントで売られてしまう                    # L2nd==0 ? 買値までがまん
            #     if(D_TargetPrice >=  D_BidPrice):
            #         D_TargetPrice =  D_BidPrice - 1
            #         # D_TargetPrice =  d_LosscutPrice         #D_BidPrice では次のイベントで売られてしまう                    # L2nd==0 ? 買値までがまん
            # 2nd Target-Price
            # elif(D_BidPrice < D_TopBidPrice):
            #     D_TargetPrice =  D_BidPrice + D_LONG2nd         # TargetPrice = 買値+L2nd
            #     # if(D_Current > D_BidPrice):                         # +
            #     #     if(D_Current <      (D_BidPrice + D_LONG2nd)):
            #     #         D_TargetPrice =  D_BidPrice + D_LONG2nd     # TargetPrice = 買値+L2nd
            #     #     elif(D_Current < D_TopBidPrice):
            #     #         D_TargetPrice =  D_BidPrice + D_LONG2nd     # TargetPrice = 買値+L2nd
            #     #     else:
            #     #         D_TargetPrice =  d_LosscutPrice             # < 買値+L2nd の時はLosscut値           +++++++++++++++++++++++++
            #     # else:
            #     #     D_TargetPrice =  d_LosscutPrice             # < 買値+L2nd の時はLosscut値           +++++++++++++++++++++++++
            #     #     # D_TargetPrice =  D_TopBidPrice - D_LONG2nd      # > 買値+L2nd の時は Max-L2nd
            else:
                D_TargetPrice =  d_LosscutPrice                 # < 買値 の時はLosscut値

            # D_TargetPrice =  D_TopBidPrice - D_LONG2nd
            # if(D_TargetPrice <  D_BidPrice):
            #     D_TargetPrice =  d_LosscutPrice                 # < 買値 の時はLosscut値
            # elif(D_TargetPrice <  D_BidPrice + D_LONG2nd):
            #     D_TargetPrice =  D_BidPrice + D_LONG2nd         # < 買値+L2nd の時は 買値+L2nd

            f_Stop = False
            # D_profit_taking : 利益確定／LONG Close
            if(D_profit_taking > 0):
                f_Stop = True
                if(d_profit > 0):
                    s_dsp = "240 CLOSE,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
                else:
                    s_dsp = "240 CLOSE,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
            # Target-Price
            elif(D_Current >= D_BidPrice):
                if(D_LONG3rd > 0 and D_LONG4th > 0):
                    if(D_Current >= D_TargetPrice and D_Current < d_3rdLossPrise and d_3rdLossPrise > D_TargetPrice): # +4th：利幅, 3rd：Topからの下げ幅 (D_BidPrice - LONG3rd で利益確定)
                        f_Stop = True
                        s_dsp = "240 3rdLoss,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,  %d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_3rdLossPrise)
                    else:
                        s_dsp = "240 3rdLoss+,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,  %d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_3rdLossPrise)

                elif(D_LONG2nd > 0):
                    if(D_Current >= D_TargetPrice):
                        f_Stop = True
                        s_dsp = "240 TargetPrice,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    else:
                        s_dsp = "240 TargetPrice-,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)

            # Loss-cut
            elif(D_Current < D_BidPrice):
                if(D_Current <= d_LosscutPrice):
                    f_Stop = True
                    s_dsp = "240 LossCut,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                else:                        
                    s_dsp = "240 Cur < Bit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            else:
                s_dsp = "240 Cur >= Bit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
        
            # 処分売り
            if(f_Stop or D_profit_taking > 0):
                if(d_profit > 0):
                    s_dsp = "241 Profit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
                else:
                    s_dsp = "241 Profit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

                Ttrading_Stop(ws, message, Symbol)
                D_TopBidPrice = D_Current
                d_BottomPrice = D_Current
                D_BidPrice = 0
                d_profit = 0
                D_TargetPrice = 0
                d_LosscutPrice = 0
                s_dsp = "242 LossCut,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
                
            # 利益確定 売り
            # elif(D_Current <= D_TargetPrice):
            #     s_dsp = "250 Profit+,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            #     print(s_dsp)
            #     if(F_Write):
            #         WriteCsvFile.write(s_dsp + '\n')

            #     D_TopBidPrice = D_Current
            #     d_BottomPrice = D_Current
            #     D_BidPrice = 0
            #     d_profit = 0
            #     D_TargetPrice = 0
            #     d_LosscutPrice = 0
            #     # return -1
            #     Ttrading_Stop(ws, message, Symbol)

            #     s_dsp = "251 Profit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            #     print(s_dsp)
            #     if(F_Write):
            #         WriteCsvFile.write(s_dsp + '\n')

            else:   #Illigal Check
                if(d_BottomPrice == 0):
                    s_dsp = "260 Bottom:0,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    d_BottomPrice = D_Current

                if(D_TopBidPrice == 0):
                    s_dsp = "261 Top:0,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    D_TopBidPrice = D_Current
                # s_dsp = "263Partial,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                # print(s_dsp)
                # if(F_Write):
                #     WriteCsvFile.write(s_dsp + '\n')

        #----- END Position有り ----------
        f_Short = False
        if(d_short_selling > 0):
            f_Short = True
        # short covering
        # if(d_short_selling > 0):
        if(f_Short):
            s_dsp = "short_selling,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            ShortSelling(ws, message, Symbol)

        # s_dsp = "290,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        # print(s_dsp)
        # if(F_Write):
        #     WriteCsvFile.write(s_dsp + '\n')
        D_CurrentLast = D_Current
        # Update Top Price
        if(D_TopBidPrice < D_Current):
            D_TopBidPrice = D_Current
        if(D_TopBidPrice == 0):
            D_TopBidPrice = D_Current
        # 直近最高値
        if(d_TopLast == 0 or d_TopLast < D_TopBidPrice):
            d_TopLast = D_TopBidPrice
        #----------------------------------------------------------------------
        #     # キャンセルからの LossCut注文
        #     cancelorder.cancelorder()
        #     ws.close()
        if(d_currentDiff != 0):    # Other than no change
            s_dsp = "291,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write and d_currentDiff):
                WriteCsvFile.write(s_dsp + '\n')

        D_CurrentLast = D_Current
        # # Update Top Price
        # if(D_TopBidPrice < D_Current):
        #     D_TopBidPrice = D_Current
        # if(D_TopBidPrice == 0):
        #     D_TopBidPrice = D_Current
        # if(d_TopLast == 0):
        #     d_TopLast = D_TopBidPrice
        #----------------------------------------------------------------------
                #     # キャンセルからの LossCut注文
                #     cancelorder.cancelorder()
                #     ws.close()
        # s_dsp = "Symbol:%s<-%d, Crt:%d, Bid[%6d], profit<%d>, LastTop:%d, Top:%d, Btm:%d) " % (Symbol, D_CurrentLast, D_Current, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice, d_BottomPrice)
        # print(s_dsp)
        s_dsp = "129,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time,D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        print(s_dsp)
        if(F_Write and d_currentDiff):
            WriteCsvFile.write(s_dsp + '\n')
#--- def Long_Symbol1(ws, message, Symbol, WriteCsvFile)-------------------------------------------------------
    



#----------------------------------------------------------
# on_message Module --------------------------------------- 株価が変わった場合に呼ばれる関数
#   Read INI file -----------------------------------------
#   Check price & decide trade mode ----------------------- Exe to INI & Choice mode / Auto mode
#
#   if Buy from INI file ----------------------------------
#       set Entry flag ------------------------------------
#   elif Selling from INI file ----------------------------
#       set Sell flag -------------------------------------
#   elif ReverseLimitOrder -------------------------------- 逆指値条件の監視
#       ----------------------------------------------------------
#
#   elif Shift1 mode --------------------------------------
#       Call shift1 class (set flag of Entry or Sell) ----- .\PythonCS\Auto_Scalping1.py
#   elif Shift2 mode --------------------------------------
#       Call shift2 class (set flag of Entry or Sell) -----
#   elif Shift3 mode --------------------------------------
#       Call shift3 class (set flag of Entry or Sell) -----
#   elif Shift4 mode --------------------------------------
#       Call shift4 class (set flag of Entry or Sell) -----
#
#   if sell flag is True ----------------------------------
#       Selling -------------------------------------------
#
#   elif entry flag is True -------------------------------
#       Entry ---------------------------------------------
#
#   elif ReverseLimitOrder -------------------------------- 逆指値条件の監視
#       Check price and write INI faile -------------------
#----------------------------------------------------------

#----- 株価イベントでコールされる関数 ----------------------
def AutomaticShift(ws, message, Symbol, WriteCsvFile):

    global Password         # Use cancel
    global S_BidOrderId
    global D_CancelSt

    global Token
    global LONG0
    global LONG1st
    global LONG2nd
    global LONG3rd
    global LONG4th

    global LONGLOSS
    global D_LONGLOSS

    global D_LogLevel1
    global D_LogLevel2
    global D_LogLevel3
    global D_LogLevel4
    global D_LogLevel5
    # global SMACounts
    # global D_SMACounts

    global S_long_simulate
    global D_long_simulate
    global S_short_simulate
    global D_short_simulate

    global S_long_position_mask
    global D_long_position_mask
    global S_short_position_mask
    global D_short_position_mask

    global S_profit_taking
    global D_profit_taking
    global S_short_covering
    global D_short_covering

    global PauseTime

    global S_CurrentTime 
    global PauseTime

    global D_Current
    global PauseTime

    global d_TopLast
    global D_TopBidPrice
    global d_BottomPrice
    global d_LosscutPrice
    global D_TargetPrice
    global D_CurrentLast
    global D_BidPrice
    global T_Now
    global T_BidTime
    #------------------------------------------------------
    # global S_CurrentTime
    global F_Write
    # global WriteCsvFile

    #------------------------------------------------------
    # Get Long Position Setting
    conf = configparser.ConfigParser()
    conf.read('./TradeSymbol.ini')
    # conf.read('./settings.ini')
    # Callback message
    LogLevel1 = conf['kabuAPI']['LogLevel1']
    LogLevel2 = conf['kabuAPI']['LogLevel2']
    LogLevel3 = conf['kabuAPI']['LogLevel3']
    LogLevel4 = conf['kabuAPI']['LogLevel4']
    LogLevel5 = conf['kabuAPI']['LogLevel5']
    D_LogLevel1 = int(LogLevel1)
    D_LogLevel2 = int(LogLevel2)
    D_LogLevel3 = int(LogLevel3)
    D_LogLevel4 = int(LogLevel4)
    D_LogLevel5 = int(LogLevel5)

    Issue1 = conf['kabuAPI']['Issue1']
    Issue2 = conf['kabuAPI']['Issue2']
    Issue3 = conf['kabuAPI']['Issue3']
    # LONGSimulate = conf['kabuAPI']['LONGSimulate']
    PauseTime = conf['kabuAPI']['PauseTime']

    LONG0 = conf['kabuAPI']['LONG0']
    LONG1st = conf['kabuAPI']['LONG1st']
    LONG2nd = conf['kabuAPI']['LONG2nd']
    LONG3rd = conf['kabuAPI']['LONG3rd']
    LONG4th = conf['kabuAPI']['LONG4th']
    LONGLOSS = conf['kabuAPI']['LONGLOSS']
    D_LONG0 = int(LONG0)
    D_LONG1st = int(LONG1st)
    D_LONG2nd = int(LONG2nd)
    # F_LONG3rd = float(LONG3rd)
    D_LONG3rd = int(LONG3rd)
    D_LONG4th = float(LONG4th)

    D_LONGLOSS = int(LONGLOSS)
    #-------------------------------------------------------
    #　Event driven ----------------------------------------
    try:
        
        config = configparser.ConfigParser()            # ConfigParserクラスをインスタンス化
        config.read('.\TradeEvent.ini')
        S_long_simulate         = config['OrderEvent']['long_simulate']
        S_long_position_mask    = config['OrderEvent']['long_position_mask']
        D_long_simulate         = int(S_long_simulate)

        d_long_position_mask_last = D_long_position_mask
        D_long_position_mask    = int(S_long_position_mask)

        S_short_simulate        = config['OrderEvent']['short_simulate']
        S_short_position_mask   = config['OrderEvent']['short_position_mask']
        D_short_simulate        = int(S_short_simulate)
        D_short_position_mask   = int(S_short_position_mask)

        # buy_order         # 買い
        buy_order               = config['OrderEvent']['buy_order']
        d_buy_order             = int(buy_order)
        # lowest_buy_order  # 底値確認後の買い
        lowest_buy_order        = config['OrderEvent']['lowest_buy_order']
        d_lowest_buy_order      = int(lowest_buy_order)

        # highest_short_selling     # 高値確認後の空売り
        highest_short_selling   = config['OrderEvent']['highest_short_selling']
        d_highest_short_selling = int(highest_short_selling)
        # short_selling     # 空売り
        short_selling           = config['OrderEvent']['short_selling']         # short_selling : 即時売り
        d_short_selling         = int(short_selling)
        # profit_taking     # 利食い (利益確定売り)
        S_profit_taking         = config['OrderEvent']['profit_taking']
        D_profit_taking         = int(S_profit_taking) 
        # short_covering    # 空売りの買戻し
        S_short_covering        = config['OrderEvent']['short_covering']
        D_short_covering        = int(S_short_covering)

        change_ini_file         = config['kabuAPI']['change_ini_file']
        reset_bottom            = config['kabuAPI']['reset_bottom']

        # 空売りの買戻し short covering
        # Event値は'0'に戻す
        # if(buy_order != '0' or lowest_buy_order != '0' or highest_short_selling != '0' or short_selling != '0' or change_ini_file != '0'):
        if(buy_order != '0' or short_selling != '0' or change_ini_file != '0' or reset_bottom != '0'):
            s_dsp = "100 Event driven   buy:%d  L_buy:%d  H_short:%d  short:%d change_ini_file:%s" % (d_buy_order, d_lowest_buy_order, d_highest_short_selling, d_short_selling, change_ini_file)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            config['OrderEvent']['buy_order'] = '0'
            config['OrderEvent']['short_selling'] = '0'
            config['kabuAPI']['change_ini_file'] = '0'
            config['kabuAPI']['reset_bottom'] = '0'
            # config['OrderEvent']['long_simulate'] = '0' 保持
            # config['OrderEvent']['long_position_mask'] = '0' 保持
            # config['OrderEvent']['lowest_buy_order'] = '0' 保持
            # config['OrderEvent']['short_simulate'] = '0' 保持
            # config['OrderEvent']['highest_short_selling'] = '0' 保持        
            # INIファイルの生成・書き込み # 書き込みモードでオープン
            with open('.\TradeEvent.ini', 'w') as configfile:
                print('INIファイルの書き込み')                      #print()->'無しで出力
                # 指定したconfigファイルを書き込み
                # conf.optionxform = setstr
                config.write(configfile)        # 指定したconfigファイルを書き込み
            print('TradeEvent.INIファイルの書き込み')                      #print()->'無しで出力

    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        pprint.pprint(content)
    except Exception as e:
        print(e)
    #　Event driven ----------------------------------------
    #-------------------------------------------------------
    # except simulation
    if(ws is not None and message is not None):
        T_Now = datetime.datetime.now().time()
        s_Time = T_Now.strftime("%H:%M:%S:%f")
        S_CurrentTime = T_Now.strftime("%H:%M:%S:%f")
        s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
        now = datetime.datetime.now()
        # %d	10進数で月の始めから何日目かを表示。
        # %y	10進数で上2桁のない西暦年を表示。
        # %Y	10進数で上2桁が付いている西暦年を表示。
        # %m	10進数で月を表示。
        # &S	10進数で秒を表示。
        # %H	10進数で24時間計での時を表示。
        # %I	10進数で12時間計での時を表示。
        # %m	10進数で月を表示。
        # %M	10進数で分を表示。
        # s_Updtime = now.strftime("%Y%m%d")      # yyyyMMddHHmmss
        # print(s_Updtime)
        # s_Updtime = now.strftime("%I%M%S")
        # print(s_Updtime)
        s_Updtime = now.strftime("%Y%m%d%I%M%S")      # yyyyMMddHHmmss
        # print('=================' , s_Updtime)

        # s_Updtime = T_Now.strftime("%y/%M/%d%H%m%s")      # yyyyMMddHHmmss
        # print(s_Updtime)
        # s_Updtime.replace('/', '')
        # # s_Updtime = now.strftime("%y%M%d %H%m%s")      # yyyyMMddHHmmss
        # print(s_Updtime)
    # For simulation
    else:
        s_Time = SimulateTime
        S_CurrentTime = SimulateTime
        s_BidTime = SimulateTime
    #------------------------------------------------------
    # 利幅
    d_profit = 0
    if(D_BidPrice > 0):
        d_profit = D_Current - D_BidPrice
    # d_currentDiff <0:下げ相場 / >0:上げ相場
    d_currentDiff = 0
    if(D_CurrentLast != D_Current):
        d_currentDiff = D_Current - D_CurrentLast
    #------------------------------------------------------
    #======================================================
    # INIファイル切り替え =========================================
    if (change_ini_file != '0'):
        time = T_Now.strftime("%H%M%S")
        s_dsp = "110一時停止,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        print(s_dsp)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')

        s_DateTime = T_Now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
        WritefileName = './Result' + s_DateTime + '.csv'
        F_Write = False;
        WriteCsvFile = open(WritefileName, 'w')     #, newline='')
        if (WriteCsvFile):
            F_Write = True;
    # INIファイル切り替え =========================================

    # 銘柄１
    if(Symbol == Issue1 and Symbol is not None):
        if(reset_bottom != '0'):
            d_BottomPrice = D_Current
        #-------------------------------------------------------
        if(D_long_position_mask > 0 and d_long_position_mask_last == 0):
            s_dsp = "long_position_mask:%d (%s)" % (D_long_position_mask, d_long_position_mask_last)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            s_dsp = "--------------------"
            # Reset Diff
            D_TopBidPrice = D_Current
            # d_BottomPrice = D_Current
            d_TopLast = D_Current

        s_Time = S_CurrentTime
        #----------------------------------------------------------
        s_dsp = "200,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        if(D_LogLevel2 > 0):
            print(s_dsp)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')            
        #----- Position無し ----------
        d_profit = D_Current - d_BottomPrice
        if(D_BidPrice == 0):
            s_dsp = "211 No Position,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')

            #下げ相場　Bottom == Top
            if(D_CurrentLast > D_Current):
                D_TopBidPrice = D_Current
                if(d_BottomPrice > D_Current):
                    d_BottomPrice = D_Current
                # D_CurrentLast = D_Current
            #上げ相場　Keep Bottom AND Update Top
            else:
                # Position無し Top上げ
                if (D_TopBidPrice < D_Current):
                    D_TopBidPrice = D_Current
                    s_dsp = "212 Up Top,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                # "W"
                elif(D_TopBidPrice > D_Current):
                    s_dsp = "213 Top > Cur,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')

            d_topBottom = 0
            if(d_BottomPrice > 0):
                d_topBottom = D_TopBidPrice - d_BottomPrice
            else:
                d_BottomPrice = D_Current

            if(d_topBottom != 0):
                s_dsp = "DIFF:%d,%s,,---,%d,(Top:%d - Bottom:%d), L_0:%d, L_1st:%d, L_2nd:%d, L_Loss:%d, L_3rd:%d, L_4th:%d" % (d_topBottom, Symbol, D_Current, D_TopBidPrice , d_BottomPrice,D_LONG0, D_LONG1st, D_LONG2nd, D_LONGLOSS, D_LONG3rd, D_LONG4th)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

            if(d_currentDiff > 0):
                s_dsp = "214 UP,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            elif(d_currentDiff < 0):
                s_dsp = "215 Down,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            # else:
                # s_dsp = "216 Partial,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                # print(s_dsp)
                # if(F_Write):
                #     WriteCsvFile.write(s_dsp + '\n')
            # LONG
            # Profit taking or loss-cut
            # -----------------------------------------------------------------
            f_Long = False
            # Enabled LONG Position Check
            
            s_dsp = "9999 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d T2B:%d Crt:%d"  % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS, d_topBottom, d_currentDiff)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')

            # lowest_buy_order from TradeEvent.ini ----------------------------
            if(d_lowest_buy_order > 0):
                # LONG Position 1st Stepを超える
                # if(d_topBottom >= D_LONG1st and d_currentDiff > 0):
                if(d_topBottom >= D_LONG2nd and d_currentDiff > 0):
                    f_Long = True
            # buy_order from TradeEvent.ini -----------------------------------
            if(d_buy_order > 0):        # 即時買い指示
                f_Long = True
                s_dsp = "buy_order,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            # -----------------------------------------------------------------

            # LONG 発行のマスク
            if(D_long_position_mask > 0):
                if(f_Long):
                    f_Long = False
                    s_dsp = "long_position_mask,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    s_dsp = "--------------------"
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
            # -----------------------------------------------------------------

            if(f_Long):
                D_BidPrice = D_Current                          # LONG Price保存
                d_profit = 0
                T_BidTime = datetime.datetime.now().time()      # global変数に保存
                s_BidTime = T_BidTime.strftime("%H:%M:%S:%f")
                s_dsp = "220 + Long,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

                #----- LONG発注 -------------------------
                # except simulation
                if(ws is not None and message is not None):
                    LongOrder(ws, message, Symbol)                   # ３．注文発注（信用）新規買い
                    # S_BidResult = content["Result"]
                    # S_BidOrderId = content["OrderId"]

                    T_Now = datetime.datetime.now().time()
                    s_Time = T_Now.strftime("%H:%M:%S:%f")
                    # s_dsp = "221 + LONG %s, %s, LongOrder(), (LONG0:%d, L_1st:%d, L_2nd:%d, SMA:%d) " % (s_Time,s_BidTime, D_LONG0, D_LONG1st, D_LONG2nd, D_SMACounts)
                    s_dsp = "221 + LONG %s, %s, LongOrder(), (LONG0:%d, L_1st:%d, L_2nd:%d, L_4th:%d) " % (s_Time,s_BidTime, D_LONG0, D_LONG1st, D_LONG2nd, D_LONG4th)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    # Check for Long Position
                    # checkSt = KABUPOSI.kabu_positions.APIPosition.check_position(product='0',symbol=Symbol, side='2', Token=Token)
                    s_dsp = "222 + LONG Check_Order(%s, %s, %s, %s) " % (Symbol, S_BidOrderId, s_Updtime, Token)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    # checkSt = kabu_CheckOrders.Check_Order(Symbol=Symbol, OrderId=S_BidOrderId, UpdateTime=s_Updtime, Token=Token)
                    checkSt = kabu_CheckOrders.Check_Order(Symbol, S_BidOrderId, s_Updtime, Token)

                    s_dsp = "222 + LONG %d=Check_Order(),%s,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (checkSt, Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    
                    # checkSt = 1   for simuration
                    # if(checkSt == 0):
                    #     if(D_LONGSimulate == 0):      # !=0:for simurate
                    #         D_BidPrice = 0
                    #         d_profit = 0
                    #         s_dsp = "222 LONG NG,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    #         D_CancelSt = kabu_CancelOrder.APICancel.cancel_position(Password=Password, OrderID=S_BidOrderId, Token=Token)
                    #         s_dsp = "223 + CANCEL %s, %s, %d=cancel_position(), (LONG0:%d, L_1st:%d, L_2nd:%d,) " % (s_Time,s_BidTime, D_CancelSt, D_LONG0, D_LONG1st, D_LONG2nd)
                    #         print(s_dsp)
                    #         if(F_Write):
                    #             WriteCsvFile.write(s_dsp + '\n')
       
                    #     else:                       # for simurate
                    #         s_dsp = "222 + LONG NG->simurate,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)

                    #     print(s_dsp)
                    #     if(F_Write):
                    #         WriteCsvFile.write(s_dsp + '\n')
                    # else:
                    #     # d_BottomPrice = D_Current
                    #     s_dsp = "224 LONG OK,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    #     print(s_dsp)
                    #     if(F_Write):
                    #         WriteCsvFile.write(s_dsp + '\n')
                #----- END LONG発注 -------------------------
                # else:
                #     LongReverseLimitOrder(ws, message, Symbol)      # for DEBUG

            #----- END LONG Position 1st Stepを超える
            D_CurrentLast = D_Current
            if(d_currentDiff != 0):    # Other than no change
                s_dsp = "229,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
        #----- END Position無し ----------
        #----- Position有り ----------
        else:       #if(D_BidPrice > 0):
            #----- TopPrice -----
            # UP    (Top < message."CurrentPrice")
            # Pos有り中の高値
            if(D_TopBidPrice < D_Current):
                D_TopBidPrice = D_Current

            if(d_BottomPrice == 0):
                d_BottomPrice = D_Current
            #------------------------------------------------------------------
            d_profit = D_Current - D_BidPrice
            if(d_currentDiff > 0):
                s_dsp = "230 UP With Position,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            elif(d_currentDiff < 0):
                s_dsp = "231 Down With Position,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            #------------------------------------------------------------------
            # 損切り価格 Top-Minus
            d_LosscutPrice = D_BidPrice - D_LONGLOSS            # Loss-Cut Transactions (Entry - LossCut)
            #------------------------------------------------------------------
            d_profitMax = D_TopBidPrice - D_Current
            #------------------------------------------------------------------
            # Profit > 0 
            # if(D_LONG1st > 0 and d_profit > 0):     
            #     D_TargetPrice =  D_BidPrice + D_LONG1st         # TargetPrice = 買値+L1st

            # 3rd Target Price
            # el
            s_dsp = "9999 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d" % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            if(D_LONG3rd > 0 and D_LONG4th > 0):
                D_TargetPrice = D_BidPrice + D_LONG4th          # 4th：利幅, 3rd：Topからの下げ幅
                # d_4thPrise =    D_BidPrice + D_LONG4th 
                d_3rdLossPrise = D_TopBidPrice - D_LONG3rd         # D_BidPrice - LONG3rd で利益確定

                s_dsp = "9999 3rd4th 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d Bid:%d target:%d" % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS, D_BidPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

                # if(D_TopBidPrice > D_LONG4th and )
                # if(d_profit > 0 and D_LONG4th < d_profitMax):
                #     # d_profit3rd = int((float(d_profit) * F_LONG3rd / float(100)) + 0.5)          # D_BidPriceは>0 利益＊LONG3rd[%]で利益確定
                #     # s_dsp = "232 d_profit3rd:%d = (d_profit:%d * L_3rd:%d )" % (d_profit3rd, d_profit, F_LONG3rd)

                #     d_profit3rd = D_TopBidPrice - D_LONG3rd         # D_BidPrice - LONG3rd で利益確定
                #     s_dsp = "232 d_profit3rd:%d = (d_profit:%d * L_3rd:%d )" % (d_profit3rd, d_profit, D_LONG3rd)
                #     # s_dsp = "232 3rd[%] Target Price,,,,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,%f" % (D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, F_LONG3rd)
                #     print(s_dsp)
                #     if(F_Write):
                #         WriteCsvFile.write(s_dsp + '\n')

                #     if(d_profit3rd > d_profit):                         # illegal
                #         d_profit3rd = d_profit
                #     # D_TargetPrice =  D_BidPrice + d_profit3rd  
                #     D_TargetPrice = D_TopBidPrice - d_profit3rd
                #     d_Target =  D_BidPrice + D_LONG4th                  # D_LONG0
                #     if(D_TargetPrice <=  d_Target):                     # LON0値以下はLosscut値
                #         D_TargetPrice =  d_LosscutPrice
                    
                #     if(D_TargetPrice <=  D_BidPrice):                   # 買値以下はLosscut値
                #         D_TargetPrice =  d_LosscutPrice
                
                #     s_dsp = "233 Down With Position D_TopBidPrice:%d d_profit:%d d_profit3rd:%d D_TargetPrice:%d d_Target:%d" % (D_TopBidPrice, d_profit, d_profit3rd, D_TargetPrice, d_Target)
                #     print(s_dsp)
                #     #     s_dsp = "232 3rd[%] Target Price,,,,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,%f" % (D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, F_LONG3rd)
                #     #     print(s_dsp)
                #     if(F_Write):
                #         WriteCsvFile.write(s_dsp + '\n')
                #     s_dsp = ""
                # else:
                #     D_TargetPrice =  d_LosscutPrice

            elif(D_LONG2nd > 0):
                D_TargetPrice =  D_BidPrice + D_LONG2nd         # TargetPrice = 買値+L2nd

                s_dsp = "9999 2nd 1st:%d 2nd:%d 3rd:%d 4th:%d Loss:%d Bid:%d target:%d" % (D_LONG1st, D_LONG2nd, D_LONG3rd, D_LONG4th, D_LONGLOSS, D_BidPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
            # Loss-cut
            # elif(D_LONG2nd == 0):
            #     D_TargetPrice =  D_BidPrice - (D_LONGLOSS / 2)         #D_BidPrice では次のイベントで売られてしまう                    # L2nd==0 ? 買値までがまん
            #     if(D_TargetPrice >=  D_BidPrice):
            #         D_TargetPrice =  D_BidPrice - 1
            #         # D_TargetPrice =  d_LosscutPrice         #D_BidPrice では次のイベントで売られてしまう                    # L2nd==0 ? 買値までがまん
            # 2nd Target-Price
            # elif(D_BidPrice < D_TopBidPrice):
            #     D_TargetPrice =  D_BidPrice + D_LONG2nd         # TargetPrice = 買値+L2nd
            #     # if(D_Current > D_BidPrice):                         # +
            #     #     if(D_Current <      (D_BidPrice + D_LONG2nd)):
            #     #         D_TargetPrice =  D_BidPrice + D_LONG2nd     # TargetPrice = 買値+L2nd
            #     #     elif(D_Current < D_TopBidPrice):
            #     #         D_TargetPrice =  D_BidPrice + D_LONG2nd     # TargetPrice = 買値+L2nd
            #     #     else:
            #     #         D_TargetPrice =  d_LosscutPrice             # < 買値+L2nd の時はLosscut値           +++++++++++++++++++++++++
            #     # else:
            #     #     D_TargetPrice =  d_LosscutPrice             # < 買値+L2nd の時はLosscut値           +++++++++++++++++++++++++
            #     #     # D_TargetPrice =  D_TopBidPrice - D_LONG2nd      # > 買値+L2nd の時は Max-L2nd
            else:
                D_TargetPrice =  d_LosscutPrice                 # < 買値 の時はLosscut値

            # D_TargetPrice =  D_TopBidPrice - D_LONG2nd
            # if(D_TargetPrice <  D_BidPrice):
            #     D_TargetPrice =  d_LosscutPrice                 # < 買値 の時はLosscut値
            # elif(D_TargetPrice <  D_BidPrice + D_LONG2nd):
            #     D_TargetPrice =  D_BidPrice + D_LONG2nd         # < 買値+L2nd の時は 買値+L2nd

            f_Stop = False
            # D_profit_taking : 利益確定／LONG Close
            if(D_profit_taking > 0):
                f_Stop = True
                if(d_profit > 0):
                    s_dsp = "240 CLOSE,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
                else:
                    s_dsp = "240 CLOSE,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
            # Target-Price
            elif(D_Current >= D_BidPrice):
                if(D_LONG3rd > 0 and D_LONG4th > 0):
                    if(D_Current >= D_TargetPrice and D_Current < d_3rdLossPrise and d_3rdLossPrise > D_TargetPrice): # +4th：利幅, 3rd：Topからの下げ幅 (D_BidPrice - LONG3rd で利益確定)
                        f_Stop = True
                        s_dsp = "240 3rdLoss,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,  %d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_3rdLossPrise)
                    else:
                        s_dsp = "240 3rdLoss+,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,  %d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_3rdLossPrise)

                elif(D_LONG2nd > 0):
                    if(D_Current >= D_TargetPrice):
                        f_Stop = True
                        s_dsp = "240 TargetPrice,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    else:
                        s_dsp = "240 TargetPrice-,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)

            # Loss-cut
            elif(D_Current < D_BidPrice):
                if(D_Current <= d_LosscutPrice):
                    f_Stop = True
                    s_dsp = "240 LossCut,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                else:                        
                    s_dsp = "240 Cur < Bit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            else:
                s_dsp = "240 Cur >= Bit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
        
            # 処分売り
            if(f_Stop or D_profit_taking > 0):
                if(d_profit > 0):
                    s_dsp = "241 Profit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
                else:
                    s_dsp = "241 Profit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d,,,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice, d_profit)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')

                Ttrading_Stop(ws, message, Symbol)
                D_TopBidPrice = D_Current
                d_BottomPrice = D_Current
                D_BidPrice = 0
                d_profit = 0
                D_TargetPrice = 0
                d_LosscutPrice = 0
                s_dsp = "242 LossCut,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                print(s_dsp)
                if(F_Write):
                    WriteCsvFile.write(s_dsp + '\n')
                
            # 利益確定 売り
            # elif(D_Current <= D_TargetPrice):
            #     s_dsp = "250 Profit+,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            #     print(s_dsp)
            #     if(F_Write):
            #         WriteCsvFile.write(s_dsp + '\n')

            #     D_TopBidPrice = D_Current
            #     d_BottomPrice = D_Current
            #     D_BidPrice = 0
            #     d_profit = 0
            #     D_TargetPrice = 0
            #     d_LosscutPrice = 0
            #     # return -1
            #     Ttrading_Stop(ws, message, Symbol)

            #     s_dsp = "251 Profit,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            #     print(s_dsp)
            #     if(F_Write):
            #         WriteCsvFile.write(s_dsp + '\n')

            else:   #Illigal Check
                if(d_BottomPrice == 0):
                    s_dsp = "260 Bottom:0,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    d_BottomPrice = D_Current

                if(D_TopBidPrice == 0):
                    s_dsp = "261 Top:0,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                    print(s_dsp)
                    if(F_Write):
                        WriteCsvFile.write(s_dsp + '\n')
                    D_TopBidPrice = D_Current
                # s_dsp = "263Partial,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
                # print(s_dsp)
                # if(F_Write):
                #     WriteCsvFile.write(s_dsp + '\n')

        #----- END Position有り ----------
        f_Short = False
        if(d_short_selling > 0):
            f_Short = True
        # short covering
        # if(d_short_selling > 0):
        if(f_Short):
            s_dsp = "short_selling,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')
            ShortSelling(ws, message, Symbol)

        # s_dsp = "290,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        # print(s_dsp)
        # if(F_Write):
        #     WriteCsvFile.write(s_dsp + '\n')
        D_CurrentLast = D_Current
        # Update Top Price
        if(D_TopBidPrice < D_Current):
            D_TopBidPrice = D_Current
        if(D_TopBidPrice == 0):
            D_TopBidPrice = D_Current
        # 直近最高値
        if(d_TopLast == 0 or d_TopLast < D_TopBidPrice):
            d_TopLast = D_TopBidPrice
        #----------------------------------------------------------------------
        #     # キャンセルからの LossCut注文
        #     cancelorder.cancelorder()
        #     ws.close()
        if(d_currentDiff != 0):    # Other than no change
            s_dsp = "291,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time, D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
            print(s_dsp)
            if(F_Write and d_currentDiff):
                WriteCsvFile.write(s_dsp + '\n')

        D_CurrentLast = D_Current
        # # Update Top Price
        # if(D_TopBidPrice < D_Current):
        #     D_TopBidPrice = D_Current
        # if(D_TopBidPrice == 0):
        #     D_TopBidPrice = D_Current
        # if(d_TopLast == 0):
        #     d_TopLast = D_TopBidPrice
        #----------------------------------------------------------------------
                #     # キャンセルからの LossCut注文
                #     cancelorder.cancelorder()
                #     ws.close()
        # s_dsp = "Symbol:%s<-%d, Crt:%d, Bid[%6d], profit<%d>, LastTop:%d, Top:%d, Btm:%d) " % (Symbol, D_CurrentLast, D_Current, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice, d_BottomPrice)
        # print(s_dsp)
        s_dsp = "129,%s,,%s,%d,%d,   %d,%d,   %d,%d,%d,   %d,%d" % (Symbol, s_Time,D_Current, d_currentDiff, D_BidPrice, d_profit, d_TopLast, D_TopBidPrice,  d_BottomPrice, d_LosscutPrice, D_TargetPrice)
        print(s_dsp)
        if(F_Write and d_currentDiff):
            WriteCsvFile.write(s_dsp + '\n')
#--- def AutomaticShift(ws, message, Symbol, WriteCsvFile)-------------------------------------------------------
    


#----- 株価が変わった場合に呼ばれる関数 ----------------------
def on_message(ws, message):
    global D_Current

    content = json.loads(message)
    Symbol = content["Symbol"]                  # 銘柄
    CurrentPrice = content["CurrentPrice"]      # 現値
    D_Current = 0
    if(CurrentPrice is not None):
        D_Current = int(CurrentPrice)

    s_dsp = "on_message,%s,,,%s," % (Symbol, CurrentPrice)
    print(s_dsp)
    if(F_Write):
        WriteCsvFile.write(s_dsp + '\n')

    # Long_Symbol1(ws, message, Symbol, WriteCsvFile)
    AutomaticShift(ws, message, Symbol, WriteCsvFile)
    # s_dsp = "<-on_message(),CurrentPrice:%s,Symbol:%s" % (CurrentPrice,Symbol)
    # print(s_dsp)


#----- エラー発生 -----------------------------------------
def on_error(ws, error):
    print('--- ERROR --- ')
    print(error)


#----- Close ----------------------------------------------
def on_close(ws):
    print('--- DISCONNECTED --- ')


#----------------------------------------------------------
#----- コールバックされる関数 -----
def on_open(ws):
    print('--- CONNECTED コールバック関数設定 --- ')

    def run(*args):
        while(True):
            line = sys.stdin.readline()
            if(line != ''):
                print('closing...')
                ws.close()
    _thread.start_new_thread(run, ())


#----------------------------------------------------------
if __name__ == '__main__':
    url = 'ws://localhost:18080/kabusapi/websocket'
    # websocketを定義する，ここでheaderにauthorizationを登録することでaccess tokenを使ったwebsocketを設定する
    # websocket.enableTrace(True)
    websocket.enableTrace(False)
    #----- WebSocketApp(コールバック,エラー,Close) -----
    ws = websocket.WebSocketApp(url,
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()                                    #WebSoketが開始


