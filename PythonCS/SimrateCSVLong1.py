# import sys
# import websocket
# import _thread
# import urllib.request       #kabusapi_sendorder_margin_pay_ClosePositionOrder
# import json
import pprint
import datetime
import csv
# import LongPosition
# import kabuApi_ WebsocketLong
# from kabuApi_ WebsocketLong import kabuApi_Long1
# from kabuApi_Long1 import Long_Symbol1

import kabuApi_Long1 as kabuLong
# import kabu_LongShort

#----------------------------------------------------------
import configparser

# APIPassword = conf['kabuAPI']['APIPassword']
# Password = conf['kabuAPI']['Password']
# Token = conf['kabuAPI']['Token']
# Issue2 = conf['kabuAPI']['Issue2']
# Issue3 = conf['kabuAPI']['Issue3']

# LONGEVENT = conf['kabuAPI']['LONGEVENT']
# LONG0 = conf['kabuAPI']['LONG0']
# LONGst = conf['kabuAPI']['LONGst']
# LONG2nd = conf['kabuAPI']['LONG2nd']
# LONG3rd = conf['kabuAPI']['LONG3rd']
# LONGLOSS = conf['kabuAPI']['LONGLOSS']
# LONGCLOSE = conf['kabuAPI']['LONGCLOSE']
#------------------------------------------------------------------------------
# d_TopLast = int(0)
# d_TopPrice = int(0)
# d_BottomPrice = int(0)
# d_LosscutPrice = int(0)
# d_TargetPrice = int(0)
# d_LastValue = int(0)
# d_BidPrice = int(0)

t_now = datetime.datetime.now().time()
s_DateTime = t_now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
WritefileName = './Result' + s_DateTime + '.csv'
s_Time = s_DateTime

F_Write = False;
with open(WritefileName, 'w', newline='') as WriteCsvFile:
    F_Write = True;
#No,Symbol,        ,       , Current, Last-Current, Bid, Current-Bid, LastTop, Top,  Bottom, LossCut, TargetPrice
#No,        ,Symbol2,       , Current, Last-Current, Bid, Current-Bid, LastTop, Top,  Bottom, LossCut, TargetPrice
#No,        ,       ,Symbol3, Current, Last-Current, Bid, Current-Bid, LastTop, Top,  Bottom, LossCut, TargetPrice

Stadalone = 1
#----------------------------------------------------------
def SimulateRead():

    # global d_TopLast
    # global d_TopPrice
    # global d_BottomPrice
    # global d_LosscutPrice
    # global d_TargetPrice
    # global d_LastValue
    # global d_BidPrice
    # global t_now

    # global Issue1
    conf = configparser.ConfigParser()
    conf.read('./settings.ini')
    Symbol = conf['kabuAPI']['Issue1']

    fileName = './' + Symbol + '.csv'
    print ( fileName )
    if(F_Write):
        WriteCsvFile.write(fileName + '\n')

    kabuLong.F_Write = F_Write
    # kabu_LongShort.F_Write = F_Write

    with open(fileName, newline='') as csvfile:
        reader = csv.reader(csvfile)
        s_dsp = "reader.line_num:%d," % (reader.line_num)
        print(s_dsp)
        if(F_Write):
            WriteCsvFile.write(s_dsp + '\n')

        kabuLong.F_Write = F_Write
        # kabu_LongShort.F_Write = F_Write
        d_Current = 0
        d_count = 0
        for row in reader:
            d_Current = int(row[1])
            kabuLong.D_Current = int(row[1])
            kabuLong.SimulateTime = row[0]
            # kabu_LongShort.D_Current = int(row[1])
            # kabu_LongShort.SimulateTime = row[0]

            s_dsp = "SimulateRead(),%s,,,%s,%d," % (Symbol, row[1], d_Current)
            print(s_dsp)
            if(F_Write):
                WriteCsvFile.write(s_dsp + '\n')

            kabuLong.D_Current = d_Current
            kabuLong.Long_Symbol1(None, None, Symbol, WriteCsvFile)
            # kabu_LongShort.D_Current = d_Current
            # kabu_LongShort.Long_Symbol1(None, None, Symbol, WriteCsvFile)
            d_count += 1

        # END for row in reader:
    # END with open(fileName, newline='') as csvfile:
    print('----------------------------------------------------------')



if __name__ == '__main__':
    if(F_Write):
        with open(WritefileName, 'w', encoding='shift_jis') as WriteCsvFile:
            kabuLong.WriteCsvFile = WriteCsvFile
            # kabu_LongShort.WriteCsvFile = WriteCsvFile

            SimulateRead()
    else:
        SimulateRead()
