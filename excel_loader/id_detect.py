def detectid(table_name, column_name, value, cursor, connection):


    cursor.execute("""SELECT "{}".id FROM
                    public."{}" WHERE "{}" = '{}';""".format(table_name,table_name,column_name,value));
    dbresponse = cursor.fetchall()

    if len(dbresponse) == 0:
        cursor.execute("""SELECT max(id) FROM public."{}";""".format(table_name))
        dbresponse = cursor.fetchall()
        if dbresponse[0][0] == None:
            id_cur = 1
        else:
            id_cur = dbresponse[0][0] + 1
        cursor.execute("""INSERT INTO public."{}"(id, "{}") VALUES ({},'{}');""".format(table_name,column_name,id_cur, value))
        connection.commit()
    else:
        id_cur = dbresponse[0][0]

    return id_cur


def mainid(cursor):
    cursor.execute("""SELECT max(id) FROM facts""")
    dbresponse = cursor.fetchall()
    if dbresponse[0][0] != None: id_cur = dbresponse[0][0] + 1
    else: id_cur = 1
    return id_cur

def mainid4cubes(cursor, cube):
    cursor.execute("""SELECT max(id) FROM {}""".format(cube))
    dbresponse = cursor.fetchall()
    if dbresponse[0][0] != None: id_cur = dbresponse[0][0] + 1
    else: id_cur = 1
    return id_cur


def detectidtime(table_name, column_name, value, cursor, connection):


    cursor.execute("""SELECT "{}".id FROM
                    public."{}" WHERE "{}" = '{}';""".format(table_name,table_name,column_name,value));
    dbresponse = cursor.fetchall()

    if len(dbresponse) == 0:
        cursor.execute("""SELECT max(id) FROM public."{}";""".format(table_name))
        dbresponse = cursor.fetchall()
        if dbresponse[0][0] == None:
            id_cur = 1
        else:
            id_cur = dbresponse[0][0] + 1
        cursor.execute("""INSERT INTO public."{}"(id) VALUES ('{}');""".format(table_name,value))
        connection.commit()
    else:
        id_cur = dbresponse[0][0]

    return id_cur

def detectidtrigger(table_name, column_name, value, cursor, connection, source):


    cursor.execute("""SELECT "{}".id FROM
                    public."{}" WHERE "{}" = '{}';""".format(table_name,table_name,column_name,source));
    dbresponse = cursor.fetchall()

    if len(dbresponse) == 0:
        cursor.execute("""SELECT max(id) FROM public."{}";""".format(table_name))
        dbresponse = cursor.fetchall()
        if dbresponse[0][0] == None:
            id_cur = 1
        else:
            id_cur = dbresponse[0][0] + 1
        cursor.execute("""INSERT INTO public."{}"(id, source_name) VALUES ({},'{}');""".format(table_name,id_cur, source))
        connection.commit()
    else:
        id_cur = dbresponse[0][0]

    return id_cur


def detectiddivisionowner(table_name, column_name, value, cursor, connection, department):


    cursor.execute("""SELECT "{}".id FROM
                    public."{}" WHERE "{}" = '{}';""".format(table_name,table_name,column_name,value));
    dbresponse = cursor.fetchall()

    if len(dbresponse) == 0:
        cursor.execute("""SELECT max(id) FROM public."{}";""".format(table_name))
        dbresponse = cursor.fetchall()
        if dbresponse[0][0] == None:
            id_cur = 1
        else:
            id_cur = dbresponse[0][0] + 1
        cursor.execute("""INSERT INTO public."{}"(id, "{}", department) VALUES ({},'{}','{}');""".format(table_name,column_name,id_cur, value, department))
        connection.commit()
    else:
        id_cur = dbresponse[0][0]

    return id_cur

def detectidhost(table_name, column_name, value, cursor, connection,purpose, division_owner, subsystem, platform_type,os,administrator):


    cursor.execute("""SELECT "{}".id FROM
                    public."{}" WHERE "{}" = '{}';""".format(table_name,table_name,column_name,value));
    dbresponse = cursor.fetchall()

    if len(dbresponse) == 0:
        cursor.execute("""SELECT max(id) FROM public."{}";""".format(table_name))
        dbresponse = cursor.fetchall()
        if dbresponse[0][0] == None:
            id_cur = 1
        else:
            id_cur = dbresponse[0][0] + 1
        cursor.execute("""INSERT INTO public."{}"(id, name, purpose, department_owner, subsystem, platform_type,os,administrator) VALUES ({},'{}','{}','{}','{}','{}','{}','{}');""".format(table_name,id_cur, value,purpose, division_owner, subsystem, platform_type,os,administrator))
        connection.commit()
    else:
        id_cur = dbresponse[0][0]

    return id_cur


