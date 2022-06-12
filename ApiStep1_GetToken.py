import urllib.request
import json
import pprint
import configparser
#----------------------------------------------------------
#----- INIファイルの書き込みで小文字にしない為の関数 -----
def setstr(object):
    return object
    

#----------------------------------------------------------
try:
    #------------------------------------------------------
    conf = configparser.ConfigParser()
    conf.read('./settings.ini')
    APIPassword = conf['kabuAPI']['APIPassword']
    Password = conf['kabuAPI']['Password']
    Token = conf['kabuAPI']['Token']

    LogLevel1 = conf['kabuAPI']['LogLevel1']
    LogLevel2 = conf['kabuAPI']['LogLevel2']
    LogLevel3 = conf['kabuAPI']['LogLevel3']
    LogLevel4 = conf['kabuAPI']['LogLevel4']
    LogLevel5 = conf['kabuAPI']['LogLevel5']

    Issue1 = conf['kabuAPI']['Issue1']
    Issue2 = conf['kabuAPI']['Issue2']
    Issue3 = conf['kabuAPI']['Issue3']

    PauseTime  = conf['kabuAPI']['PauseTime']

    LONG0 = conf['kabuAPI']['LONG0']
    LONG1st = conf['kabuAPI']['LONG1st']
    LONG2nd = conf['kabuAPI']['LONG2nd']
    LONG3rd = conf['kabuAPI']['LONG3rd']
    LONG4th = conf['kabuAPI']['LONG4th']

    LONGLOSS = conf['kabuAPI']['LONGLOSS']
    LONGCLOSE = conf['kabuAPI']['LONGCLOSE']
    FrontOrderType= conf['kabuAPI']['FrontOrderType']

    # LONG01 = conf[Issue1]['LONG0']
    # LONG1st1 = conf[Issue1]['LONG1st']
    # LONG2nd1 = conf[Issue1]['LONG2nd']
    # LONG3rd1 = conf[Issue1]['LONG3rd']
    # LONGLOSS1 = conf[Issue1]['LONGLOSS']
    # LONGCLOSE1 = conf[Issue1]['LONGCLOSE']

    # LONG02 = conf[Issue2]['LONG0']
    # LONG1st2 = conf[Issue2]['LONG1st']
    # LONG2nd2 = conf[Issue2]['LONG2nd']
    # LONG3rd2 = conf[Issue2]['LONG3rd']
    # LONGLOSS2 = conf[Issue2]['LONGLOSS']
    # LONGCLOSE2 = conf[Issue2]['LONGCLOSE']

    conf.optionxform = setstr
    print('APIPassword:', APIPassword)
    print('Password:', Password)
    print('Token:', Token)
    # print('Issue:', Issue)
    print('Issue1:', Issue1)
    print('Issue2:', Issue2)
    print('Issue3:', Issue3)

    print('PauseTime:', PauseTime)

    print('LONG0:', LONG0)
    print('LONG1st:', LONG1st)
    print('LONG2nd:', LONG2nd)
    print('LONG3rd:', LONG3rd)
    print('LONG4th:', LONG4th)

    print('LONGLOSS:', LONGLOSS)
    print('LONGCLOSE:', LONGCLOSE)

    #--------------------------------------------------------
    obj = { 'APIPassword': APIPassword}    #'111111'
    json_data = json.dumps(obj).encode('utf8')

    url = 'http://localhost:18080/kabusapi/token'
    req = urllib.request.Request(url, json_data, method='POST')
    req.add_header('Content-Type', 'application/json')

    with urllib.request.urlopen(req) as res:
        print(res.status, res.reason)
        for header in res.getheaders():
            print(header)
        print()
        content = json.loads(res.read())
        pprint.pprint(content)

        pprint.pprint( content['Token'] )
        Token = content['Token']
        print('content[Token]:', Token)

        pprint.pprint('セクションの情報を変数に格納')       #pprint.pprint()->'付きで出力
        # 空のセクションを作成
        conf['kabuAPI'] = {}
        conf.optionxform = setstr
        # セクションの情報を変数に格納
        section = conf['kabuAPI']
        # セクション内の値の書き換え
        section['APIPassword'] = APIPassword
        section['Password'] = Password
        section['Token'] = Token

        section['LogLevel1'] = LogLevel1
        section['LogLevel2'] = LogLevel2
        section['LogLevel3'] = LogLevel3
        section['LogLevel4'] = LogLevel4
        section['LogLevel5'] = LogLevel5

        section['Issue1'] = Issue1
        section['Issue2'] = Issue2
        section['Issue3'] = Issue3

        section['PauseTime'] = PauseTime

        section['LONG0'] = LONG0
        section['LONG1st'] = LONG1st
        section['LONG2nd'] = LONG2nd
        section['LONG3rd'] = LONG3rd
        section['LONG4th'] = LONG4th
        
        section['LONGLOSS'] = LONGLOSS
        section['LONGCLOSE'] = LONGCLOSE
        section['FrontOrderType'] = FrontOrderType
        

        # section = conf[Issue1]
        # section['LONG0'] = LONG01
        # section['LONG1st'] = LONG1st1
        # section['LONG2nd'] = LONG2nd1
        # section['LONG3rd'] = LONG3rd1
        # section['LONGLOSS'] = LONGLOSS1
        # section['LONGCLOSE'] = LONGCLOSE1

        # section = conf[Issue2]
        # section['LONG0'] = LONG02
        # section['LONG1st'] = LONG1st2
        # section['LONG2nd'] = LONG2nd2
        # section['LONG3rd'] = LONG3rd2
        # section['LONGLOSS'] = LONGLOSS2
        # section['LONGCLOSE'] = LONGCLOSE2

        print('INIファイルの書き込み')                      #print()->'無しで出力
        # INIファイルの生成・書き込み # 書き込みモードでオープン
        with open('settings.ini', 'w') as configfile:
            conf.optionxform = setstr
            conf.write(configfile)        # 指定したconfigファイルを書き込み

        # ApiSettings .whiteToken(Token)

except urllib.error.HTTPError as e:
    print(e)
    content = json.loads(e.read())
    pprint.pprint(content)
except Exception as e:
    print(e)
