import sys
import websocket
import _thread
import urllib.request       #kabusapi_sendorder_margin_pay_ClosePositionOrder
import json
import pprint
import datetime
#----------------------------------------------------------
import KABUPOSI
#----------------------------------------------------------
import configparser

conf = configparser.ConfigParser()
conf.read('./settings.ini')
APIPassword = conf['kabuAPI']['APIPassword']
Password = conf['kabuAPI']['Password']
Token = conf['kabuAPI']['Token']
Issue = conf['kabuAPI']['Issue']

LONGEVENT = conf['kabuAPI']['LONGEVENT']
LONG0 = conf['kabuAPI']['LONG0']
LONG1st = conf['kabuAPI']['LONG1st']
LONG2nd = conf['kabuAPI']['LONG2nd']
LONG3rd = conf['kabuAPI']['LONG3rd']
LONGLOSS = conf['kabuAPI']['LONGLOSS']
LONGCLOSE = conf['kabuAPI']['LONGCLOSE']
#------------------------------------------------------------------------------
#							＊
#							＊								    LONGCLOSE = 1   (利益確定・強制終了)
#						＊		＊	LONG2nd				LONG2nd	:4		LONGEVENT & 4
#						＊		＊
#					＊				＊	LONG3rd			LONG3rd	:8		LONGEVENT & 8
#					＊				＊
#				＊	LONG1st				＊				LONG1st	:2		LONGEVENT & 2
#				＊						＊
#	＊		＊	LONG0						＊			LONG0	:1		LONGEVENT & 1　(LONGは常に有効)
#	＊		＊								＊
#		＊	0	Buttom							＊
#												＊	LONGLOSS			Loss-cut(常に有効)
#------------------------------------------------------------------------------
#----------------------------------------------------------
d_LONGEVENT = int(LONGEVENT)
d_LONG0 = int(LONG0)
d_LONG1st = int(LONG1st)
d_LONG2nd = int(LONG2nd)
d_LONG3rd = int(LONG3rd)
d_LONGLOSS = int(LONGLOSS)
d_LONGCLOSE = int(LONGCLOSE)

