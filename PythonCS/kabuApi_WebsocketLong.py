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
conf.read('settings.ini')
APIPassword = conf['kabuAPI']['APIPassword']
Password = conf['kabuAPI']['Password']
Token = conf['kabuAPI']['Token']
Issue1 = conf['kabuAPI']['Issue1']
Issue2 = conf['kabuAPI']['Issue2']
Issue3 = conf['kabuAPI']['Issue3']
SimulateID = conf['kabuAPI']['SimulateID']
PauseTime = conf['kabuAPI']['PauseTime']

LONGEVENT = conf['kabuAPI']['LONGEVENT']
LONG0 = conf['kabuAPI']['LONG0']
LONG1st = conf['kabuAPI']['LONG1st']
LONG2nd = conf['kabuAPI']['LONG2nd']
LONG3rd = conf['kabuAPI']['LONG3rd']
LONGLOSS = conf['kabuAPI']['LONGLOSS']
LONGCLOSE = conf['kabuAPI']['LONGCLOSE']
#------------------------------------------------------------------------------
#							＊
#							＊								    LONGCLOSE = 1   ( Profit・強制終了)
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
#------------------------------------------------------------------------------
#							＊
#							＊								    LONGCLOSE = 1   ( Profit・強制終了)
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

d_CurrentPrice = 0
d_SimulateID = int(SimulateID)

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
# t_SellTime = t_now
s_CurrentTime = t_now.strftime("%H:%M:%S:%f")

d_TopLast1 = int(0)
d_TopPrice1 = int(0)
d_BottomPrice1 = int(0)
d_LosscutPrice1 = int(0)
d_TargetPrice1 = int(0)
d_LastValue1 = int(0)
d_BidPrice1 = int(0)
# t_now = datetime.datetime.now().time()
t_BidTime1 = datetime.datetime.now().time()      #t_now                       #Purchase time
# t_SellTime1 = t_now

d_TopLast2 = int(0)
d_TopPrice2 = int(0)
d_BottomPrice2 = int(0)
d_LosscutPrice2 = int(0)
d_TargetPrice2 = int(0)
d_LastValue2 = int(0)
d_BidPrice2 = int(0)
# t_now = datetime.datetime.now().time()
t_BidTime2 = datetime.datetime.now().time()      #t_now                       #Purchase time
# t_SellTime2 = t_now
s_Tab = "    "
s_Tab1 = "    "
s_Tab2 = "        "
s_Tab3 = "            "
# MessageList = {}

#----------------------------------------------------------
s_DateTime = t_now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
WritefileName = './Result' + s_DateTime + '.csv'
# s_DateTime = t_now.strftime("result")  #YYYY-MM-DDTHH:MM:SS
# WritefileName = './Result' + s_DateTime + '.csv'
f_write = False;
writeCsvfile = open(WritefileName, 'w')     #, newline='')
if (writeCsvfile):
    f_write = True;
    if(f_write):
        s_dsp = "True = %s" % (WritefileName)
        writeCsvfile.write(s_dsp + '\n')
    else:
        s_dsp = "False = %s" % (WritefileName)
    print(s_dsp)



