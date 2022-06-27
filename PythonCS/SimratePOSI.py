import pprint
import datetime
import csv
import configparser

# import kabuApi_Long1
import KABUPOSI
#----------------------------------------------------------
t_now = datetime.datetime.now().time()
s_DateTime = t_now.strftime("%H%M%S")  #YYYY-MM-DDTHH:MM:SS
WritefileName = 'Positions' + s_DateTime + '.csv'
# s_Time = s_DateTime

# F_Write = False;
with open(WritefileName, 'w', newline='') as WriteCsvFile:
    # F_Write = True;

    config = configparser.ConfigParser()
    config.read('./KABUPOSI/positions.ini')
    Symbol = config['kabuPOSI']['Symbol']
    Product = config['kabuPOSI']['Product']
    Side = config['kabuPOSI']['Side']
    Token = config['kabuPOSI']['Token']

    s_dsp = "check_position(%s,%s,%s,%s)" % (0, Symbol, Side, Token)
    print(s_dsp)
    WriteCsvFile.write(s_dsp + '\n')

    checkSt = 0
    checkSt = KABUPOSI.kabu_positions.APIPosition.check_position(product='0', symbol=Symbol, side=Side, Token=Token)
    # if(checkSt == 0):
    #     s_dsp = "0 checkSt:%d," % (checkSt)
    #     print(s_dsp)
    # else:
    s_dsp = "checkSt:%d," % (checkSt)
    print(s_dsp)
    WriteCsvFile.write(s_dsp + '\n')

print('----------------------------------------------------------')



# if __name__ == '__main__':
#     SimulatePOSI()