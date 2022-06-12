import urllib.request
import json
import pprint
#----------------------------------------------------------
import configparser

conf = configparser.ConfigParser()
conf.read('./settings.ini')
Token = conf['kabuAPI']['Token']
print('Token:', Token)
#----------------------------------------------------------
obj = { 'Symbols':
        [ 
            # {'Symbol': '6521', 'Exchange': 1},          #6521:オキサイド, 1:東証
            {'Symbol': '2413', 'Exchange': 1}           #2413:エムスリー, 1:東証
            # {'Symbol': '6367', 'Exchange': 1},          #6367:ダイキン, 1:東証
        #    {'Symbol': '7095', 'Exchange': 1},          #6521:マクビープラ, 1:東証     8359:八十二, 1:東証
        ] }
json_data = json.dumps(obj).encode('utf8')

url = 'http://localhost:18080/kabusapi/register'
req = urllib.request.Request(url, json_data, method='PUT')
#req = urllib.request.Request(url, json_data, method='None') error
#req = urllib.request.urlcleanup()
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
except urllib.error.HTTPError as e:
    print(e)
    content = json.loads(e.read())
    pprint.pprint(content)
except Exception as e:
    print(e)
