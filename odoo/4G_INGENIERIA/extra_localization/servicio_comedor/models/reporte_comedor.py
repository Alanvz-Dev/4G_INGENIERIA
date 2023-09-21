#!/usr/bin/env python3
import pyodbc
from xmlrpc.client import ServerProxy
import pandas as pd
from datetime import *
from dateutil.relativedelta import relativedelta
from time import time

def Reporte_Comedor(fecha_inicial,fecha_final):
    # print(id_tarjeta)
    # print(fecha_inicial)
    # "2020-10-11 00:00:00.000", @dateTo = "2020-10-11 23:59:00.000"'
    server = '192.168.1.1'
    database = 'ZkTecko2021'
    username = 'sa'
    password = 'a750105530A12345'
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cnxn.cursor()

    # Execute stored procedure
    storedProc = "select * from [dbo].[ReporteComedor]('"+fecha_inicial+"','"+fecha_final+"')"
    print(storedProc)
    # print(storedProc)
    data = pd.read_sql(storedProc, cnxn)
    
    return data
