# Import Python ODBC module
import pyodbc
from datetime import datetime
import pandas as pd

def Get_Axtrax_Attendandce(id_axtrax, fecha):
    server = '192.168.1.1'
    database = 'Axtrax1'
    username = 'sa'
    password = 'a750105530A12345'
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    storedProc = 'SET NOCOUNT ON EXEC	[dbo].[SpAttendaceReport] @listUserId = "' + str(
        id_axtrax) + '", @listReadersId = "1,2", @listOfDays = "1,2,3,4,5,6,7", @autoArrival = 0, @autoExit = 0, @startWorking = "2020-11-09 07:00:00.000", @endWorking = "2020-11-09 17:00:00.000", @overNightOption = 0, @dateFrom = "' + fecha + ' 00:00:00.000", @dateTo = "' + fecha + ' 23:59:00.000"'
    data = pd.read_sql(storedProc, cnxn)
    axtr_entrada = '00:00'
    axtr_salida = '00:00'   
    entrada = '00:00'
    salida = '00:00'
    conta=0
    for em in data.Entrada.values:

        if data.Entrada.values[conta] !='':
            entrada=data.Entrada.values[conta]
            break
        conta = conta + 1
    conta_inv=len(data.Salida.values)
    for out in reversed(data.Salida.values):
        if data.Salida.values[conta_inv-1]:
            salida=data.Salida.values[conta_inv-1]
            break
        conta_inv=conta_inv-1
    horas_array = []
    minutos_array = []
    for item in data['Tiempo Total']:
        horas_array.append(int(item.split(":")[0]))
        minutos_array.append(int(item.split(":")[1]))
    
    horas_efectivas = float(sum(horas_array) + ((sum(minutos_array) * 1) / 60))
    horas_efectivas = float("{0:.2f}".format(horas_efectivas))

    total_retardos = 0
    error=""
    data_lunes_a_viernes=data
    horas_entrada=0
    minutos_entrada=0
    #print(data_lunes_a_viernes['Entrada'].values)
    for item in data_lunes_a_viernes['Entrada'].values:
        try:
            minutos_entrada=item
            horas_entrada = int(item.split(":")[0])
            minutos_entrada = int(item.split(":")[1])
            if horas_entrada > 7:
                total_retardos = total_retardos + 1

            if horas_entrada >= 7 and minutos_entrada > 5:
                total_retardos = total_retardos + 1
            break
        except:
            error=("Por favor revise las entradas del Empleado con Id de AxtraxNG con el \nId:"+str(id_axtrax) +"ya que la entrada la registra a las"+str(entrada))
            total_retardos = 1
    for itemx in data_lunes_a_viernes['Salida'].values:
        try:
            minutos_salida=itemx
            horas_salida = int(itemx.split(":")[0])
            minutos_salida = int(itemx.split(":")[1])
        except:
            pass
    axtr_entrada=entrada
    axtr_salida=salida
    horas=0.0
    if  float(entrada.split(":")[0]) >0.0 and float(entrada.split(":")[0]) <7.0:
        entrada='07:00'

    if float(entrada.split(":")[0]) ==7.0 and (float(entrada.split(":")[1]) >= 0 and float(entrada.split(":")[1]) <= 5):
        entrada='07:00'

    #Preguntar si a la salida se consideran las +-10 para los que salen a las 17:00
    if float(salida.split(":")[0]) >=17.0:
        if float(salida.split(":")[1]) >= 50 and float(salida.split(":")[1]) <= 60:
            #print(float(salida.split(":")[0]))
            salida= str(int(salida.split(":")[0])+1)+':00'
        if float(salida.split(":")[1]) >= 1 and float(salida.split(":")[1]) <= 49:
            salida= str(int(salida.split(":")[0]))+':00'


    FMT = '%H:%M'
    try:
        horas_de_trabajo = datetime.strptime(salida, FMT) - datetime.strptime(entrada, FMT)
    except:
        return [axtr_entrada, axtr_salida,0,0,0,error]

    horas_checador=str(abs(horas_de_trabajo))
    horas_checador[2].split(":")[0]
    horas=float("{0:.2f}".format(float(horas_checador.split(":")[0])+(float(horas_checador.split(":")[1])/60)))
    return [axtr_entrada, axtr_salida,horas,horas_efectivas, total_retardos,error]

#print(Get_Axtrax_Attendandce(142,'2021-01-18'))




































# # Import Python ODBC module
# import pyodbc
# from datetime import datetime
# import pandas as pd

# def Get_Axtrax_Attendandce(id_axtrax, fecha):
#     # print(id_axtrax)
#     # print(fecha)
#     # "2020-10-11 00:00:00.000", @dateTo = "2020-10-11 23:59:00.000"'
#     server = '192.168.1.1'
#     database = 'Axtrax1'
#     username = 'sa'
#     password = 'a750105530A12345'
#     cnxn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
#     cursor = cnxn.cursor()

