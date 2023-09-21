# Import Python ODBC module
import pyodbc
import pandas as pd

def Get_Axtrax_Attendandce(id_axtrax, fecha):
    # print(id_axtrax)
    # print(fecha)
    # "2020-10-11 00:00:00.000", @dateTo = "2020-10-11 23:59:00.000"'
    server = '192.168.1.1'
    database = 'Axtrax1'
    username = 'sa'
    password = 'a750105530A12345'
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()

    # Execute stored procedure
    storedProc = 'SET NOCOUNT ON EXEC	[dbo].[SpAttendaceReport] @listUserId = "' + str(
        id_axtrax) + '", @listReadersId = "1,2", @listOfDays = "1,2,3,4,5,6,7", @autoArrival = 0, @autoExit = 0, @startWorking = "2020-11-09 07:00:00.000", @endWorking = "2020-11-09 17:00:00.000", @overNightOption = 0, @dateFrom = "' + fecha + ' 00:00:00.000", @dateTo = "' + fecha + ' 23:59:00.000"'
    # print(storedProc)
    data = pd.read_sql(storedProc, cnxn)
    print(data)    
    dias_con_falta = []
    if data.empty:
        query = "SELECT (CASE DATENAME(dw,'" + fecha + " 00:00:00.000') when 'Monday' then 'Lunes' when 'Tuesday' then 'Martes' when 'Wednesday' then 'Miércoles' when 'Thursday' then 'Jueves' when 'Friday' then 'Viernes' when 'Saturday' then 'Sábado' when 'Sunday' then 'Domingo' END) as Dia"
        # print(query)
        cursor.execute(query)
        for item in cursor:
            # print('No vino el prro'+str(item))
            if (item.Dia == 'Sábado') or (item.Dia == 'Domingo'):

                return ['00:00', '00:00', '00', 0, 0]
            else:
                # print('No es fin de semana')
                dias_con_falta.append(item.Dia)
    falta = len(dias_con_falta)


    entrada = '00:00'
    salida = '00:00'


    conta=0
    for em in data.Entrada.values:

        if data.Entrada.values[conta] !='':
            entrada=data.Entrada.values[conta]
            print(entrada)
            break
        conta = conta + 1
    conta_inv=len(data.Salida.values)
    for out in reversed(data.Salida.values):
        if data.Salida.values[conta_inv-1]:
            salida=data.Salida.values[conta_inv-1]
            print(salida)
            break
        conta_inv=conta_inv-1


    horas_array = []
    minutos_array = []
    for item in data['Tiempo Total']:
        horas_array.append(int(item.split(":")[0]))
        minutos_array.append(int(item.split(":")[1]))
    horas_totales = sum(horas_array) + ((sum(minutos_array) * 1) / 60)

    total_retardos = 0
    data_lunes_a_viernes=data[(data.Día != 'Domingo') & (data.Día != 'Sabado')]

    for item in data_lunes_a_viernes['Entrada']:
        o=item
        d = int(item.split(":")[0])
        o = int(item.split(":")[1])
        if d >= 7 and o > 5:
            total_retardos = total_retardos + 1
        break

    # print('Hora de entrada\t'+str(entrada))
    # print('Hora de salida\t'+str(salida))
    # print('Horas Efectivas\t'+str(horas_totales))
    # print('Retardo\t'+str(total_retardos))
    # print('Falta\t'+str(falta))
    return [entrada, salida, horas_totales, total_retardos, falta]

#print(Get_Axtrax_Attendandce(89,'2020-10-19'))