#----- 株価が変わった場合に呼ばれる関数 ----------------------
def Symbol_Price1(ws, message, Symbol, writeCsvfile):

    s_dsp = "200-0 Symbol_Price1,%s" % (Symbol)
    print(s_dsp)

    global Password
    global Token
    # global Issue 
    global d_CurrentPrice
    global s_Tab
    # Use Sub Module --------------------------------------
    global d_TopLast
    global d_TopPrice
    global d_BottomPrice
    global d_LosscutPrice
    global d_TargetPrice
    global d_LastValue
    global d_BidPrice
    global t_BidTime
    #------------------------------------------------------
    # Issue 1
    global d_TopLast1
    global d_TopPrice1
    global d_BottomPrice1
    global d_LosscutPrice1
    global d_TargetPrice1
    global d_LastValue1
    global d_BidPrice1
    global t_BidTime1
    # # Issue 2
    # global d_TopLast2
    # global d_TopPrice2
    # global d_BottomPrice2
    # global d_LosscutPrice2
    # global d_TargetPrice2
    # global d_LastValue2
    # global d_BidPrice2
    # global t_BidTime2
    global s_CurrentTime

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
    global f_write
    
    s_dsp = "200-1 Symbol_Price1,%s" % (Symbol)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')


    # Get Long Position Setting
    conf = configparser.ConfigParser()
    conf.read('settings.ini')
    # LONGEVENT = conf['kabuAPI']['LONGEVENT']
    # Issue1 = conf['kabuAPI']['Issue1']
    # Issue2 = conf['kabuAPI']['Issue2']
    # Issue3 = conf['kabuAPI']['Issue3']
    # SimulateID = conf['kabuAPI']['SimulateID']    
    # PauseTime = conf['kabuAPI']['PauseTime']

    # LONG0 = conf['kabuAPI']['LONG0']
    # LONG1st = conf['kabuAPI']['LONG1st']
    # LONG2nd = conf['kabuAPI']['LONG2nd']
    # LONG3rd = conf['kabuAPI']['LONG3rd']
    # LONGLOSS = conf['kabuAPI']['LONGLOSS']
    # LONGCLOSE = conf['kabuAPI']['LONGCLOSE']

    LONG0 = conf[Issue1]['LONG0']
    LONG1st = conf[Issue1]['LONG1st']
    LONG2nd = conf[Issue1]['LONG2nd']
    LONG3rd = conf[Issue1]['LONG3rd']
    LONGLOSS = conf[Issue1]['LONGLOSS']
    LONGCLOSE = conf[Issue1]['LONGCLOSE']
    d_LONGEVENT = int(LONGEVENT)
    d_LONG0 = int(LONG0)
    d_LONG1st = int(LONG1st)
    d_LONG2nd = int(LONG2nd)
    d_LONG3rd = int(LONG3rd)
    d_LONGLOSS = int(LONGLOSS)
    d_LONGCLOSE = int(LONGCLOSE)
    # Symbol１用 global変数を取得
    d_TopLast       = d_TopLast1
    d_TopPrice      = d_TopPrice1
    d_BottomPrice   = d_BottomPrice1
    d_LosscutPrice  = d_LosscutPrice1
    d_TargetPrice   = d_TargetPrice1
    d_LastValue     = d_LastValue1
    d_BidPrice      = d_BidPrice1
    t_BidTime       = t_BidTime1    

    s_Time = s_CurrentTime
    d_profit = 0        # int(0)
    if(d_BidPrice > 0):
        d_profit = d_CurrentPrice - d_BidPrice
    d_Diff = 0
    if(d_LastValue != d_CurrentPrice):
        d_Diff = d_LastValue - d_CurrentPrice
    # s_dsp = "--100--,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    # print(s_dsp)
    # if(f_write):
    #     writeCsvfile.write(s_dsp + '\n')
    #----------------------------------------------------------
    # s_dsp = " %s2  (%s),Cur:%d, L:%d,(%d),     LONG:%5d,(%d)     Top:%5d,  Btm:%5d, LossC:%5d, Target:%5d) " % (s_Tab, Symbol, d_CurrentPrice, d_LastValue,d_Diff, d_BidPrice,d_profit, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    s_dsp = "200,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')

    if(Symbol is not None):
        up_down = 0
        if(d_LastValue < d_CurrentPrice):
            up_down = 1
        elif(d_LastValue > d_CurrentPrice):
            up_down = -1
            
        # Position無し
        if(d_BidPrice == 0):
            # s_dsp = " %s2 0(%s),Cur:%d, L:%d,(%d),     LONG:%5d,(%d)     Top:%5d,  Btm:%5d, LossC:%5d, Target:%5d) " % (s_Tab, Symbol, d_CurrentPrice, d_LastValue,d_Diff, d_BidPrice,d_profit, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            s_dsp = "211,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            #下げ相場　Bottom == Top
            if(d_LastValue > d_CurrentPrice):
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                # d_LastValue = d_CurrentPrice
            #上げ相場　Bottom < Top
            else:
                # Position無し Top上げ
                if(d_TopPrice < d_CurrentPrice):
                    # s_dsp = " < 3 ----- UP Top上げ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
                    # s_dsp = "212%s上 ----- Top:%d < Cur:%d -----" % (s_Tab, d_TopPrice, d_CurrentPrice)
                    # print(s_dsp)
                    d_TopPrice = d_CurrentPrice
                    s_dsp = "212 Top,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    # if(d_TopLast < d_TopPrice):
                    #     d_TopLast = d_TopPrice
                    # Illegal check
                    # if(d_BottomPrice > d_TopPrice):
                    #     d_BottomPrice = d_TopPrice
                # "W"
                elif(d_TopPrice > d_CurrentPrice):
                    # s_dsp = "213%s上 ----- CR:%d < Top:%d -----" % (s_Tab, d_CurrentPrice, d_TopPrice)
                    # print(s_dsp)
                    s_dsp = "213,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')

            d_Diff = 0
            if(d_BottomPrice > 0):
                d_Diff = d_TopPrice - d_BottomPrice
            else:
                d_BottomPrice = d_CurrentPrice
            if(up_down > 0):
                # s_dsp = "214%sUP(Last:%d < Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                # print(s_dsp)
                s_dsp = "214 UP,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
            elif(up_down < 0):
                # s_dsp = "215%sDouwn (Last:%d > Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                # print(s_dsp)
                s_dsp = "214 Douwn,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
            # else:
            #     s_dsp = "216===== (Last:%d == Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            #     print(s_dsp)
                
            # Positionは１つ:d_BidPrice == 0
            if(d_Diff >= d_LONG1st and up_down > 0):    # and d_BidPrice == 0):
                # s_dsp = "LONG %6d,[%6d],(23),Top:%6d,  Btm:%6d,  (Diff:%d>=d_LONG1st:%d)>>LongOrder() " % (d_BidPrice, d_BidPrice,d_profit,d_TopPrice,d_BottomPrice, d_profit,d_LONG1st)
                # d_BottomPrice = d_CurrentPrice
                # LONG Price保存
                d_BidPrice = d_CurrentPrice
                d_profit = 0
                t_BidTime = datetime.datetime.now().time()                           #global変数に保存
                s_BidTime = t_BidTime.strftime("%H:%M:%S:f")
                # s_dsp = " %sLONG %s, %s, (Diff:%d>=LONG1st:%d and Bid:%d==0), LONGEVENT:%d,LONG0:%d,LONG2nd:%d,LONG3rd:%d " % (s_Tab, s_Time,s_BidTime, d_Diff, d_LONG1st, d_BidPrice, d_LONGEVENT,d_LONG0,d_LONG2nd,d_LONG3rd)
                s_dsp = "220,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')

                #-----LONG発注 -------------------------------
                if(ws != None and message != None):
                    LongOrder(ws, message, Symbol)
                    t_now = datetime.datetime.now().time()
                    s_Time = t_now.strftime("%H:%M:%S:%f")
                    s_dsp = "221%sLONG %s, %s, LongOrder(), (LONGEVENT:%d, LONG0:%d, LONG1st:%d, LONG2nd:%d, LONG3rd:%d) " % (s_Tab, s_Time,s_BidTime, d_LONGEVENT, d_LONG0, d_LONG1st, d_LONG2nd, d_LONG3rd)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    checkSt = KABUPOSI.kabu_positions.APIPosition.check_position(Symbol, side='2')
                    if(checkSt == 0):
                        d_BidPrice = 0
                        d_profit = 0
                        # d_BottomPrice = d_CurrentPrice
                        # print("----- 一時的にBitPriceを設定　for simulation -----")
                        # s_dsp = "222%sLONG %s, %s, 0=check_position(), Cur:%6d,Bid[%6d], Btm:%6d, Losscut:%6d, Target:%6d) " % (s_Tab, s_Time,s_BidTime, d_CurrentPrice, d_BidPrice, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        # s_dsp = "122LONG %s, %s, %6d,[%6d],<%d>,(24)0=check_position(),  Btm:%6d,Losscut:%6d,  Target:%6d) " % (s_Time,s_BidTime, d_LastValue,d_BidPrice,d_profit, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        s_dsp = "222 LONG NG,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                        print(s_dsp)
                        if(f_write):
                            writeCsvfile.write(s_dsp + '\n')
                    else:
                        d_BottomPrice = d_LastValue
                        # s_dsp = "223%sLONG %s, %s, %d=check_position(), Cur:%6d,Bid[%6d], Btm:%6d, Losscut:%6d, Target:%6d) " % (s_Tab, s_Time,s_BidTime, checkSt, d_CurrentPrice, d_BidPrice, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        # s_dsp = "123%s, %s,%6d,[%6d],<%d>,(24)%d=check_position(),  Btm:%6d,Losscut:%6d,  Target:%6d) " % (s_Time,s_BidTime, d_LastValue,d_BidPrice,d_profit, checkSt, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        s_dsp = "223 LONG,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                        print(s_dsp)
                        if(f_write):
                            writeCsvfile.write(s_dsp + '\n')

                        #     # キャンセルからの LossCut注文
                        #     cancelorder.cancelorder()
                        #     if(d_BidPrice >= d_LastValue):
                        #     ##s_dsp = "%s, %s,%6d,[%6d],<%d>,(8)>> Bottom:%6d >= Current:%6d" % (t_now.strftime("%H:%M:%S"), t_BidTime("%H:%M:%S"), d_LastValue,t_BidTime, d_BidPrice, d_BottomPrice, d_LastValue)
                        #     d_BottomPrice = d_LastValue
                        #     ##print(s_dsp)
                #--------------------------------------------------------------
            d_LastValue = d_CurrentPrice
            # s_dsp = "229%s(%s),Cur:%d, L:%d,(%d),     LONG:%5d,(%d)     Top:%5d,  Btm:%5d, LossC:%5d, Target:%5d) " % (s_Tab, Symbol, d_CurrentPrice, d_LastValue,d_Diff, d_BidPrice,d_profit, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            s_dsp = "229,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

        # Position有り
        else:       #if(d_BidPrice > 0):
            # UP    (Top < message."CurrentPrice")
            if(d_TopPrice < d_CurrentPrice):
                d_TopPrice = d_CurrentPrice

            if(d_BottomPrice == 0):
                d_BottomPrice = d_CurrentPrice
            #------------------------------------------------------------------
            #----- TopPrice -----
            # if(d_TopPrice < d_CurrentPrice and d_BottomPrice < d_CurrentPrice):
            #     s_dsp = "3 (Top%d < Cur:%d and Btm:%d < Cur:%6d) " % (d_TopPrice, d_CurrentPrice, d_BottomPrice, d_CurrentPrice)
            #     print(s_dsp)

            if(up_down > 0):
                # s_dsp = "230%sUP(Last:%d < Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                s_dsp = "230 UP,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            elif(up_down < 0):
                # s_dsp = " 231%sDouwn(Last:%d > Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                s_dsp = "231 Down,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            # else:
            #     s_dsp = " %s3P ===== (Last:%d == Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            # s_dsp = "%s, %s,%6d->%d,[%6d],<%d>,(12),- Symbol:%s -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_Time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
            # print(s_dsp)
            #  LossCut価格 Top-Minus
            d_LosscutPrice = d_BidPrice - d_LONGLOSS            # Loss-Cut Transactions (Entry - LossCut)
            d_TargetPrice =  d_TopPrice - d_LONGLOSS            #  ProfitDefault:(Top-LossCut)
            # (Top - LONG3rd)で Profit (優先度:LONG3rd < LONG2nd)
            # if(flagLONG3rd):
            #     d_TargetPrice =  d_TopPrice - d_LONG3rd
            # # (Top - LONG2nd)で Profit (優先度:LONG3rd < LONG2nd)
            # if(flagLONG2nd):
            d_TargetPrice =  d_TopPrice - d_LONG2nd

            # Loss-cut OR ( Profit・強制終了:LONGCLOSE = 1)
            if(d_CurrentPrice <= d_LosscutPrice or d_CurrentPrice < d_BidPrice  or d_LONGCLOSE > 0):
                
                # if(d_profit <= 0):
                s_dsp = "241 LossCut,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
                # else:
                #     s_dsp = "142 Profit,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                #     print(s_dsp)
                #     if(f_write):
                #         writeCsvfile.write(s_dsp + '\n')
                # # return -1
                if(ws != None and message != None):
                    TtradingStop(ws, message)
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                d_BidPrice = 0
                d_profit = 0
                d_TargetPrice = 0
                d_LosscutPrice = 0
                s_dsp = "242 LossCut,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
                
            elif(d_CurrentPrice <= d_TargetPrice):
                # s_dsp = " %s%6d,[%6d],(40),-  Profit(%d) -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_Tab, d_LastValue,d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                # print(s_dsp)
                s_dsp = "250 Profit,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                d_BidPrice = 0
                d_profit = 0
                d_TargetPrice = 0
                d_LosscutPrice = 0
                # return -1
                if(ws != None and message != None):
                    TtradingStop(ws, message)

                s_dsp = "251 Profit,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')

            else:   #Illigal Check
                if(d_BottomPrice == 0):
                    s_dsp = "260Bottom:0,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    d_BottomPrice = d_CurrentPrice

                if(d_TopPrice == 0):
                    s_dsp = "261Top:0,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    d_TopPrice = d_CurrentPrice
                    if(d_TopLast < d_TopPrice):
                        d_TopLast = d_TopPrice
                # s_dsp = "263Partial,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                # print(s_dsp)
                # if(f_write):
                #     writeCsvfile.write(s_dsp + '\n')

        s_dsp = "290,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        print(s_dsp)
        if(f_write):
            writeCsvfile.write(s_dsp + '\n')
        d_LastValue = d_CurrentPrice
        if(d_TopPrice == 0):
            d_TopPrice = d_CurrentPrice
        if(d_TopLast == 0):
            d_TopLast = d_TopPrice
        # global変数に保存
        d_TopLast1      = d_TopLast
        d_TopPrice1     = d_TopPrice
        d_BottomPrice1  = d_BottomPrice
        d_LosscutPrice1 = d_LosscutPrice
        d_TargetPrice1  = d_TargetPrice
        d_LastValue1    = d_LastValue
        d_BidPrice1     = d_BidPrice
        t_BidTime1      = t_BidTime    
        #----------------------------------------------------------------------
        #     # キャンセルからの損切り注文
        #     cancelorder.cancelorder()
        #     ws.close()
    s_dsp = "291,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')
    s_dsp = "292,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue1, d_BidPrice, d_profit \
        , d_TopLast1, d_TopPrice1,  d_BottomPrice1, d_LosscutPrice1, d_TargetPrice1)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')




