# Import Python ODBC module
import pyodbc
from datetime import datetime
import pandas as pd

def Get_Axtrax_Attendandce(id_axtrax, date_from,date_to):
    server = '192.168.1.1'
    database = 'Axtrax1'
    username = 'sa'
    password = 'a750105530A12345'
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    storedProc = 'SET NOCOUNT ON EXEC	[dbo].[SpAttendaceReport] @listUserId = "' + str(
        id_axtrax) + '", @listReadersId = "1,2", @listOfDays = "1,2,3,4,5,6,7", @autoArrival = 0, @autoExit = 0, @startWorking = "2020-11-09 00:00:00.000", @endWorking = "2020-11-09 23:00:00.000", @overNightOption = 0, @dateFrom = "'+date_from+ '", @dateTo = "'+date_to+'"'
    data = pd.read_sql(storedProc, cnxn)
    in_outs_str =[]
    list_in_out = data[['Entrada','Salida','Fecha']].values.tolist()
    print(list_in_out)
    for item in list_in_out:
        if not (item[0]=='' or item[1]=='' or len(item[1])!=5 or len(item[0])!=5):
            in_outs_str.append('%s %s:00'%(item[2]._short_repr,item[0]))
            in_outs_str.append('%s %s:00'%(item[2]._short_repr,item[1]))
        elif (not item[0]=='') and len(item[0])==5:
            print(item[2]._short_repr)
            in_outs_str.append('%s %s:00'%(item[2]._short_repr,item[0]))
        elif (not item[1]=='') and len(item[1])==5:
            print(item[2]._short_repr)
            in_outs_str.append('%s %s:00'%(item[2]._short_repr,item[1]))            
    if len(in_outs_str)>=2:
        return [in_outs_str[0],in_outs_str[-1]]
    return []