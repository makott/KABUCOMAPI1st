【前提】
・PCにpython3がインストールされていること。
・PUSH配信(websocket)をするには、python3のインストール後にコマンドプロンプトにて以下のコマンドを実行する。
コマンド：

py -m pip install websocket-client

【注意】
「token.py」ファイル名は、pythonで予約とされているため使用できません。

【kabuステAPI実行方法】
コマンドプロンプトから、各コマンドを実行する。
#---------------------------------------------------
#----- 必要に応じて ------
pip install websocket-client

websocket-clientモジュールのインストール
下記コマンドでwebsocket-serverモジュールをインストールします。

$ sudo pip install websocket-client
上記モジュールについて詳しく知りたい方は下記ページを参照してください。
https://github.com/websocket-client/websocket-client

#----- 必要に応じて ------
#---------------------------------------------------

コマンドプロンプトから実行
1 
・PUSH配信(websocket)をする為に、コマンドプロンプトにて以下のコマンドを実行する。
コマンド：py -m pip install websocket-client

2
・Token取得し、カレントディレクトリのINIファイルに書き込む
.\kabusapi_token.py

3
API登録銘柄リストに登録
.\kabusapi_register.py

4
・コマンドログは　kabuSログファイルを確認 --> C:\Users\"ログインユーザー名"\AppData\Roaming\KabuS\Log
