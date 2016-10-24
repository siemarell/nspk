import json
import csv
import psycopg2
import datetime
from os import listdir
from config import config

pg_types = {
    1043: {
        "name": "varchar",
        "vc_type": "string"
    },
    25: {
        "name": "text",
        "vc_type": "string"
    },
    701: {
        "name": "float8",
        "vc_type": "float"
    },
    23: {
        "name": "int4",
        "vc_type": "integer"
    },
    1082: {
        "name": "date",
        "vc_type": "date"
    }
}

class CsvSource:
    def __init__(self):
        self.path = config.file_source.path


    def get_tables(self):
        return [table.split('.json')[0] for table in listdir(self.path + '/tables') if table.endswith('.json')]

    def get_schema(self, table):
        with open('%s/tables/%s.json' % (self.path, table)) as file:
            return json.load(file)

    def get_data_iterator(self, table):
        try:
            file = open('%s/data/%s.csv' % (self.path, table))
            #reader = csv.reader(file)
            return CsvIter(file)
            #return iter(reader)
        except FileExistsError:
            return iter(())

class PgSource:
    def __init__(self):
        self.conn = psycopg2.connect(config.pg_source.conn_string)
        self.tables = config.pg_source.tables

    def get_tables(self):
        return self.tables


    def get_schema(self, table):
        result = {
            'name': table
        }
        with psycopg2.connect(config.pg_source.conn_string) as conn:
            cur = conn.cursor()

            #get table key column
            cur.execute('''
                        SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
                        FROM   pg_index i
                        JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                             AND a.attnum = ANY(i.indkey)
                        WHERE  i.indrelid = %s::regclass
                        AND    i.indisprimary
                    ''', (table,))
            key_column = cur.fetchone()
            if key_column: result['primary'] =  key_column[0]

            #get columns and types
            columns = []
            cur.execute('SELECT * FROM %s LIMIT 1' % table.split(' ')[0])
            for column in cur.description:
                col = {}
                col['name'] = column.name
                col['type'] = pg_types[column.type_code]['vc_type']
                columns.append(col)
        result['columns'] = columns
        return result

    def get_data_iterator(self, table):
        with psycopg2.connect(config.pg_source.conn_string) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM %s' % table.split(' ')[0])
            #return iter(cur.fetchall())
            return PgIter(cur)


class CsvIter:
    def __init__(self, file):
        self.file = file
        self.iterator = iter(csv.reader(self.file))

    def __next__(self):
        try:
            return next(self.iterator)
        except StopIteration:
            self.file.close()
        if self.file.closed: raise StopIteration

class PgIter:
    def __init__(self, cursor):
        self.cursor = cursor

    def __next__(self):
        nextRow = self.cursor.fetchone()
        if not nextRow: raise StopIteration
        return list(map(lambda x: x.isoformat() if isinstance(x, datetime.date) else x, nextRow))


if __name__ == '__main__':
    pg_source = PgSource()
    a = pg_source.get_tables()
    print(a)
    print(pg_source.get_schema(a[0]))