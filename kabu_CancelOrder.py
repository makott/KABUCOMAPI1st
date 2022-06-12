import urllib.request
import json
import pprint


# obj = { 'OrderID': '20200709A02N04712032', 'Password': '123456' }
# json_data = json.dumps(obj).encode('utf8')

# url = 'http://localhost:18080/kabusapi/cancelorder'
# req = urllib.request.Request(url, json_data, method='PUT')
# req.add_header('Content-Type', 'application/json')
# req.add_header('X-API-KEY', 'ed94b0d34f9441c3931621e55230e402')

# try:
#     with urllib.request.urlopen(req) as res:
#         print(res.status, res.reason)
#         for header in res.getheaders():
#             print(header)
#         print()
#         content = json.loads(res.read())
#         pprint.pprint(content)
# except urllib.error.HTTPError as e:
#     print(e)
#     content = json.loads(e.read())
#     pprint.pprint(content)
# except Exception as e:
#     print(e)
#----------------------------------------------------------
import configparser
from time import sleep
 
#----------------------------------------------------------
class APICancel :
    #----- 株価が変わった場合に呼ばれる関数 ----------------------
    def cancel_position(Password='', OrderID='2', Token=''):
        # global Token

        d_return_code = int(0)
        #----- Check Argument -----
        # if (OrderID == ''):
        #     print('引数error : OrderIDがNULL check_position()')
        #     return 0;

        # obj = { 'OrderID': '20200709A02N04712032', 'Password': '123456' }
        obj = { 'OrderID': OrderID, 'Password': Password }
        json_data = json.dumps(obj).encode('utf8')

        url = 'http://localhost:18080/kabusapi/cancelorder'
        req = urllib.request.Request(url, json_data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', Token)

        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                print()
                content = json.loads(res.read())
                pprint.pprint(content)

                print('1 ----------------------------------------')
                return 1

        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            pprint.pprint(content)
            return 0

        except Exception as e:
            print(e)
            return 0

        return 0
        # url = 'http://localhost:18080/kabusapi/positions'
        # if(product == '0'):
        #     params = { 'product': 0 }   	# product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        # elif(product == '1'):
        #     params = { 'product': 1 }   	# product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        # elif(product == '2'):
        #     params = { 'product': 2 }   	# product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        # else:
        #     print('Illegal argument : product', product)
        #     return
        # params['symbol'] = symbol  		# symbol='xxxx'
        # params['side'] = s_side			# 1:売、2:買
        # params['addinfo'] = 'false' 	# true:追加情報を出力する、false:追加情報を出力しない　※追加情報は、「現在値」、「評価金額」、「評価損益額」、「評価損益率」を意味します
        # req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
        # req.add_header('Content-Type', 'application/json')
        # req.add_header('X-API-KEY', Token)

        # try:
        #     with urllib.request.urlopen(req) as res:
        #         print(res.status, res.reason)
        #         for header in res.getheaders():
        #             print(header)
        #         # print()
        #         content = json.loads(res.read())
        #         pprint.pprint(content)
        #         Symbol = content["Symbol"]          #銘柄
        #         if (symbol == ''):
        #             print('無し : SymbolがNULL check_position()')
        #             return 0;
        #         # curPrice = content["CurrentPrice"]
        #         d_return_code = int(1)

        # except urllib.error.HTTPError as e:
        #     print(e)
        #     content = json.loads(e.read())
        #     pprint.pprint(content)
        #     print('1 ----------------------------------------')

        # except Exception as e:
        #     print(e)

        #     print('3 Retry ----------------------------------------')
        #     # Retry ----------------------------------------
        #     sleep(1)
        #     try:
        #         with urllib.request.urlopen(req) as res:
        #             for header in res.getheaders():
        #                 print(header)
        #             content = json.loads(res.read())
        #             pprint.pprint(content)
        #             Symbol = content["Symbol"]          #銘柄
        #             if (symbol == ''):
        #                 print('無し : SymbolがNULL check_position()')
        #                 return 0;
        #             # curPrice = content["CurrentPrice"]
        #             d_return_code = int(1)

        #     except urllib.error.HTTPError as e:
        #         print(e)
        #         content = json.loads(e.read())
        #         pprint.pprint(content)
        #         print('4 ----------------------------------------')

        #     return 0;            
        #     # return 0;

        # print('5 POSI 有り ----------------------------------------')
        # return 1            # d_return_code

if __name__ == "__main__":
    # global Issue1
    conf = configparser.ConfigParser()      # ConfigParserクラスをインスタンス化
    conf.read('./settings.ini')               # INIファイルの読み込み
    # conf.read('../TradeSymbol.ini')               # INIファイルの読み込み
    Password = conf['kabuAPI']['Password']
    s_token = conf['kabuAPI']['Token']
    # Issue1 = conf['kabuAPI']['Issue1']

    d_rtn = APICancel.cancel_position(Password=Password, OrderID='', Token=s_token)      #side:1:売、2:買, product - 0:すべて
    s_dsp = "%d = cancel_position(%s)" % (d_rtn, s_token)
    print(s_dsp)

    # checkSt = KABUCANCEL.kabu_cancel.APICancel.cancel_position(product='0',symbol=Symbol, side='2', Token=Token)
