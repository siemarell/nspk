import json
import csv
import psycopg2
from os import listdir
from config import config

pg_types = {
    "1043": {
        "name": "varchar",
        "vc_type": "string"
    },
    "25": {
        "name": "text",
        "vc_type": "string"
    },
    "701": {
        "name": "float8",
        "vc_type": "float"
    },
    "23": {
        "name": "int4",
        "vc_type": "integer"
    },
    "1082": {
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
            return SmartIter(file)
            #return iter(reader)
        except FileExistsError:
            return iter(())

class PgSource:
    def __init__(self):
        self.conn = psycopg2.connect(config.pg_source.conn_string)
        self.tables = config.pg_source.tables

    def get_tables(self):
        pass


class SmartIter:
    def __init__(self, file):
        self.file = file
        self.iterator = iter(csv.reader(self.file))

    def __next__(self):
        try:
            return next(self.iterator)
        except StopIteration:
            self.file.close()
        if self.file.closed: raise StopIteration