#----- 株価が変わった場合に呼ばれる関数 ----------------------
def Symbol_Price(ws, message, Symbol_Issue, writeCsvfile):

    Symbol = Symbol_Issue

    global Password
    global Token
    # global Issue 
    global d_CurrentPrice
    global s_Tab
    # Use Sub Module --------------------------------------
    global d_TopLast
    global d_TopPrice
    global d_BottomPrice
    global d_LosscutPrice
    global d_TargetPrice
    global d_LastValue
    global d_BidPrice
    global t_BidTime
    #------------------------------------------------------
    # Issue 1
    # global d_TopLast1
    # global d_TopPrice1
    # global d_BottomPrice1
    # global d_LosscutPrice1
    # global d_TargetPrice1
    # global d_LastValue1
    # global d_BidPrice1
    # global t_BidTime1
    # # Issue 2
    # global d_TopLast2
    # global d_TopPrice2
    # global d_BottomPrice2
    # global d_LosscutPrice2
    # global d_TargetPrice2
    # global d_LastValue2
    # global d_BidPrice2
    # global t_BidTime2
    global s_CurrentTime

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
    global f_write

    s_Time = s_CurrentTime
    d_profit = 0        # int(0)
    if(d_BidPrice > 0):
        d_profit = d_CurrentPrice - d_BidPrice
    d_Diff = 0
    if(d_LastValue != d_CurrentPrice):
        d_Diff = d_LastValue - d_CurrentPrice
    # s_dsp = "--100--,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    # print(s_dsp)
    # if(f_write):
    #     writeCsvfile.write(s_dsp + '\n')
    #----------------------------------------------------------
    # s_dsp = " %s2  (%s),Cur:%d, L:%d,(%d),     LONG:%5d,(%d)     Top:%5d,  Btm:%5d, LossC:%5d, Target:%5d) " % (s_Tab, Symbol_Issue, d_CurrentPrice, d_LastValue,d_Diff, d_BidPrice,d_profit, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    s_dsp = "200,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')

    if(Symbol_Issue is not None):
        up_down = 0
        if(d_LastValue < d_CurrentPrice):
            up_down = 1
        elif(d_LastValue > d_CurrentPrice):
            up_down = -1
            
        # Position無し
        if(d_BidPrice == 0):
            # s_dsp = " %s2 0(%s),Cur:%d, L:%d,(%d),     LONG:%5d,(%d)     Top:%5d,  Btm:%5d, LossC:%5d, Target:%5d) " % (s_Tab, Symbol_Issue, d_CurrentPrice, d_LastValue,d_Diff, d_BidPrice,d_profit, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            s_dsp = "211,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            #下げ相場　Bottom == Top
            if(d_LastValue > d_CurrentPrice):
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                # d_LastValue = d_CurrentPrice
            #上げ相場　Bottom < Top
            else:
                # Position無し Top上げ
                if(d_TopPrice < d_CurrentPrice):
                    # s_dsp = " < 3 ----- UP Top上げ----- %d = %d" % (d_TopPrice, d_CurrentPrice)
                    # s_dsp = "212%s上 ----- Top:%d < Cur:%d -----" % (s_Tab, d_TopPrice, d_CurrentPrice)
                    # print(s_dsp)
                    d_TopPrice = d_CurrentPrice
                    s_dsp = "212 Top,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    # if(d_TopLast < d_TopPrice):
                    #     d_TopLast = d_TopPrice
                    # Illegal check
                    # if(d_BottomPrice > d_TopPrice):
                    #     d_BottomPrice = d_TopPrice
                # "W"
                elif(d_TopPrice > d_CurrentPrice):
                    # s_dsp = "213%s上 ----- CR:%d < Top:%d -----" % (s_Tab, d_CurrentPrice, d_TopPrice)
                    # print(s_dsp)
                    s_dsp = "213,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')

            d_Diff = 0
            if(d_BottomPrice > 0):
                d_Diff = d_TopPrice - d_BottomPrice
            else:
                d_BottomPrice = d_CurrentPrice
            if(up_down > 0):
                # s_dsp = "214%sUP(Last:%d < Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                # print(s_dsp)
                s_dsp = "214 UP,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
            elif(up_down < 0):
                # s_dsp = "215%sDouwn (Last:%d > Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                # print(s_dsp)
                s_dsp = "214 Douwn,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
            # else:
            #     s_dsp = "216===== (Last:%d == Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            #     print(s_dsp)
                
            # Positionは１つ:d_BidPrice == 0
            if(d_Diff >= d_LONG1st and up_down > 0):    # and d_BidPrice == 0):
                # s_dsp = "LONG %6d,[%6d],(23),Top:%6d,  Btm:%6d,  (Diff:%d>=d_LONG1st:%d)>>LongOrder() " % (d_BidPrice, d_BidPrice,d_profit,d_TopPrice,d_BottomPrice, d_profit,d_LONG1st)
                # d_BottomPrice = d_CurrentPrice
                # LONG Price保存
                d_BidPrice = d_CurrentPrice
                d_profit = 0
                t_BidTime = datetime.datetime.now().time()                           #global変数に保存
                s_BidTime = t_BidTime.strftime("%H:%M:%S:f")
                # s_dsp = " %sLONG %s, %s, (Diff:%d>=LONG1st:%d and Bid:%d==0), LONGEVENT:%d,LONG0:%d,LONG2nd:%d,LONG3rd:%d " % (s_Tab, s_Time,s_BidTime, d_Diff, d_LONG1st, d_BidPrice, d_LONGEVENT,d_LONG0,d_LONG2nd,d_LONG3rd)
                s_dsp = "220,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')

                #-----LONG発注 -------------------------------
                if(ws != None and message != None):
                    LongOrder(ws, message, Symbol_Issue)
                    t_now = datetime.datetime.now().time()
                    s_Time = t_now.strftime("%H:%M:%S:%f")
                    s_dsp = "221%sLONG %s, %s, LongOrder(), (LONGEVENT:%d, LONG0:%d, LONG1st:%d, LONG2nd:%d, LONG3rd:%d) " % (s_Tab, s_Time,s_BidTime, d_LONGEVENT, d_LONG0, d_LONG1st, d_LONG2nd, d_LONG3rd)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    checkSt = KABUPOSI.kabu_positions.APIPosition.check_position(Symbol_Issue, side='2')
                    if(checkSt == 0):
                        d_BidPrice = 0
                        d_profit = 0
                        # d_BottomPrice = d_CurrentPrice
                        # print("----- 一時的にBitPriceを設定　for simulation -----")
                        # s_dsp = "222%sLONG %s, %s, 0=check_position(), Cur:%6d,Bid[%6d], Btm:%6d, Losscut:%6d, Target:%6d) " % (s_Tab, s_Time,s_BidTime, d_CurrentPrice, d_BidPrice, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        # s_dsp = "122LONG %s, %s, %6d,[%6d],<%d>,(24)0=check_position(),  Btm:%6d,Losscut:%6d,  Target:%6d) " % (s_Time,s_BidTime, d_LastValue,d_BidPrice,d_profit, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        s_dsp = "222 LONG NG,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                        print(s_dsp)
                        if(f_write):
                            writeCsvfile.write(s_dsp + '\n')
                    else:
                        d_BottomPrice = d_LastValue
                        # s_dsp = "223%sLONG %s, %s, %d=check_position(), Cur:%6d,Bid[%6d], Btm:%6d, Losscut:%6d, Target:%6d) " % (s_Tab, s_Time,s_BidTime, checkSt, d_CurrentPrice, d_BidPrice, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        # s_dsp = "123%s, %s,%6d,[%6d],<%d>,(24)%d=check_position(),  Btm:%6d,Losscut:%6d,  Target:%6d) " % (s_Time,s_BidTime, d_LastValue,d_BidPrice,d_profit, checkSt, d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                        s_dsp = "223 LONG,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                        print(s_dsp)
                        if(f_write):
                            writeCsvfile.write(s_dsp + '\n')

                        #     # キャンセルからの損切り注文
                        #     cancelorder.cancelorder()
                        #     if(d_BidPrice >= d_LastValue):
                        #     ##s_dsp = "%s, %s,%6d,[%6d],<%d>,(8)>> Bottom:%6d >= Current:%6d" % (t_now.strftime("%H:%M:%S"), t_BidTime("%H:%M:%S"), d_LastValue,t_BidTime, d_BidPrice, d_BottomPrice, d_LastValue)
                        #     d_BottomPrice = d_LastValue
                        #     ##print(s_dsp)
                #--------------------------------------------------------------
            d_LastValue = d_CurrentPrice
            # s_dsp = "229%s(%s),Cur:%d, L:%d,(%d),     LONG:%5d,(%d)     Top:%5d,  Btm:%5d, LossC:%5d, Target:%5d) " % (s_Tab, Symbol_Issue, d_CurrentPrice, d_LastValue,d_Diff, d_BidPrice,d_profit, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            s_dsp = "229,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

        # Position有り
        else:       #if(d_BidPrice > 0):
            # UP    (Top < message."CurrentPrice")
            if(d_TopPrice < d_CurrentPrice):
                d_TopPrice = d_CurrentPrice

            if(d_BottomPrice == 0):
                d_BottomPrice = d_CurrentPrice
            #------------------------------------------------------------------
            #----- TopPrice -----
            # if(d_TopPrice < d_CurrentPrice and d_BottomPrice < d_CurrentPrice):
            #     s_dsp = "3 (Top%d < Cur:%d and Btm:%d < Cur:%6d) " % (d_TopPrice, d_CurrentPrice, d_BottomPrice, d_CurrentPrice)
            #     print(s_dsp)

            if(up_down > 0):
                # s_dsp = "230%sUP(Last:%d < Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                s_dsp = "230 UP,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            elif(up_down < 0):
                # s_dsp = " 231%sDouwn(Last:%d > Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                s_dsp = "231 Down,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            # else:
            #     s_dsp = " %s3P ===== (Last:%d == Cur:%d), Cur:%d, L:%d,(%d), Top:%d,  Btm:%d, LossC:%6d, Target:%6d) " % (s_Tab, d_LastValue, d_CurrentPrice, d_CurrentPrice, d_LastValue,d_Diff, d_TopPrice, d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            # s_dsp = "%s, %s,%6d->%d,[%6d],<%d>,(12),- Symbol:%s -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_Time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
            # print(s_dsp)
            # 損切り価格 Top-Minus
            d_LosscutPrice = d_BidPrice - d_LONGLOSS            # Loss-Cut Transactions (Entry - LossCut)
            d_TargetPrice =  d_TopPrice - d_LONGLOSS            #  ProfitDefault:(Top-LossCut)
            # (Top - LONG3rd)で Profit (優先度:LONG3rd < LONG2nd)
            # if(flagLONG3rd):
            #     d_TargetPrice =  d_TopPrice - d_LONG3rd
            # # (Top - LONG2nd)で Profit (優先度:LONG3rd < LONG2nd)
            # if(flagLONG2nd):
            d_TargetPrice =  d_TopPrice - d_LONG2nd

            # Loss-cut OR ( Profit・強制終了:LONGCLOSE = 1)
            if(d_CurrentPrice <= d_LosscutPrice or d_CurrentPrice < d_BidPrice  or d_LONGCLOSE > 0):
                
                # if(d_profit <= 0):
                s_dsp = "241 LossCut,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
                # else:
                #     s_dsp = "142 Profit,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                #     print(s_dsp)
                #     if(f_write):
                #         writeCsvfile.write(s_dsp + '\n')
                # # return -1
                if(ws != None and message != None):
                    TtradingStop(ws, message)
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                d_BidPrice = 0
                d_profit = 0
                d_TargetPrice = 0
                d_LosscutPrice = 0
                s_dsp = "242 LossCut,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
                
            elif(d_CurrentPrice <= d_TargetPrice):
                # s_dsp = " %s%6d,[%6d],(40),-  Profit(%d) -,Top:%6d,  Btm:%6d,  Losscut:%6d,  Target:%6d) " % (s_Tab, d_LastValue,d_BidPrice,d_profit, d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
                # print(s_dsp)
                s_dsp = "250 Profit,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                d_BidPrice = 0
                d_profit = 0
                d_TargetPrice = 0
                d_LosscutPrice = 0
                # return -1
                if(ws != None and message != None):
                    TtradingStop(ws, message)

                s_dsp = "251 Profit,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                print(s_dsp)
                if(f_write):
                    writeCsvfile.write(s_dsp + '\n')

            else:   #Illigal Check
                if(d_BottomPrice == 0):
                    s_dsp = "260Bottom:0,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    d_BottomPrice = d_CurrentPrice

                if(d_TopPrice == 0):
                    s_dsp = "261Top:0,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                    print(s_dsp)
                    if(f_write):
                        writeCsvfile.write(s_dsp + '\n')
                    d_TopPrice = d_CurrentPrice
                    if(d_TopLast < d_TopPrice):
                        d_TopLast = d_TopPrice
                # s_dsp = "263Partial,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
                # print(s_dsp)
                # if(f_write):
                #     writeCsvfile.write(s_dsp + '\n')

        s_dsp = "290,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        print(s_dsp)
        if(f_write):
            writeCsvfile.write(s_dsp + '\n')
        d_LastValue = d_CurrentPrice
        if(d_TopPrice == 0):
            d_TopPrice = d_CurrentPrice
        if(d_TopLast == 0):
            d_TopLast = d_TopPrice
        #----------------------------------------------------------------------
        #     # キャンセルからの LossCut注文
        #     cancelorder.cancelorder()
        #     ws.close()
    s_dsp = "291,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol_Issue, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')


