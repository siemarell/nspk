import pandas as pd
import psycopg2
import id_detect as id

df = pd.ExcelFile("D:\\PROJECTS\\PYTHON_PROJECTS\\NSPK\\dataForLoadCopy.xlsx")
sheet = df.parse(0)
dbname = 'data'
connection = psycopg2.connect(""" dbname = {} user = postgres host = 192.168.47.54 password = Polymedia10""".format(dbname))
cursor = connection.cursor()

for row in sheet.iterrows():
    val_time_start = row[1]['time_create']
    val_time_start = str(val_time_start).split()[1]
    val_time_start = val_time_start.split(':')
    val_time_start = int(val_time_start[0])*60 + int(val_time_start[1])


    val_time_close = row[1]['time_clear']
    val_time_close = str(val_time_close).split()[1]
    val_time_close = val_time_close.split(':')
    val_time_close = int(val_time_close[0])*60 + int(val_time_close[1])


    val_date_start = row[1]['time_create']
    val_date_start = str(val_date_start).split()[0]

    val_date_close = row[1]['time_clear']
    val_date_close = str(val_date_close).split()[0]

    val_client = row[1]['inc_src_name']
    val_client = str(val_client).split('_')[0]

    val_provider = row[1]['inc_prov1']

    val_rfc = row[1]['RFC']

    val_guilty = row[1]['Виновная организация']

    val_downtime = str(row[1]['Время простоя'])
    if len(val_downtime.split()) > 1:
        val_downtime = val_downtime.split()[1]
        val_downtime = val_downtime.split(':')
        val_downtime = int(val_downtime[0])*60*60 + int(val_downtime[1])*60 + int(val_downtime[2])
    else:
        val_downtime = val_downtime.split(':')
        val_downtime = int(val_downtime[0])*60*60 + int(val_downtime[1])*60 + int(val_downtime[2])

    val_sla = str(row[1]['SLA'])
    if len(val_sla.split())>1:
        val_sla = val_sla.split()[1]
        val_sla = val_sla.split(':')
        val_sla = int(val_sla[0])*60 + int(val_sla[1])
    else:
        val_sla = val_sla.split(':')
        val_sla = int(val_sla[0])*60 + int(val_sla[1])



    id_client = id.detectid('d_client','name',val_client,cursor,connection)
    id_provider = id.detectid('d_provider','name',val_provider,cursor,connection)
    id_rfc = id.detectid('d_rfc','name',val_rfc,cursor,connection)
    id_guilty = id.detectid('d_guilty','name',val_guilty,cursor,connection)
    id_fact = id.mainid4cubes(cursor,'f_channel_connect')
    id_time_start = id.detectidtime('d_time','id',val_time_start,cursor,connection)
    id_time_close = id.detectidtime('d_time','id',val_time_close,cursor,connection)

    cursor.execute(''' INSERT INTO public."f_channel_connect"(id, "id_date_start", "id_date_end", "id_client",
                       "id_provider", "id_rfc", "id_guilty", fact_timedelta,
                       "fact_sla", "id_time_start", "id_time_end") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);''',(
        id_fact,
        val_date_start,
        val_date_close,
        id_client,
        id_provider,
        id_rfc,
        id_guilty,
        val_downtime,
        val_sla,
        val_time_start,
        val_time_close,
    ))
    connection.commit()
    id_fact+=1
    print('take!')



connection.close()