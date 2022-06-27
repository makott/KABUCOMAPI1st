import sys
import websocket
import _thread
import urllib.request       #kabusapi_sendorder_margin_pay_ClosePositionOrder
import json
import pprint
import datetime
import configparser
# import configparser

#----------------------------------------------------------

# D:\MAKOTOWORK\CaseStudy\PythonCS\kabu_Automatic1.py
import kabu_Automatic1 as kabuAuto
#----------------------------------------------------------
# on_message Module --------------------------------------- 株価が変わった場合に呼ばれる関数
#   Read INI file ----------------------------------------------------------
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

#----------------------------------------------------------
#----- 株価イベントでコールされる関数 ----------------------
def AutomaticShift(ws, message, Symbol, WriteCsvFile):

    kabuAuto.D_BidPrice


#----------------------------------------------------------
#----------------------------------------------------------
#----------------------------------------------------------
