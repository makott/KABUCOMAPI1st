from os import stat_result
import urllib.request
import json
import pprint
import datetime

#----------------------------------------------------------

import configparser
# from time import sleep
import time

def Check_Order(Symbol='', OrderID='', UpdateTime='', Token=''):

    s_dsp = "700 Check_Order(%s,%s,%s,%s)" % (Symbol, OrderID, UpdateTime, Token)
    print(s_dsp)
    # if(F_Write):
    #     WriteCsvFile.write(s_dsp + '\n')

    url = 'http://localhost:18080/kabusapi/orders'
    # params = { 'product': 0 }               # product - 0:すべて、1:現物、2:信用、3:先物、4:OP
    #params['id'] = '20201207A02N04830518' # id='xxxxxxxxxxxxxxxxxxxx'
    #params['updtime'] = 20201101123456    # updtime=yyyyMMddHHmmss
    #params['details'] =  'false'          # details='true'/'false'
    #params['symbol'] = '9433'             # symbol='xxxx'
    #params['state'] = 5                   # state - 1:待機（発注待機）、2:処理中（発注送信中）、3:処理済（発注済・訂正済）、4:訂正取消送信中、5:終了（発注エラー・取消済・全約定・失効・期限切れ）
    #params['side'] = '2'                  # side - '1':売、'2':買
    #params['cashmargin'] = 3              # cashmargin - 2:新規、3:返済

    params = { 'product': 2 }               # product - 0:すべて、1:現物、2:信用、3:先物、4:OP
    params['id'] = OrderID                  # id='xxxxxxxxxxxxxxxxxxxx'   注文番号
    params['updtime'] = UpdateTime          # updtime=yyyyMMddHHmmss
    params['details'] = 'true'              # details='true'/'false'
    params['symbol'] = Symbol               # symbol='xxxx'
    # params['state'] = 5                     # state - 1:待機（発注待機）、2:処理中（発注送信中）、3:処理済（発注済・訂正済）、4:訂正取消送信中、5:終了（発注エラー・取消済・全約定・失効・期限切れ）
    params['state'] = 3     # 3:処理済（発注済・訂正済）# state - 1:待機（発注待機）、2:処理中（発注送信中）、3:処理済（発注済・訂正済）、4:訂正取消送信中、5:終了（発注エラー・取消済・全約定・失効・期限切れ）
    params['side'] = '2'                    # side - '1':売、'2':買
    params['cashmargin'] = 2                # cashmargin - 2:新規、3:返済

    req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
    req.add_header('Content-Type', 'application/json')
    req.add_header('X-API-KEY', Token) # '37b96984a496419ebc2abcffa29728d4')
    state = 0
    try:
        print('701 --------------------------------')
        pprint.pprint(params)
        print('--------------------------------')

        with urllib.request.urlopen(req) as res:
            print(res.status, res.reason)
            for header in res.getheaders():
                print(header)
            print()
            content = json.loads(res.read())
            pprint.pprint(content)

            ResponsesParams = content[0]
            state = ResponsesParams['state']

        if(state == 2):  #1:待機（発注待機）,2:処理中（発注送信中）,3:処理済（発注済・訂正済）,4:訂正取消送信中,5:終了（発注エラー・取消済・全約定・失効・期限切れ）
            for counter in range(5):
                time.sleep(1)

                with urllib.request.urlopen(req) as res:
                    print(res.status, res.reason)
                    for header in res.getheaders():
                        print(header)
                    print()
                    content = json.loads(res.read())
                    pprint.pprint(content)
                    ResponsesParams = content[0]
                    state = ResponsesParams['state']

                if(state == 3 or state == 5): #1:待機（発注待機）,2:処理中（発注送信中）,3:処理済（発注済・訂正済）,4:訂正取消送信中,5:終了（発注エラー・取消済・全約定・失効・期限切れ）
                    break

        print(counter)  # 0、1、2、3、4を順次出力
    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        pprint.pprint(content)
    except Exception as e:
        print(e)

    return state



if __name__ == "__main__":
    # global Issue1
    conf = configparser.ConfigParser()          # ConfigParserクラスをインスタンス化
    conf.read('./settings.ini')                 # INIファイルの読み込み
    # conf.read('../TradeSymbol.ini')           # INIファイルの読み込み

    s_token = conf['kabuAPI']['Token']
    Issue1 = conf['kabuAPI']['Issue1']
    # Issue1 = '4641'   #for test

    # %d	10進数で月の始めから何日目かを表示。
    # %y	10進数で上2桁のない西暦年を表示。
    # %Y	10進数で上2桁が付いている西暦年を表示。
    # %m	10進数で月を表示。
    # &S	10進数で秒を表示。
    # %H	10進数で24時間計での時を表示。
    # %I	10進数で12時間計での時を表示。
    # %m	10進数で月を表示。
    # %M	10進数で分を表示。
    now = datetime.datetime.now()
    s_Updtime = now.strftime("%Y%m%d%I%M%S")      # yyyyMMddHHmmss

    s_Price = Check_Order(Symbol=Issue1, OrderID='', UpdateTime=s_Updtime, Token=s_token)      #side:1:売、2:買, product - 0:すべて

    s_dsp = "%s = check_position(%s)" % (s_Price, Issue1)
    print(s_dsp)

