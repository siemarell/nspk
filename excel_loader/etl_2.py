import pandas as pd
import psycopg2
import id_detect as id

df = pd.ExcelFile("D:\\PROJECTS\\PYTHON_PROJECTS\\NSPK\\dataForLoad2.xlsx")
sheet = df.parse(0)
dbname = 'data'
connection = psycopg2.connect(""" dbname = {} user = postgres host = 192.168.47.54 password = Polymedia10""".format(dbname))
cursor = connection.cursor()

for row in sheet.iterrows():
    val_host = row[1]['Имя хоста']
    if val_host == '!НЕ ЗАДАНО!':
        val_host = 'Не задано'

    val_subsystem = row[1]['Подсистема']
    if val_subsystem == '!НЕ ЗАДАНО!':
        val_subsystem = 'Не задано'

    val_purpose = row[1]['Назначение']
    if val_purpose == '!НЕ ЗАДАНО!':
        val_purpose = 'Не задано'

    val_os = row[1]['ОС']
    if val_os == '!НЕ ЗАДАНО!':
        val_os = 'Не задано'

    val_divisionOwner = row[1]['Подразделение-владелец']
    if val_divisionOwner == '!НЕ ЗАДАНО!':
        val_divisionOwner = 'Не задано'

    val_administrator = row[1]['Администратор']
    if val_administrator == '!НЕ ЗАДАНО!':
        val_administrator = 'Не задано'

    val_date_start = row[1]['Начало']
    val_date_start = str(val_date_start).split()[0]

    val_date_end = row[1]['Окончание']
    val_date_end = str(val_date_end).split()[0]

    val_trigger = row[1]['Триггер']
    if val_trigger == '!НЕ ЗАДАНО!':
        val_trigger = 'Не задано'

    val_downtime = str(row[1]['Конец-Начало'])
    if len(val_downtime.split()) > 1:
        val_downtime = val_downtime.split()[1]
        val_downtime = val_downtime.split(':')
        val_downtime = int(val_downtime[0])*60*60 + int(val_downtime[1])*60 + int(val_downtime[2])
    else:
        val_downtime = val_downtime.split(':')
        val_downtime = int(val_downtime[0])*60*60 + int(val_downtime[1])*60 + int(val_downtime[2])

    val_platformType = row[1]['Тип апп. платформы']
    if val_platformType == '!НЕ ЗАДАНО!':
        val_platformType = 'Не задано'

    val_period = row[1]['В рамках периода?']
    if val_period == '!НЕ ЗАДАНО!':
        val_period = 'Не задано'

    val_time_start = row[1]['Начало']
    val_time_start = str(val_time_start).split()[1]
    val_time_start = val_time_start.split(':')
    val_time_start = int(val_time_start[0])*60 + int(val_time_start[1])

    val_time_close = row[1]['Окончание']
    val_time_close = str(val_time_close).split()[1]
    val_time_close = val_time_close.split(':')
    val_time_close = int(val_time_close[0])*60 + int(val_time_close[1])

    val_source = row[1]['Источник события']

    val_department = row[1]['Департамент/\nУправление']
    if val_department == '!НЕ ЗАДАНО!':
        val_department = 'Не задано'


    id_fact = id.mainid4cubes(cursor,'f_serv_incident')
    id_host = id.detectidhost('d_host','name',val_host,cursor,connection,val_purpose,val_divisionOwner,val_subsystem,val_platformType,val_os,val_administrator)
#    id_subsystem = id.detectid('d_subsystem','name',val_subsystem,cursor,connection)
#    id_purpose = id.detectid('d_purpose','name',val_purpose,cursor,connection)
#    id_os = id.detectid('d_os','name',val_os,cursor,connection)
#    id_divisionOwner = id.detectiddivisionowner('d_division_owner','name',val_divisionOwner,cursor,connection,val_department)
#    id_administrator = id.detectid('d_administrator','name',val_administrator,cursor,connection)
    id_trigger = id.detectidtrigger('d_trigger','source_name',val_trigger,cursor,connection, val_source)
#    id_period = id.detectid('d_period_type','name',val_period,cursor,connection)
#    id_platform_type = id.detectid('d_platform_type','name',val_platformType,cursor,connection)
    id_time_start = id.detectidtime('d_time','id',val_time_start,cursor,connection)
    id_time_close = id.detectidtime('d_time','id',val_time_close,cursor,connection)





    cursor.execute(''' INSERT INTO public."f_serv_incident"(id, event_start_id, id_host,
 id_date_start, id_date_end, id_time_start, id_time_end, id_trigger,
 fact_timedelta, description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);''',(
    id_fact,
    None,
    id_host,
    val_date_start,
    val_date_end,
    id_time_start,
    id_time_close,
    id_trigger,
    val_downtime,
    None,
    ))
    connection.commit()
    id_fact+=1
    print('take!')



connection.close()