d_TopLast = int(0)
d_TopPrice = int(0)
d_BottomPrice = int(0)
d_LosscutPrice = int(0)
d_TargetPrice = int(0)
d_LastValue = int(0)
d_BidPrice = int(0)
t_now = datetime.datetime.now().time()
t_BidTime = datetime.datetime.now().time()      #t_now                       #Purchase time
t_SellTime = t_now
#----------------------------------------------------------
# ３．注文発注（信用）
# （２）返済（決済順序）
# コマンド：python kabusapi_sendorder_margin_pay_ClosePositionOrder.pyより
def TtradingStop(ws, message):
    global Password
    global Token
    global Issue 
    global d_TopLast
    global d_TopPrice
    global d_BottomPrice
    global d_LosscutPrice
    global d_TargetPrice
    global d_LastValue
    global d_BidPrice

    global d_LONGEVENT
    global d_LONG0
    global d_LONG1st
    global d_LONG2nd
    global d_LONG3rd
    global d_LONGLOSS
    global d_LONGCLOSE

    global t_now
    global t_BidTime
    global t_SellTime
    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_time = t_now.strftime("%H:%M:%S:%f")
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")
    s_SellTime = t_SellTime.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(100),----- TtradingStop -----" % (s_time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------

    # 成行で終了
    obj = { 'Password': Password,
        'Symbol': Issue,            #銘柄
        'Exchange': 1,              #市場コード 1:東証
        'SecurityType': 1,          #商品種別   1:株式
        'Side': '1',                #売買区分   1:売, 2:買
        'CashMargin': 3,            #信用区分   1:現物, 2:新規, 3:返済
        'MarginTradeType': 3,       #信用取引区分   1:制度信用, 2:一般信用（長期）, 3:一般信用（デイトレ）
        'DelivType': 0,     #受渡区分   0:指定なし, 1:自動振替, 2:お預り金(信用返済は指定必須)
        'AccountType': 2,   #口座種別   2:一般, 4:特定, 12:法人
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
    pprint.pprint(obj)
    json_data = json.dumps(obj).encode('utf-8')

    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(101),----- TtradingStop -----" % (s_time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------

    url = 'http://localhost:18080/kabusapi/sendorder'
    req = urllib.request.Request(url, json_data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('X-API-KEY', Token);

    try:
        with urllib.request.urlopen(req) as res:
            print(res.status, res.reason)
            for header in res.getheaders():
                print(header)
            print("-----------------------------------------------")
            content = json.loads(res.read())
            pprint.pprint(content)

        s_dsp = "Symbol:%-6d:" % (Issue)
        ##print(s_dsp)

    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        pprint.pprint(content)
    except Exception as e:
        print(e)
    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(102),----- TtradingStop -----" % (s_time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------

#----------------------------------------------------------
#----- 株価が変わった場合に呼ばれる関数 ----------------------
def on_message(ws, message):
    global Password
    global Token
    global Issue 

    global d_TopLast
    global d_TopPrice
    global d_BottomPrice
    global d_LosscutPrice
    global d_TargetPrice
    global d_LastValue
    global d_BidPrice
    global t_now
    global t_BidTime

    global LONGEVENT
    global LONG0
    global LONG1st
    global LONG2nd
    global LONG3rd
    global LONGLOSS
    global LONGCLOSE

    global d_LONGEVENT
    global d_LONG0
    global d_LONG1st
    global d_LONG2nd
    global d_LONG3rd
    global d_LONGLOSS
    global d_LONGCLOSE
    #----------------------------------------------------------
    # Get Long Position Setting
    conf = configparser.ConfigParser()
    conf.read('./settings.ini')
    LONGEVENT = conf['kabuAPI']['LONGEVENT']
    LONG0 = conf['kabuAPI']['LONG0']
    LONG1st = conf['kabuAPI']['LONG1st']
    LONG2nd = conf['kabuAPI']['LONG2nd']
    LONG3rd = conf['kabuAPI']['LONG3rd']
    LONGLOSS = conf['kabuAPI']['LONGLOSS']
    LONGCLOSE = conf['kabuAPI']['LONGCLOSE']
    d_LONGEVENT = int(LONGEVENT)
    d_LONG0 = int(LONG0)
    d_LONG1st = int(LONG1st)
    d_LONG2nd = int(LONG2nd)
    d_LONG3rd = int(LONG3rd)
    d_LONGLOSS = int(LONGLOSS)
    d_LONGCLOSE = int(LONGCLOSE)

    #----------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_time = t_now.strftime("%H:%M:%S:%f")
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")
    s_dsp = "  %s, %s,--- Issue:%s ---,LONGEVENT:%d,LONG0:%d,LONG1st:%d,LONG2nd:%d,LONG3rd:%d) " % (s_time,s_BidTime, Issue,d_LONGEVENT,d_LONG0,d_LONG1st,d_LONG2nd,d_LONG3rd)
    print(s_dsp)
    #------------------------------------------------------
    flagLONG2nd = True
    if((d_LONGEVENT & 2)==0):
        flagLONG2nd = False
    if(d_LONG2nd <= 0):
        flagLONG2nd = False
    #------------------------------------------------------
    flagLONG3rd = True
    if((d_LONGEVENT & 3)==0):
        flagLONG3rd = False
    if(d_LONG3rd <= 0):
        flagLONG3rd = False
    #------------------------------------------------------
    # t_now = datetime.datetime.now().time()

    content = json.loads(message)
    CurrentPrice = content["CurrentPrice"]
    Symbol = content["Symbol"]         #銘柄
    # pprint.pprint('curPrice:', curPrice)

    if not CurrentPrice:
        d_CurrentPrice = 0
    else:
        d_CurrentPrice = int(CurrentPrice)

    # pprint.pprint(content)
    d_profit = 0        # int(0)
    if(d_BidPrice > 0):
        d_profit = d_CurrentPrice - d_BidPrice
    s_dsp = "0 %s, %s,%6d->%d,[%6d],<%d>, Symbol:%s, Top:%6d, Btm:%6d, Losscut:%6d, Target:%6d) " % (s_time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
    print(s_dsp)

    #----- メッセージの銘柄がINIのIssueと同じ
    if(Symbol == Issue):
        s_dsp = "1 (Last:%6d->Current:%d, Bid[%6d], profit<%d>, Symbol:%s, Top:%6d, Btm:%6d) " % (d_LastValue, d_CurrentPrice, d_BidPrice, d_profit, Symbol, d_TopPrice, d_BottomPrice)
        print(s_dsp)

        #----------------------------------------------------------------------
        # UP
        if(d_LastValue < d_CurrentPrice):
            # s_dsp = "(Last:%d < Cur:%d)   ,[%6d],<%d>,(10),- UP -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
            s_dsp = "2 UP  (Last:%d < Cur:%d), Cur:%d, Last:%d, Top:%d,  Btm:%d) " % (d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue, d_TopPrice, d_BottomPrice)
            print(s_dsp)
            #------------------------------------------------------------------
            if(d_BottomPrice == 0):
                # Position無し Top上げ
                if(d_TopPrice < d_CurrentPrice):
                    s_dsp = "3    ----- UP Top上げ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
                    print(s_dsp)
                    d_TopPrice = d_CurrentPrice
                    if(d_TopLast < d_TopPrice):
                        d_TopLast = d_TopPrice

                elif(d_TopPrice > d_CurrentPrice):
                    s_dsp = "3    ----- UP Top下げ ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
                    print(s_dsp)
                    d_TopPrice = d_CurrentPrice
                    if(d_TopLast < d_TopPrice):
                        d_TopLast = d_TopPrice

                # Bottom上げ
                # if(d_BottomPrice > d_CurrentPrice or d_BottomPrice == 0):
                if(d_BottomPrice == 0):
                    s_dsp = "3    ----- UP Bottom上げ ----- %d = %d" % (d_BottomPrice, d_CurrentPrice)
                    print(s_dsp)
                    d_BottomPrice = d_CurrentPrice
            #------------------------------------------------------------------
            # #----- TopPrice -----
            # if(d_TopPrice < d_CurrentPrice and d_BottomPrice < d_CurrentPrice):
            #     s_dsp = "3 (Top%d < Cur:%d and Btm:%d < Cur:%6d) " % (d_TopPrice, d_CurrentPrice, d_BottomPrice, d_CurrentPrice)
            #     print(s_dsp)

                # d_TopPrice = d_CurrentPrice

            d_Diff = d_TopPrice - d_BottomPrice
            s_dsp = "2 (Last:%d < Cur:%d),----- Diff:%d -----, d_LONG1st:%6d,  Btm:%6d, Losscut:%6d,  Target:%6d) " % (d_LastValue, d_CurrentPrice, d_Diff, d_LONG1st, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
                
            # Positionは１つ:d_BidPrice == 0
            if(d_Diff >= d_LONG1st and d_BidPrice == 0):
                # s_dsp = "LONG %6d,[%6d],(23),Top:%6d,  Btm:%6d,  (Diff:%d>=d_LONG1st:%d)>>LongOrder() " % (d_BidPrice, d_BidPrice,d_profit,d_TopPrice,d_BottomPrice, d_profit,d_LONG1st)
                # d_BottomPrice = d_CurrentPrice
                d_BidPrice = d_CurrentPrice
                t_BidTime = datetime.datetime.now().time()                           #global変数に保存
                s_BidTime = t_BidTime.strftime("%H:%M:%S:f")
                s_dsp = "LONG %s, %s, (Diff:%d>=LONG1st:%d and Bid:%d==0), LONGEVENT:%d,LONG0:%d,LONG2nd:%d,LONG3rd:%d " % (s_time,s_BidTime, d_Diff, d_LONG1st, d_BidPrice, d_LONGEVENT,d_LONG0,d_LONG2nd,d_LONG3rd)
                print(s_dsp)
                #--------------------------------------------------------------
                LongOrder(ws, message)
                #--------------------------------------------------------------
                t_now = datetime.datetime.now().time()
                s_time = t_now.strftime("%H:%M:%S:%f")
                s_dsp = "LONG %s, %s, LongOrder(), (LONGEVENT:%d, LONG0:%d, LONG1st:%d, LONG2nd:%d, LONG3rd:%d) " % (s_time,s_BidTime, d_LONGEVENT, d_LONG0, d_LONG1st, d_LONG2nd, d_LONG3rd)
                #--------------------------------------------------------------
                checkSt = KABUPOSI.kabu_positions.APIPosition.check_position(symbol=Symbol, side='2')
                if(checkSt == 0):
                    # d_BidPrice = 0                      # else 一時マスク 
                    # else '一時マスク' 
                    # ###d_BottomPrice = d_LastValue                        #'一時マスク' else
                    print("----- 一時的にBitPriceを設定　for simulation -----")
                    #'一時マスク' end
                    s_dsp = "LONG %s, %s, 0=check_position(), Cur:%6d,Bid[%6d], Btm:%6d, Losscut:%6d, Target:%6d) " % (s_time,s_BidTime, d_CurrentPrice, d_BidPrice, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                    # s_dsp = "LONG %s, %s, %6d,[%6d],<%d>,(24)0=check_position(),  Btm:%6d,Losscut:%6d,  Target:%6d) " % (s_time,s_BidTime, d_LastValue,d_BidPrice,d_profit, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                    print(s_dsp)
                else:
                    d_BottomPrice = d_LastValue
                    s_dsp = "LONG %s, %s, %d=check_position(), Cur:%6d,Bid[%6d], Btm:%6d, Losscut:%6d, Target:%6d) " % (s_time,s_BidTime, checkSt, d_CurrentPrice, d_BidPrice, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                    # s_dsp = "%s, %s,%6d,[%6d],<%d>,(24)%d=check_position(),  Btm:%6d,Losscut:%6d,  Target:%6d) " % (s_time,s_BidTime, d_LastValue,d_BidPrice,d_profit, checkSt, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                    print(s_dsp)

                    #     # キャンセルからの損切り注文
                    #     cancelorder.cancelorder()
                    #     if(d_BidPrice >= d_LastValue):
                    #     ##s_dsp = "%s, %s,%6d,[%6d],<%d>,(8)>> Bottom:%6d >= Current:%6d" % (t_now.strftime("%H:%M:%S"), t_BidTime("%H:%M:%S"), d_LastValue,t_BidTime, d_BidPrice, d_BottomPrice, d_LastValue)
                    #     d_BottomPrice = d_LastValue
                    #     ##print(s_dsp)
            d_LastValue = d_CurrentPrice
        #----------------------------------------------------------------------
        # ==
        elif(d_LastValue == d_CurrentPrice):
            s_dsp = "2 PART(Last:%d == Cur:%d), Cur:%d, Last:%d, Top:%d,  Btm:%d) " % (d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue, d_TopPrice, d_BottomPrice)
            print(s_dsp)
            # s_dsp = "%s, %s,%6d->%d,[%6d],<%d>,(11),- Symbol:%s -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
            # print(s_dsp)

            # Bottom下げ
            if(d_BottomPrice > d_CurrentPrice and d_BottomPrice == 0):
                s_dsp = "3    ----- PARTIAL Bottom下げ ----- %d = %d" % (d_BottomPrice, d_CurrentPrice)
                print(s_dsp)
                d_BottomPrice = d_CurrentPrice

            if(d_TopPrice == 0):
                s_dsp = "3    ----- PARTIAL Top ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
                print(s_dsp)
                d_TopPrice = d_CurrentPrice
                if(d_TopLast < d_TopPrice):
                    d_TopLast = d_TopPrice
            # Position無し Top下げ 
            # if(d_TopPrice > d_CurrentPrice and d_BidPrice == 0):
            #     s_dsp = "3    ----- PARTIAL Top下げ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
            #     print(s_dsp)
            #     d_TopPrice = d_CurrentPrice
            #     if(d_TopLast < d_TopPrice):
            #         d_TopLast = d_TopPrice

            # elif(d_TopPrice < d_CurrentPrice):
            #     s_dsp = "3    ----- PARTIAL Top下げ ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
            #     print(s_dsp)
            #     d_TopPrice = d_CurrentPrice
            #     if(d_TopLast < d_TopPrice):
            #         d_TopLast = d_TopPrice

        #----------------------------------------------------------------------
        # Down
        else:
            s_dsp = "2 Down(Last:%d > Cur:%d), Cur:%d, Last:%d, LastTop:%d, Top:%d,  Btm:%d) " % (d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue, d_TopLast, d_TopPrice, d_BottomPrice)
            print(s_dsp)
            # s_dsp = "%s, %s,%6d->%d,[%6d],<%d>,(12),- Symbol:%s -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
            # print(s_dsp)
            # 損切り価格 Top-Minus
            if(d_BidPrice > 0):
                # Loss-Cut Transactions
                d_LosscutPrice = d_BidPrice - d_LONGLOSS            # Entry - LossCut
                d_TargetPrice =  d_TopPrice - d_LONGLOSS            # 利益確定Default:(Top-LossCut)
                # (Top - LONG3rd)で利益確定 (優先度:LONG3rd < LONG2nd)
                if(flagLONG3rd):
                    d_TargetPrice =  d_TopPrice - d_LONG3rd
                # (Top - LONG2nd)で利益確定 (優先度:LONG3rd < LONG2nd)
                if(flagLONG2nd):
                    d_TargetPrice =  d_TopPrice - d_LONG2nd

                # Loss-cut OR (利益確定・強制終了:LONGCLOSE = 1)
                if(d_LastValue <= d_LosscutPrice or d_LONGCLOSE > 0):
                    
                    if(d_profit <= 0):
                        s_dsp = "%6d,[%6d],(30),- 損切り(%d) ---,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        print(s_dsp)
                    else:
                        s_dsp = "%6d,[%6d],(31),- 利益確定(%d) -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        print(s_dsp)

                    TtradingStop(ws, message)
                    d_TopPrice = d_LastValue
                    d_BottomPrice = d_LastValue
                    d_BidPrice = 0
                    d_TargetPrice = 0
                    d_LosscutPrice = 0
                    print("----- break -----")
                    # ws.close()
                    
                if(d_LastValue <= d_TargetPrice):
                    s_dsp = "%6d,[%6d],(40),- 利益確定(%d) -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                    print(s_dsp)
                    d_TopPrice = d_LastValue
                    d_BottomPrice = d_LastValue
                    d_BidPrice = 0
                    d_TargetPrice = 0
                    d_LosscutPrice = 0
                    TtradingStop(ws, message)
                    print("----- break 利益確定 -----")
            # else:
            #     s_dsp = "%6d,[%6d],(39),- Posi無し(%d) ---,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
            #     print(s_dsp)

            # Bottom下げ
            if(d_BottomPrice > d_CurrentPrice and d_BidPrice == 0):
                s_dsp = "    ----- DOWN Bottom下げ ----- %d = %d " % (d_BottomPrice, d_CurrentPrice)
                print(s_dsp)
                d_BottomPrice = d_CurrentPrice
            # Position無し Top下げ
            if(d_TopPrice > d_CurrentPrice and d_BidPrice == 0):
                s_dsp = "    ----- DOWN Top下げ ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
                print(s_dsp)
                d_TopPrice = d_CurrentPrice
                if(d_TopLast < d_TopPrice):
                    d_TopLast = d_TopPrice

                # else:
                #     d_TopLast = d_TopPrice
                # d_TopPrice = d_CurrentPrice

                # #----- BottomPrice -----
                # if(d_BottomPrice > d_LastValue):
                #     s_dsp = "%6d,[%6d],(51), ----- Bottom下げ ----,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                #     ##s_dsp = "%s, %s,%6d,[%6d],<%d>,(21), - Bottom --,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_time,s_BidTime,d_LastValue,d_BidPrice,d_profit,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                #     d_BottomPrice = d_LastValue
                #     print(s_dsp)

                # # Position無し,Top下げ
                # if(d_TopPrice > d_LastValue and d_BidPrice == 0):   # d_TopPrice >= d_BidPrice):
                #     s_dsp = "%6d,[%6d],(52),---- Posi無し,Top下げ ----,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                #     ##s_dsp = "%s, %s,%6d,[%6d],<%d>,(21), - Bottom --,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_time,s_BidTime,d_LastValue,d_BidPrice,d_profit,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                #     d_TopPrice = d_LastValue
                #     print(s_dsp)

            d_LastValue = d_CurrentPrice
            if(d_TopPrice == 0):
                d_TopPrice = d_CurrentPrice
            if(d_TopLast == 0):
                d_TopLast = d_TopPrice
        #----------------------------------------------------------------------


        # if(d_BottomPrice == 0):
        #     d_BottomPrice = d_LastValue
        #     s_dsp = "%6d,[%6d],(11)- Bottom==0-,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
        #     print(s_dsp)
        # # el
        # if (d_TopPrice == 0):
        #     d_TopPrice = d_LastValue
        #     s_dsp = "%6d,[%6d],(12)- Top==0 ---,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (d_LastValue,d_BidPrice,d_profit,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
        #     print(s_dsp)

                 #     # キャンセルからの損切り注文
                #     cancelorder.cancelorder()
                #     ws.close()
        s_dsp = "---------- Last:%6d->Current:%d, Bid[%6d], profit<%d>, Symbol:%s, LastTop:%d, Top:%d, Btm:%d) " % (d_LastValue, d_CurrentPrice, d_BidPrice, d_profit, Symbol, d_TopLast, d_TopPrice, d_BottomPrice)
        print(s_dsp)

#----------------------------------------------------------
# ３．注文発注（信用）
# （１）新規
# コマンド：python kabusapi_sendorder_margin_new.py     kabusapi_sendorder_margin_new.pyより
def LongOrder(ws, message):
    global Password
    global Token
    global Issue 

    global LONGEVENT
    global LONG0
    global LONG1st
    global LONG2nd
    global LONG3rd
    global LONGLOSS
    # global d_TopPrice
    # global d_BottomPrice
    # global d_LosscutPrice
    # global d_TargetPrice
    global d_LastValue
    global d_BidPrice
    global s_BidPrice
    global t_now
    global t_BidTime
    #------------------------------------------------------
    BidPrice = str(d_BidPrice)
    #------------------------------------------------------
    global t_now
    global t_BidTime
    global t_SellTime

    t_now = datetime.datetime.now().time()
    s_time = t_now.strftime("%H:%M:%S:%f")
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")
    s_SellTime = t_SellTime.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(200),----- LongOrder -----" % (s_time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------

    obj = { 'Password': Password,   #123456','111111',
        'Symbol': Issue,        #銘柄          'Symbol': '6521',       #6521：オキサイド
        'Exchange': 1,          #1:東証
        'SecurityType': 1,      #1:株式
        'Side': '2',            #2:買
        'CashMargin': 2,        #信用区分       2:新規
        'MarginTradeType': 3,   #信用取引区分   1:制度信用, 2:一般信用（長期）, 3:一般信用（デイトレ）
        'DelivType': 0,         #受渡区分       0:指定無し
        'AccountType': 2,       #口座種別       2：一般
        'Qty': 100,             #注文数量       100
        # 'FrontOrderType': 30,   #執行条件       10:成行,20:指値,30:逆指値,    
        # 'FrontOrderType': 10,   #執行条件       10:成行
        'FrontOrderType': 20,   #執行条件       20:指値

        # 'Price': 9450.0,        #注文価格
        'Price': BidPrice,      #注文価格
        'ExpireDay': 0,         #注文有効期限   0:today     yyyyMMdd
        # 'ReverseLimitOrder': {}     #逆指値条件
        'ReverseLimitOrder': {  #逆指値条件
                            #    'TriggerSec': 2, #1.発注銘柄 2.NK225指数 3.TOPIX指数
                            #    'TriggerPrice': 30000,
                            #    'UnderOver': 2, #1.以下 2.以上
                            #    'AfterHitOrderType': 2, #1.成行 2.指値 3. 不成
                            #    'AfterHitPrice': 8435
                               'TriggerSec': 1,         #1.発注銘柄 2.NK225指数 3.TOPIX指数
                            #    'TriggerPrice': 9450,
                               'TriggerPrice': BidPrice,
                               'UnderOver': 2,          #1.以下 2.以上
                               'AfterHitOrderType': 2,  #1.成行 2.指値 3. 不成
                               'AfterHitPrice': BidPrice
                               }
      }
    json_data = json.dumps(obj).encode('utf-8')
    s_dsp = "%6d,[%6d],(50),----- LongOrder -----" % (d_LastValue, d_BidPrice)
    print(s_dsp)
    #------------------------------------------------------
    pprint.pprint(json_data)
    print("----- 発行マスク -----")

    # url = 'http://localhost:18080/kabusapi/sendorder'
    # req = urllib.request.Request(url, json_data, method='POST')
    # req.add_header('Content-Type', 'application/json')
    # req.add_header('X-API-KEY', Token)

    # try:
    #     with urllib.request.urlopen(req) as res:
    #         print(res.status, res.reason)
    #         for header in res.getheaders():
    #             print(header)
    #         print("-----------------------------------------------")
    #         content = json.loads(res.read())
    #         pprint.pprint(content)
    #         #----- {'OrderId': '20210708A01N28692121', 'Result': 0} -----
    #         s_dsp = "----- Result:%s/OrderId:%s  (BidPrice:%6d,Issue:%s, d_LastValue:%6d) -----" % (content["Result"], content["OrderId"], BidPrice, Issue, d_LastValue)
    #         print(s_dsp)

    # except urllib.error.HTTPError as e:
    #     print(e)
    #     content = json.loads(e.read())
    #     pprint.pprint(content)
    # except Exception as e:
    #     print(e)
    # t_now = datetime.datetime.now().time()
    # s_time = t_now.strftime("%H:%M:%S:%f")
    # s_dsp = "%s,BidTime%s,SellTime%s,(201),----- LongOrder -----" % (s_time,s_BidTime, s_SellTime)
    # print(s_dsp)
    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(201),----- LongOrder -----" % (s_time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------

#----- エラー発生 -----
def on_error(ws, error):
    print('--- ERROR --- ')
    print(error)

def on_close(ws):
    print('--- DISCONNECTED --- ')

#----------------------------------------------------------
#----- コールバックされる関数 -----
def on_open(ws):
    print('--- CONNECTED コールバック関数設定 --- ')

    def run(*args):
        while(True):
            line = sys.stdin.readline()
            if line != '':
                print('closing...')
                ws.close()
    _thread.start_new_thread(run, ())

    #------------------------------------------------------

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