#----- 株価が変わった場合に呼ばれる関数 ----------------------
def on_message(ws, message):
    global d_CurrentPrice

    # content = json.loads(message)
    # CurrentPrice = content["CurrentPrice"]
    # Symbol = content["Symbol"]         #銘柄
    content = json.loads(message)
    CurrentPrice = content["CurrentPrice"]      # 現値
    Symbol = content["Symbol"]                  # 銘柄
    if not CurrentPrice:
        d_CurrentPrice = 0
    else:
        d_CurrentPrice = int(CurrentPrice)

    s_dsp = "on_message()->,CurrentPrice:%s,Symbol:%s" % (CurrentPrice,Symbol)
    print(s_dsp)
    message2Trace(ws, message, Symbol, writeCsvfile)
    # message2Trace2(ws, message, Symbol, writeCsvfile)
    s_dsp = "<-on_message(),CurrentPrice:%s,Symbol:%s" % (CurrentPrice,Symbol)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')


#----- 株価が変わった場合に呼ばれる関数 ----------------------
def message2Trace2(ws, message, Symbol, writeCsvfile):
    global Password
    global Token
    global Issue 
    global d_CurrentPrice
    global s_Tab
    global s_Tab1
    global s_Tab2
    global s_Tab3
    global PauseTime

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
    #------------------------------------------------------

    global d_TopLast
    global d_TopPrice
    global d_BottomPrice
    global d_LosscutPrice
    global d_TargetPrice
    global d_LastValue
    global d_BidPrice
    global t_BidTime

    global d_TopLast1
    global d_TopPrice1
    global d_BottomPrice1
    global d_LosscutPrice1
    global d_TargetPrice1
    global d_LastValue1
    global d_BidPrice1
    global t_BidTime1

    global d_TopLast2
    global d_TopPrice2
    global d_BottomPrice2
    global d_LosscutPrice2
    global d_TargetPrice2
    global d_LastValue2
    global d_BidPrice2
    global t_BidTime2

    global s_CurrentTime
    global f_write
    # global writeCsvfile
    #------------------------------------------------------
    # Get Long Position Setting
    conf = configparser.ConfigParser()
    conf.read('settings.ini')
    LONGEVENT = conf['kabuAPI']['LONGEVENT']
    Issue1 = conf['kabuAPI']['Issue1']
    Issue2 = conf['kabuAPI']['Issue2']
    Issue3 = conf['kabuAPI']['Issue3']
    SimulateID = conf['kabuAPI']['SimulateID']    
    PauseTime = conf['kabuAPI']['PauseTime']

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
    s_Time = t_now.strftime("%H:%M:%S:%f")
    
    s_CurrentTime = t_now.strftime("%H:%M:%S:%f")
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")
    #------------------------------------------------------
    # flagLONG2nd = True
    # if((d_LONGEVENT & 2)==0):
    #     flagLONG2nd = False
    # if(d_LONG2nd <= 0):
    #     flagLONG2nd = False
    #------------------------------------------------------
    # flagLONG3rd = True
    # if((d_LONGEVENT & 3)==0):
    #     flagLONG3rd = False
    # if(d_LONG3rd <= 0):
    #     flagLONG3rd = False
    #------------------------------------------------------
    # t_now = datetime.datetime.now().time()

    # content = json.loads(message)
    # CurrentPrice = content["CurrentPrice"]
    # Symbol = content["Symbol"]         #銘柄

    # s_dsp = " %s %s(Issue:%s, Issue2:%s)  %s, %s, LONGEVENT:%d, LONG0:%d, LONG1st:%d, LONG2nd:%d, LONG3rd:%d) " % (s_Tab, Symbol, Issue, Issue2, s_Time,s_BidTime,d_LONGEVENT,d_LONG0,d_LONG1st,d_LONG2nd,d_LONG3rd)
    # print(s_dsp)

    # if not CurrentPrice:
    #     d_CurrentPrice = 0
    # else:
    #     d_CurrentPrice = int(CurrentPrice)

    # pprint.pprint(content)
    d_profit = 0        # int(0)
    if(d_BidPrice > 0):
        d_profit = d_CurrentPrice - d_BidPrice
    d_Diff = 0
    if(d_LastValue == d_CurrentPrice):
        d_Diff = d_LastValue - d_CurrentPrice
    # Check of doing
    # s_dsp = "-110-,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    # print(s_dsp)

    # INIファイルで一時停止 ファイルClose　→　再Open 
    if (PauseTime is not None):
        time = t_now.strftime("%H%M%S")
        if (PauseTime == time):        
            s_dsp = "110----------一時停止----------,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.close()

            s_DateTime = t_now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
            WritefileName = './Result' + s_DateTime + '.csv'
            f_write = False;
            writeCsvfile = open(WritefileName, 'w')     #, newline='')
            if (writeCsvfile):
                f_write = True;

    # s_dsp = " %s0 %s, %s,%6d->%d,[%6d],<%d>, Symbol:%s, Top:%6d, Btm:%6d, Losscut:%6d, Target:%6d) " % (s_Tab, s_Time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
    # s_dsp = " %s0 %s, %s,[%6d],<%d>, Symbol:%s) " % (s_Time,s_BidTime, d_BidPrice, d_profit, Symbol)
    # print(s_dsp)

    if(Symbol == Issue1 or Symbol == Issue2):
        if(Symbol == Issue1):
            s_Tab = s_Tab1
            # LONG0 = conf[Issue1]['LONG0']
            # LONG1st = conf[Issue1]['LONG1st']
            # LONG2nd = conf[Issue1]['LONG2nd']
            # LONG3rd = conf[Issue1]['LONG3rd']
            # LONGLOSS = conf[Issue1]['LONGLOSS']
            # LONGCLOSE = conf[Issue1]['LONGCLOSE']
            # d_LONGEVENT = int(LONGEVENT)
            # d_LONG0 = int(LONG0)
            # d_LONG1st = int(LONG1st)
            # d_LONG2nd = int(LONG2nd)
            # d_LONG3rd = int(LONG3rd)
            # d_LONGLOSS = int(LONGLOSS)
            # d_LONGCLOSE = int(LONGCLOSE)

            d_TopLast       = d_TopLast1
            d_TopPrice      = d_TopPrice1
            d_BottomPrice   = d_BottomPrice1
            d_LosscutPrice  = d_LosscutPrice1
            d_TargetPrice   = d_TargetPrice1
            d_LastValue     = d_LastValue1
            d_BidPrice      = d_BidPrice1
            t_BidTime       = t_BidTime1

            s_dsp = "111Symbol_Price1,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')
            #----- Issue1 Issue2 Issue3 共通処理 ---------------
            # s_dsp = "120 PiwSymbol_Price1,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            # print(s_dsp)
            # if(f_write):
            #     writeCsvfile.write(s_dsp + '\n')

            status = Symbol_Price1(ws, message, Symbol, writeCsvfile)

            s_dsp = "121 %d=Symbol_Price1(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (status, Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            if(status == 1):
                LongOrder(ws, message, Symbol)
            elif(status == -1):
                TtradingStop(ws, message, Symbol)
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                d_BidPrice = 0
                d_TargetPrice = 0
                d_LosscutPrice = 0
                print("----- Reset -----")
            #----- Issue1 Issue2 Issue3 共通処理 ---------------
            #--------------------------------------------------

        if(Symbol == Issue2):
            s_Tab = s_Tab2
            LONG0 = conf[Issue2]['LONG0']
            LONG1st = conf[Issue2]['LONG1st']
            LONG2nd = conf[Issue2]['LONG2nd']
            LONG3rd = conf[Issue2]['LONG3rd']
            LONGLOSS = conf[Issue2]['LONGLOSS']
            LONGCLOSE = conf[Issue2]['LONGCLOSE']
            d_LONGEVENT = int(LONGEVENT)
            d_LONG0 = int(LONG0)
            d_LONG1st = int(LONG1st)
            d_LONG2nd = int(LONG2nd)
            d_LONG3rd = int(LONG3rd)
            d_LONGLOSS = int(LONGLOSS)
            d_LONGCLOSE = int(LONGCLOSE)
            # 銘柄２の状態を取得
            d_TopLast       = d_TopLast2
            d_TopPrice      = d_TopPrice2
            d_BottomPrice   = d_BottomPrice2
            d_LosscutPrice  = d_LosscutPrice2
            d_TargetPrice   = d_TargetPrice2
            d_LastValue     = d_LastValue2
            d_BidPrice      = d_BidPrice2
            t_BidTime       = t_BidTime2
            s_dsp = "112,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            #----- Issue1 Issue2 Issue3 共通処理 ---------------
            s_dsp = "120,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            status = Symbol_Price(ws, message, Symbol, writeCsvfile)

            s_dsp = "121 %d=Symbol_Price(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (status, Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

            if(status == 1):
                LongOrder(ws, message, Symbol)
            elif(status == -1):
                TtradingStop(ws, message, Symbol)
                d_TopPrice = d_CurrentPrice
                d_BottomPrice = d_CurrentPrice
                d_BidPrice = 0
                d_TargetPrice = 0
                d_LosscutPrice = 0
                print("----- Reset -----")
            #----- Issue1 Issue2 Issue3 共通処理 ---------------
            #--------------------------------------------------
        #--------------------------------------------------
        # #----- Issue1 Issue2 Issue3 共通処理 ---------------
        # s_dsp = "120,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        # print(s_dsp)
        # if(f_write):
        #     writeCsvfile.write(s_dsp + '\n')

        # status = Symbol_Price1(ws, message, Symbol, writeCsvfile)

        # s_dsp = "121 %d=Symbol_Price1(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (status, Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        # print(s_dsp)
        # if(f_write):
        #     writeCsvfile.write(s_dsp + '\n')

        # if(status == 1):
        #     LongOrder(ws, message, Symbol)
        # elif(status == -1):
        #     TtradingStop(ws, message, Symbol)
        #     d_TopPrice = d_CurrentPrice
        #     d_BottomPrice = d_CurrentPrice
        #     d_BidPrice = 0
        #     d_TargetPrice = 0
        #     d_LosscutPrice = 0
        #     print("----- Reset -----")
        # #----- Issue1 Issue2 Issue3 共通処理 ---------------
        # #--------------------------------------------------
        # if(Symbol == Issue1):
        #     # 銘柄１の状態を保存
        #     d_TopLast1      = d_TopLast
        #     d_TopPrice1     = d_TopPrice
        #     d_BottomPrice1  = d_BottomPrice
        #     d_LosscutPrice1 = d_LosscutPrice
        #     d_TargetPrice1  = d_TargetPrice
        #     d_LastValue1    = d_LastValue
        #     d_BidPrice1     = d_BidPrice
        #     t_BidTime1      = t_BidTime
        #     s_dsp = "122 %d=Symbol_Price(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice1, d_profit, d_TopLast1, d_TopPrice1, d_BottomPrice1, d_LosscutPrice1, d_TargetPrice1)
        #     print(s_dsp)
        #     if(f_write):
        #         writeCsvfile.write(s_dsp + '\n')
        #     # return
        # if(Symbol == Issue2):
        #     # 銘柄２の状態を保存
        #     d_TopLast2      = d_TopLast
        #     d_TopPrice2     = d_TopPrice
        #     d_BottomPrice2  = d_BottomPrice
        #     d_LosscutPrice2 = d_LosscutPrice
        #     d_TargetPrice2  = d_TargetPrice
        #     d_LastValue2    = d_LastValue
        #     d_BidPrice2     = d_BidPrice
        #     t_BidTime2      = t_BidTime
        #     s_dsp = "123 %d=Symbol_Price(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice2, d_profit, d_TopLast2, d_TopPrice2, d_BottomPrice2, d_LosscutPrice2, d_TargetPrice2)
        #     print(s_dsp)
        #     if(f_write):
        #         writeCsvfile.write(s_dsp + '\n')
        #     # return

        d_LastValue = d_CurrentPrice
        if(d_TopPrice == 0):
            d_TopPrice = d_CurrentPrice
        if(d_TopLast == 0):
            d_TopLast = d_TopPrice
        #----------------------------------------------------------------------
                #     # キャンセルからの LossCut注文
                #     cancelorder.cancelorder()
                #     ws.close()
        # s_dsp = "Symbol:%s<-%d, Crt:%d, Bid[%6d], profit<%d>, LastTop:%d, Top:%d, Btm:%d) " % (Symbol, d_LastValue, d_CurrentPrice, d_BidPrice, d_profit, d_TopLast, d_TopPrice, d_BottomPrice)
        # print(s_dsp)
        s_dsp = "129,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        print(s_dsp)
        if(f_write):
            writeCsvfile.write(s_dsp + '\n')
