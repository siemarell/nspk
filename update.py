from etl import etl, config
from vc_loader.vicube import ViCube
from vc_loader.data_sources import PgSource
import json


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



if __name__ == '__main__':
    # file1 = open('/home/siem/PycharmProjects/nspk/data/ak_events_20161015000000_20161028135045.json')
    # file2 = open('/home/siem/PycharmProjects/nspk/data/infra_events_20161015000000_20161028135209.json')
    # data1 = json.load(file1)
    # data2 = json.load(file2)
    # update_dwh(data1)
    # update_dwh(data2)
    update_vicube()