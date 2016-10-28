from .etlprocessor import EtlProcessor
import json

def process_data(json)->bool:
    etl_processor = EtlProcessor()
    type = _get_data_type(json)
    if type == 'chan': return etl_processor.process_channel_data(json)
    if type == 'serv': return etl_processor.process_server_data(json)
    print('Wrong json')
    return False


def _get_data_type(json)->bool:
    try:
        hosts = json['hosts']
        host = next (iter (hosts.values()))
        if 'org' in host.keys(): return 'chan'
        if 'os' in host.keys(): return 'serv'
        return None
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    file = open('../test_data/report001.json')
    data = json.load(file)
    process_data(data)
