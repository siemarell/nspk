from etl import etl, config
from vc_loader import vicube_loader, data_sources


def update_vicube()->bool:
    v_loader = vicube_loader.DataLoader()
    try:
        v_loader.load_metadata()
        v_loader.load_data(data_sources.PgSource())
        return True
    except Exception as e:
        print(e)
        return False


def update_dwh(data) -> bool:
    return etl.process_data(data)


if __name__ == '__main__':
    update_vicube()