#     # Execute stored procedure
#     storedProc = 'SET NOCOUNT ON EXEC	[dbo].[SpAttendaceReport] @listUserId = "' + str(
#         id_axtrax) + '", @listReadersId = "1,2", @listOfDays = "1,2,3,4,5,6,7", @autoArrival = 0, @autoExit = 0, @startWorking = "2020-11-09 07:00:00.000", @endWorking = "2020-11-09 17:00:00.000", @overNightOption = 0, @dateFrom = "' + fecha + ' 00:00:00.000", @dateTo = "' + fecha + ' 23:59:00.000"'
#     # print(storedProc)
#     data = pd.read_sql(storedProc, cnxn)   



#     entrada = '00:00'
#     salida = '00:00'


#     conta=0
#     for em in data.Entrada.values:

#         if data.Entrada.values[conta] !='':
#             entrada=data.Entrada.values[conta]
#             break
#         conta = conta + 1
#     conta_inv=len(data.Salida.values)
#     for out in reversed(data.Salida.values):
#         if data.Salida.values[conta_inv-1]:
#             salida=data.Salida.values[conta_inv-1]
#             break
#         conta_inv=conta_inv-1

# #Entrada y salida correctos


#     horas_array = []
#     minutos_array = []
#     for item in data['Tiempo Total']:
#         horas_array.append(int(item.split(":")[0]))
#         minutos_array.append(int(item.split(":")[1]))
    
#     horas_efectivas = float(sum(horas_array) + ((sum(minutos_array) * 1) / 60))
#     horas_efectivas = float("{0:.2f}".format(horas_efectivas))

#     total_retardos = 0
#     error=""
#     data_lunes_a_viernes=data#data[(data.Día != 'Domingo') & (data.Día != 'Sabado')]
#     #Hora de entrada y salida correctos
#     # print(data_lunes_a_viernes['Entrada'].values)
#     horas_entrada=0
#     minutos_entrada=0
#     #print(data_lunes_a_viernes['Entrada'].values)
#     #Validar cuando no tengan hora de entrada o de salida va a irse a la excepcion
#     for item in data_lunes_a_viernes['Entrada'].values:
#         try:
#             minutos_entrada=item
#             horas_entrada = int(item.split(":")[0])
#             minutos_entrada = int(item.split(":")[1])
#             if horas_entrada > 7:
#                 total_retardos = total_retardos + 1

#             if horas_entrada >= 7 and minutos_entrada > 5:
#                 total_retardos = total_retardos + 1
#             break
#         except:
#             error=("Por favor revise las entradas del Empleado con Id de AxtraxNG con el \nId:"+str(id_axtrax) +"ya que la entrada la registra a las"+str(entrada))
#             total_retardos = 1
#     #print(data_lunes_a_viernes['Salida'].values)
#     for itemx in data_lunes_a_viernes['Salida'].values:
#         try:
#             minutos_salida=itemx
#             horas_salida = int(itemx.split(":")[0])
#             minutos_salida = int(itemx.split(":")[1])
#         except:
#             pass
    
#     # no limitar entrada y salida
#     # si el tiempo total es mayor es de 11 horas o mas se manda a revision si no no y se paga como dia normal
#     # total_de_horas_e_s=horas_salida-horas_entrada

#     # print('Hora de entrada\t'+str(entrada))
#     # print('Hora de salida\t'+str(salida))
#     # print('Horas Efectivas\t'+str(horas_efectivas))
#     # print('Retardo\t'+str(total_retardos))
#     # print('Falta\t'+str(falta))
#     horas=0.0

#     aux_minutos=0


#     FMT = '%H:%M'
#     horas_de_trabajo = datetime.strptime(salida, FMT) - datetime.strptime(entrada, FMT)
#     horas_checador=str(abs(horas_de_trabajo))
#     horas_checador[2].split(":")[0]
#     #print(horas_checador.split(":")[0])
#     #print(horas_checador.split(":")[1])
#     aux_horas=float(horas_checador.split(":")[0])
#     print(horas_checador)

#     aux_minutos=float(horas_checador.split(":")[1]) /60
#     print(aux_minutos)



#     if float(entrada.split(":")[0])<7.0:
#         aux_horas=7.00
#         aux_minutos=0.00
    


    
    

#     try:
#         horas=float("{0:.2f}".format(aux_horas)+(float(aux_minutos)))
#     except:
#         horas=aux_horas+aux_minutos

#     return [entrada, salida,horas,horas_efectivas, total_retardos,error]

# #print(Get_Axtrax_Attendandce(142,'2021-01-18'))
