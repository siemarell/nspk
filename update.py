from etl import etl, config
from vc_loader.vicube import ViCube
from vc_loader.data_sources import PgSource
import json
from os import listdir
from os.path import isfile, join


def update_vicube() -> bool:
    vicube = ViCube()
    try:
        vicube.load_metadata()
        vicube.load_data(PgSource())
        vicube.save_snapshot()
        return True
    except Exception as e:
        print(e)
        vicube.load_snapshot()
        return False


def update_dwh(data) -> bool:
    try:
        result = etl.process_data(data)
        return result
    except Exception as e:
        print(e)
        return False


def update_dwh_nosafe(data):
    print(etl.process_data(data))

if __name__ == '__main__':
    file1 = open('/home/siem/PycharmProjects/nspk/test_data/ak_events_20161101202759_20161101212759.json')
    onlyfiles = [f for f in listdir('test_data') if isfile(join('test_data', f))]
    for file in onlyfiles:
        print(file)
        data = json.load(open('test_data/'+file))
        update_dwh_nosafe(data)
    # file2 = open('/home/siem/PycharmProjects/nspk/data/infra_events_20161015000000_20161028135209.json')
    # data1 = json.load(file1)
    # data2 = json.load(file2)
    # update_dwh(data1)
    # update_dwh(data2)
    #update_vicube()