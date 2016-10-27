import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from etl.etlprocessor import EtlProcessor
from etl import etl, config
from vc_loader import vicube_loader, data_sources
from worker import DataWorker

import json


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, consumer: DataWorker):
        super().__init__()
        self.consumer = consumer

    def on_created(self, event):
        print(event.src_path)
        path = event.src_path
        if path.endswith('.json'):
            file = open(path)
            data = json.load(file)
            self.consumer.add_item(data)


def update_dwh(data) -> bool:
    return etl.process_data(data)


def update_vicube():
    v_loader = vicube_loader.DataLoader()
    v_loader.load_metadata()
    v_loader.load_data(data_sources.PgSource())


if __name__ == "__main__":
    worker = DataWorker()
    worker.setDaemon(True)
    worker.start()
    path = config.data_folder
    event_handler = MyEventHandler(worker)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
#
# if __name__ == '__main__':
#     # file = open('test_data/ak.json')
#     # data = json.load(file)
#     # if etl.process_data(data):
#     #     update_vicube()
#     # else:
#     #     print('etl error')
#     update_vicube()