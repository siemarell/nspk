from etl import etl, config
from vc_loader.vicube import ViCube
from vc_loader.data_sources import PgSource


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
    return etl.process_data(data)


if __name__ == '__main__':
    update_vicube()

    #update_dwh()