import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from etl import config
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