import json
from collections import OrderedDict
from urllib.parse import quote

import requests

from vc_loader.config import config
from vc_loader.data_sources import CsvSource


def extract(d, keys):
    return {key: value for key, value in d.items() if key in keys}


def build_path(route, *args):
    route = quote(route % args)
    return config.host + route


class ViCube:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-VERSION': config.api_version
        }
        self.create_cube_counter = 0
        self.create_measure_group_counter = 0
        self.create_measure_counter = 0
        self.create_attribute_counter = 0
        self.create_link_counter = 0
        self.create_dimension_counter = 0

    def save_snapshot(self):
        path = build_path('/snapshots')
        response = requests.post(url=path, headers=config.headers, json={'values': config.snapshot_path})
        assert response.status_code == 200, 'Cannot save snapshot'

    def load_snapshot(self):
        path = build_path('/snapshots')
        response = requests.put(url=path, headers=config.headers, json={'values': config.snapshot_path})
        assert response.status_code == 200, 'Cannot load snapshot'

    def load_metadata(self):
        with open('metadata/metadata.json', encoding='utf-8') as file:
            body = json.load(file, object_pairs_hook=OrderedDict)

            self._drop_cubes()
            self._drop_dimension()

            for dimension in body['dimensions']:
                dim_id = self._create_dimension(dimension)

                for attribute in dimension['attributes']:
                    self._create_attribute(dim_id, attribute)

            for cube in body['cubes']:
                cube_id = self._create_cube(cube)

                for measure_group in cube['measureGroups']:
                    mg_id = self._create_measure_group(cube_id, measure_group)

                    for measure in measure_group['measures']:
                        self._create_measure(cube_id, mg_id, measure)

                    for link in measure_group['dimensionlinks']:
                        self._create_link(cube_id, mg_id, link)

    def load_data(self, source):
        database = config.database
        self._drop_database(database)
        self._create_database(database)
        tables = source.get_tables()

        for table in tables:
            self._create_table(database, source.get_schema(table))

            rows = []
            run = True
            count = 0

            path = build_path('/databases/%s/tables/%s/records', database, table)
            data_iterator = source.get_data_iterator(table)

            print('Load data into table "%s"' % table)
            while run:
                for i in range(config.bulk_size):
                    try:
                        row = next(data_iterator)
                        rows.append(row)
                        count += 1
                    except StopIteration:
                        run = False
                        break

                response = requests.post(url=path, headers=self.headers, json={'values': rows})

                assert response.status_code == 200, 'Cannot insert values into table %s: %s' % (table, response.text)

                #print('%d rows inserted into %s' % (count, table))
                rows = []

    def _drop_database(self, database):
        print('Drop database "%s"' % database)

        path = build_path('/databases/%s', database)
        response = requests.delete(url=path, headers=self.headers)

        # if response.status_code == 200:
        #     print('Successfully dropped database "%s"' % database)
        # else:
        #     args = (database, response.status_code, response.text)
        #     print('Cannot drop database %s: (%d) %s' % args)

    def _create_database(self, database):
        print('Create database "%s"' % database)

        path = build_path('/databases')
        response = requests.post(url=path, headers=self.headers, json={"name": database})

        assert response.status_code == 200, 'Cannot create database "%s": %s' % (database, response.text)

        #print('Database "%s" successfully created' % database)

    def _create_table(self, database, body):
        print('Create table "%s"' % body['name'])

        path = build_path('/databases/%s/tables', database)
        response = requests.post(url=path, headers=self.headers, json=body)

        assert response.status_code == 200, 'Cannot create table "%s": %s' % (body['name'], response.text)

        print('Table "%s" successfully created' % body['name'])

    def _insert_rows(self, table, dataset):
        path = build_path('/databases/%s/tables/%s/records', config.database, table)
        response = requests.post(url=path, headers=config.headers, json={'values': dataset})
        assert response.status_code == 200, 'Cannot insert values into table %s: %s' % (table, response.text)
        # print('%d rows inserted into %s' % (reader.line_num, table))

    def _drop_cubes(self):
        self.create_cube_counter = 0
        self.create_measure_group_counter = 0
        print('Drop cubes')

        path = build_path('/metadata/cubes')
        response = requests.delete(url=path, headers=self.headers)

        # if response.status_code == 200:
        #     print('Successfully dropped cubes')
        # else:
        #     print('Cannot drop cubes')

    def _drop_dimension(self):
        print('Drop dimensions')

        path = build_path('/metadata/dimensions')
        response = requests.delete(url=path, headers=self.headers)

        if response.status_code == 200:
            print('Successfully dropped dimensions')
        else:
            print('Cannot drop dimensions')

    def __create_entity(self, entity, name, path, body):
        # print('Create %s "%s"' % (entity, name))

        response = requests.post(url=path, headers=self.headers, json=body)

        assert response.status_code == 200, 'Cannot create %s "%s": %s' % (entity, name, response.text)

        # print('%s "%s" successfully created' % (entity.title(), name))

    def _create_cube(self, body):
        data = extract(body, ('name', 'databaseName'))

        path = build_path('/metadata/cubes')
        self.__create_entity('cube', data['name'], path, data)

        self.create_cube_counter += 1
        self.create_measure_group_counter = 0
        return self.create_cube_counter

    def _create_measure_group(self, cube, body):
        data = extract(body, ('name', 'tableName', 'dateColumn'))

        path = build_path('/metadata/cubes/%d/measuregroups', cube)
        self.__create_entity('measure group', data['name'], path, data)

        self.create_measure_group_counter += 1
        return self.create_measure_group_counter

    def _create_measure(self, cube, group, body):
        data = extract(body, ('name', 'columnName', 'aggregator'))

        path = build_path('/metadata/cubes/%d/measuregroups/%d/measures', cube, group)
        self.__create_entity('measure', data['name'], path, data)

        self.create_measure_counter += 1
        return self.create_measure_counter

    def _create_link(self, cube, group, body):
        data = extract(body, ('dimensionId', 'factColumnName'))

        path = build_path('/metadata/cubes/%d/measuregroups/%d/dimensionlinks', cube, group)
        self.__create_entity('dimension link', data['dimensionId'], path, data)

        self.create_link_counter += 1
        return self.create_link_counter

    def _create_dimension(self, body):
        data = extract(body, ('name', 'databaseName', 'tableName', 'idColumnName'))

        path = build_path('/metadata/dimensions')
        self.__create_entity('dimension', data['name'], path, data)

        self.create_attribute_counter = 0
        self.create_dimension_counter += 1
        return self.create_dimension_counter

    def _create_attribute(self, dimension, body):
        data = extract(body, ('name', 'columnName', 'orderByColumn'))
        path = build_path('/metadata/dimensions/%d/attributes', dimension)
        self.__create_entity('attribute', data['name'], path, data)

        self.create_attribute_counter += 1
        return self.create_attribute_counter





if __name__ == '__main__':
    csvSource = CsvSource()
    print(sorted(csvSource.get_tables()))
    print(csvSource.get_schema(csvSource.get_tables()[2]))
    print(next(csvSource.get_data_iterator('calendar')))
    itera = csvSource.get_data_iterator('d_uslugi')
    while True:
        print(next(itera))
