import urllib.request
import json
import pprint
#----------------------------------------------------------
import configparser
from time import sleep
 
#----------------------------------------------------------
class APIPosition :
    #----- 株価が変わった場合に呼ばれる関数 ----------------------
    def check_position(product='', symbol='', side='2', Token=''):

        Price = ""
        #----- Check Argument -----
        if (symbol == ''):
            print('引数error : SymbolがNULL check_position()')
            return 0;
        s_side = '2'
        if (side == '1' or side == '2'):
            s_side = side

        url = 'http://localhost:18080/kabusapi/positions'
        if(product == '0'):
            params = { 'product': 0 }   	# product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        elif(product == '1'):
            params = { 'product': 1 }   	# product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        elif(product == '2'):
            params = { 'product': 2 }   	# product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        else:
            print('Illegal argument : product', product)
            return
        params['symbol'] = symbol  		# symbol='xxxx'
        params['side'] = s_side			# 1:売、2:買
        params['addinfo'] = 'false' 	# true:追加情報を出力する、false:追加情報を出力しない　※追加情報は、「現在値」、「評価金額」、「評価損益額」、「評価損益率」を意味します
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', Token)

        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                # print()
                content = json.loads(res.read())
                pprint.pprint(content)
                # Symbol = content['Symbol']          # 銘柄
                # Price = content['Price']            # 取得価格
                # s_dsp = "---------- (Symbol:%s, Price:%s) ----------" % (Symbol, Price)
                print('content[0]', content[0])
                params = content[0]
                Price = params['Price']            # 取得価格
                Symbol = params['Symbol']          # 銘柄

                # if (symbol == ''):
                #     print('無し : SymbolがNULL check_position()')
                #     return ''

                # s_dsp = "---------- (Symbol:%s, Price:%s) ----------" % (Symbol, Price)
                # print(s_dsp)

        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
            print('1 ----------------------------------------')
            return ''

        except Exception as e:
            print(e)

            print('3 Retry ----------------------------------------')
            # Retry ----------------------------------------
            sleep(1)
            try:
                with urllib.request.urlopen(req) as res:
                    for header in res.getheaders():
                        print(header)
                    content = json.loads(res.read())
                    pprint.pprint(content)

                    # Symbol = content['Symbol']          # 銘柄
                    # Price = content['Price']            # 取得価格
                    # s_dsp = "---------- (Symbol:%s, Price:%s) ----------" % (Symbol, Price)
                    # print(s_dsp)
                    print('content[0]', content[0])
                    params = content[0]
                    Price = params['Price']            # 取得価格
                    Symbol = params['Symbol']          # 銘柄

                    # if (symbol == ''):
                    #     print('無し : SymbolがNULL check_position()')
                    #     return ''

                    return Price

            except urllib.error.HTTPError as e:
                print(e)
                content = json.loads(e.read())
                pprint.pprint(content)
                print('4 ----------------------------------------')
                return ''

            return Price;

        print('5 POSI 有り ----------------------------------------')
        return Price

if __name__ == "__main__":
    # global Issue1
    conf = configparser.ConfigParser()      # ConfigParserクラスをインスタンス化
    conf.read('./settings.ini')               # INIファイルの読み込み
    # conf.read('../TradeSymbol.ini')               # INIファイルの読み込み

    s_token = conf['kabuAPI']['Token']
    Issue1 = conf['kabuAPI']['Issue1']
    Issue1 = '4641'   #for test

    s_Price = APIPosition.check_position(product='0', symbol=Issue1, side='2', Token=s_token)      #side:1:売、2:買, product - 0:すべて

    s_dsp = "%s = check_position(%s)" % (s_Price, Issue1)
    print(s_dsp)