#--- on_message -------------------------------------------------------


#----- 株価が変わった場合に呼ばれる関数 ----------------------
def message2Trace(ws, message, Symbol, writeCsvfile):

    # Symbol = Symbol_Issue

    global Password
    global Token
    global Issue 
    global d_CurrentPrice
    global s_Tab
    global s_Tab1
    global s_Tab2
    global s_Tab3
    global PauseTime

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
    #------------------------------------------------------
    global d_TopLast1
    global d_TopPrice1
    global d_BottomPrice1
    global d_LosscutPrice1
    global d_TargetPrice1
    global d_LastValue1
    global d_BidPrice1
    global t_BidTime1

    global d_TopLast2
    global d_TopPrice2
    global d_BottomPrice2
    global d_LosscutPrice2
    global d_TargetPrice2
    global d_LastValue2
    global d_BidPrice2
    global t_BidTime2

    global s_CurrentTime
    global f_write
    # global writeCsvfile
    #------------------------------------------------------
    # Get Long Position Setting
    conf = configparser.ConfigParser()
    conf.read('settings.ini')
    LONGEVENT = conf['kabuAPI']['LONGEVENT']
    Issue1 = conf['kabuAPI']['Issue1']
    Issue2 = conf['kabuAPI']['Issue2']
    Issue3 = conf['kabuAPI']['Issue3']
    SimulateID = conf['kabuAPI']['SimulateID']
    PauseTime = conf['kabuAPI']['PauseTime']

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
    d_SimulateID = int(SimulateID)

    #----------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_Time = t_now.strftime("%H:%M:%S:%f")
    
    s_CurrentTime = t_now.strftime("%H:%M:%S:%f")
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")
    #------------------------------------------------------
    # flagLONG2nd = True
    # if((d_LONGEVENT & 2)==0):
    #     flagLONG2nd = False
    # if(d_LONG2nd <= 0):
    #     flagLONG2nd = False
    #------------------------------------------------------
    # flagLONG3rd = True
    # if((d_LONGEVENT & 3)==0):
    #     flagLONG3rd = False
    # if(d_LONG3rd <= 0):
    #     flagLONG3rd = False
    #------------------------------------------------------
    # t_now = datetime.datetime.now().time()

    # content = json.loads(message)
    # CurrentPrice = content["CurrentPrice"]
    # Symbol = content["Symbol"]         #銘柄

    # s_dsp = " %s %s(Issue:%s, Issue2:%s)  %s, %s, LONGEVENT:%d, LONG0:%d, LONG1st:%d, LONG2nd:%d, LONG3rd:%d) " % (s_Tab, Symbol, Issue, Issue2, s_Time,s_BidTime,d_LONGEVENT,d_LONG0,d_LONG1st,d_LONG2nd,d_LONG3rd)
    # print(s_dsp)

    # if not CurrentPrice:
    #     d_CurrentPrice = 0
    # else:
    #     d_CurrentPrice = int(CurrentPrice)

    # pprint.pprint(content)
    d_profit = 0        # int(0)
    if(d_BidPrice > 0):
        d_profit = d_CurrentPrice - d_BidPrice
    d_Diff = 0
    if(d_LastValue == d_CurrentPrice):
        d_Diff = d_LastValue - d_CurrentPrice
    # Check of doing
    # s_dsp = "-110-,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    # print(s_dsp)

    # INIファイルで一時停止 ファイルClose　→　再Open 
    if (PauseTime is not None):
        time = t_now.strftime("%H%M%S")
        if (PauseTime == time):        
            s_dsp = "110一時停止,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.close()

            s_DateTime = t_now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
            WritefileName = './Result' + s_DateTime + '.csv'
            f_write = False;
            writeCsvfile = open(WritefileName, 'w')     #, newline='')
            if (writeCsvfile):
                f_write = True;

    # s_dsp = " %s0 %s, %s,%6d->%d,[%6d],<%d>, Symbol:%s, Top:%6d, Btm:%6d, Losscut:%6d, Target:%6d) " % (s_Tab, s_Time,s_BidTime, d_LastValue,d_CurrentPrice, d_BidPrice,d_profit, Symbol,d_TopPrice,d_BottomPrice,d_LosscutPrice,d_TargetPrice)
    # s_dsp = " %s0 %s, %s,[%6d],<%d>, Symbol:%s) " % (s_Time,s_BidTime, d_BidPrice, d_profit, Symbol)
    # print(s_dsp)

    if(Symbol == Issue1 or Symbol == Issue2):
        if(Symbol == Issue1):
            s_Tab = s_Tab1
            LONG0 = conf[Issue1]['LONG0']
            LONG1st = conf[Issue1]['LONG1st']
            LONG2nd = conf[Issue1]['LONG2nd']
            LONG3rd = conf[Issue1]['LONG3rd']
            LONGLOSS = conf[Issue1]['LONGLOSS']
            LONGCLOSE = conf[Issue1]['LONGCLOSE']
            d_LONGEVENT = int(LONGEVENT)
            d_LONG0 = int(LONG0)
            d_LONG1st = int(LONG1st)
            d_LONG2nd = int(LONG2nd)
            d_LONG3rd = int(LONG3rd)
            d_LONGLOSS = int(LONGLOSS)
            d_LONGCLOSE = int(LONGCLOSE)

            d_TopLast       = d_TopLast1
            d_TopPrice      = d_TopPrice1
            d_BottomPrice   = d_BottomPrice1
            d_LosscutPrice  = d_LosscutPrice1
            d_TargetPrice   = d_TargetPrice1
            d_LastValue     = d_LastValue1
            d_BidPrice      = d_BidPrice1
            t_BidTime       = t_BidTime1

            s_dsp = "111,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')

        if(Symbol == Issue2):
            s_Tab = s_Tab2
            LONG0 = conf[Issue2]['LONG0']
            LONG1st = conf[Issue2]['LONG1st']
            LONG2nd = conf[Issue2]['LONG2nd']
            LONG3rd = conf[Issue2]['LONG3rd']
            LONGLOSS = conf[Issue2]['LONGLOSS']
            LONGCLOSE = conf[Issue2]['LONGCLOSE']
            d_LONGEVENT = int(LONGEVENT)
            d_LONG0 = int(LONG0)
            d_LONG1st = int(LONG1st)
            d_LONG2nd = int(LONG2nd)
            d_LONG3rd = int(LONG3rd)
            d_LONGLOSS = int(LONGLOSS)
            d_LONGCLOSE = int(LONGCLOSE)
            # 銘柄２の状態を取得
            d_TopLast       = d_TopLast2
            d_TopPrice      = d_TopPrice2
            d_BottomPrice   = d_BottomPrice2
            d_LosscutPrice  = d_LosscutPrice2
            d_TargetPrice   = d_TargetPrice2
            d_LastValue     = d_LastValue2
            d_BidPrice      = d_BidPrice2
            t_BidTime       = t_BidTime2
            s_dsp = "112,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')
        #--------------------------------------------------
        #----- Issue1 Issue2 Issue3 共通処理 ---------------
        s_dsp = "120,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        print(s_dsp)
        if(f_write):
            writeCsvfile.write(s_dsp + '\n')

        status = Symbol_Price(ws, message, Symbol, writeCsvfile)

        s_dsp = "121 %d=Symbol_Price(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (status, Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        print(s_dsp)
        if(f_write):
            writeCsvfile.write(s_dsp + '\n')

        if(status == 1):
            LongOrder(ws, message, Symbol)
        elif(status == -1):
            TtradingStop(ws, message, Symbol)
            d_TopPrice = d_CurrentPrice
            d_BottomPrice = d_CurrentPrice
            d_BidPrice = 0
            d_TargetPrice = 0
            d_LosscutPrice = 0
            print("----- Reset -----")
        #----- Issue1 Issue2 Issue3 共通処理 ---------------
        #--------------------------------------------------
        if(Symbol == Issue1):
            # 銘柄１の状態を保存
            d_TopLast1      = d_TopLast
            d_TopPrice1     = d_TopPrice
            d_BottomPrice1  = d_BottomPrice
            d_LosscutPrice1 = d_LosscutPrice
            d_TargetPrice1  = d_TargetPrice
            d_LastValue1    = d_LastValue
            d_BidPrice1     = d_BidPrice
            t_BidTime1      = t_BidTime
            s_dsp = "122 %d=Symbol_Price(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice1, d_profit, d_TopLast1, d_TopPrice1, d_BottomPrice1, d_LosscutPrice1, d_TargetPrice1)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')
            # return
        if(Symbol == Issue2):
            # 銘柄２の状態を保存
            d_TopLast2      = d_TopLast
            d_TopPrice2     = d_TopPrice
            d_BottomPrice2  = d_BottomPrice
            d_LosscutPrice2 = d_LosscutPrice
            d_TargetPrice2  = d_TargetPrice
            d_LastValue2    = d_LastValue
            d_BidPrice2     = d_BidPrice
            t_BidTime2      = t_BidTime
            s_dsp = "123 %d=Symbol_Price(),%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice2, d_profit, d_TopLast2, d_TopPrice2, d_BottomPrice2, d_LosscutPrice2, d_TargetPrice2)
            print(s_dsp)
            if(f_write):
                writeCsvfile.write(s_dsp + '\n')
            # return

        d_LastValue = d_CurrentPrice
        if(d_TopPrice == 0):
            d_TopPrice = d_CurrentPrice
        if(d_TopLast == 0):
            d_TopLast = d_TopPrice
        #----------------------------------------------------------------------
                #     # キャンセルからの LossCut注文
                #     cancelorder.cancelorder()
                #     ws.close()
        # s_dsp = "Symbol:%s<-%d, Crt:%d, Bid[%6d], profit<%d>, LastTop:%d, Top:%d, Btm:%d) " % (Symbol, d_LastValue, d_CurrentPrice, d_BidPrice, d_profit, d_TopLast, d_TopPrice, d_BottomPrice)
        # print(s_dsp)
        s_dsp = "129,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time,d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
        print(s_dsp)
        if(f_write):
            writeCsvfile.write(s_dsp + '\n')
#--- on_message -------------------------------------------------------


#----------------------------------------------------------
# ３．注文発注（信用）
# （２）返済（決済順序）
# コマンド：python kabusapi_sendorder_margin_pay_ClosePositionOrder.pyより
def TtradingStop(ws, message, Symbol):
    global Password
    global Token
    global Issue 
    global PauseTime

    global d_LONGEVENT
    global d_LONG0
    global d_LONG1st
    global d_LONG2nd
    global d_LONG3rd
    global d_LONGLOSS
    global d_LONGCLOSE
    # Use Sub Module --------------------------------------
    global d_TopLast
    global d_TopPrice
    global d_BottomPrice
    global d_LosscutPrice
    global d_TargetPrice
    global d_LastValue
    global d_BidPrice
    global t_BidTime
    #------------------------------------------------------

    global t_now
    global t_BidTime
    
    global s_CurrentTime
    global f_write
    global writeCsvfile
    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_Time = t_now.strftime("%H:%M:%S:%f")
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")

    t_SellTime = t_now
    s_SellTime = t_now.strftime("%H:%M:%S:%f")
    s_dsp = " TtradingStop() --- %s, BidTime:%s, SellTime:%s" % (s_Time, s_BidTime, s_SellTime)
    print(s_dsp)

    d_profit = 0
    s_dsp = "800返済,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')

    #------------------------------------------------------

    # 成行で終了
    obj = { 'Password': Password,
        'Symbol': Symbol,            #銘柄
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
    s_Time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(101),----- TtradingStop -----" % (s_Time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------

    if(ws is not None and message is not None):
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

            s_dsp = "Symbol:%-6d:" % (Symbol)
            ##print(s_dsp)

        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
        except Exception as e:
            print(e)
    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_Time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(102),----- TtradingStop -----" % (s_Time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------


#----------------------------------------------------------
# ３．注文発注（信用）
# （１）新規
# コマンド：python kabusapi_sendorder_margin_new.py     kabusapi_sendorder_margin_new.pyより
def LongOrder(ws, message, Symbol):
    global Password
    global Token
    global s_CurrentTime 
    global PauseTime
    global LONGEVENT
    global LONG0
    global LONG1st
    global LONG2nd
    global LONG3rd
    global LONGLOSS
    global d_SimulateID

    # Use Sub Module --------------------------------------
    global d_LastValue
    global d_BidPrice
    #------------------------------------------------------

    global s_BidPrice
    global t_now
    global t_BidTime
    global f_write
    global writeCsvfile
   #------------------------------------------------------
    BidPrice = str(d_BidPrice)
    #------------------------------------------------------
    global t_now
    global t_BidTime
    # global t_SellTime

    t_now = datetime.datetime.now().time()
    s_Time = t_now.strftime("%H:%M:%S:%f")

    t_BidTime = t_now
    s_BidTime = t_BidTime.strftime("%H:%M:%S:%f")
    s_SellTime = t_now.strftime("%H:%M:%S:%f")
    s_dsp = " LongOrder --- %s, BidTime:%s, SellTime:%s" % (s_Time, s_BidTime, s_SellTime)
    print(s_dsp)
    
    d_profit = 0
    s_dsp = "800新規,%s,,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (Symbol, s_Time, d_CurrentPrice, d_CurrentPrice-d_LastValue, d_BidPrice, d_profit, d_TopLast, d_TopPrice,  d_BottomPrice, d_LosscutPrice, d_TargetPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')
    #------------------------------------------------------
    obj = { 'Password': Password,   #123456','111111',
        'Symbol': Symbol,        #銘柄          'Symbol': '6521',       #6521：オキサイド
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
    if(ws is not None and message is not None):
        json_data = json.dumps(obj).encode('utf-8')    
    #------------------------------------------------------

    pprint.pprint(json_data)
    s_dsp = "801,%s,%s,,,%d,----- Long Order json_data -----" % (Symbol, s_CurrentTime, d_BidPrice)
    print(s_dsp)
    if(f_write):
        writeCsvfile.write(s_dsp + '\n')

    if(ws is not None and message is not None and d_SimulateID == 0):
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
                s_dsp = "----- Result:%s/OrderId:%s  (BidPrice:%6d,Symbol:%s, d_LastValue:%6d) -----" % (content["Result"], content["OrderId"], BidPrice, Symbol, d_LastValue)
                print(s_dsp)

        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
        except Exception as e:
            print(e)
    else:
        print("%d ----- 発行マスク -----", d_SimulateID)
        
    t_now = datetime.datetime.now().time()
    s_Time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(201),----- LongOrder -----" % (s_Time,s_BidTime, s_SellTime)
    print(s_dsp)
    #------------------------------------------------------
    t_now = datetime.datetime.now().time()
    s_Time = t_now.strftime("%H:%M:%S:%f")
    s_dsp = "%s,BidTime%s,SellTime%s,(201),----- LongOrder -----" % (s_Time,s_BidTime, s_SellTime)
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


