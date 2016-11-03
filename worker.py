from queue import Queue
from threading import Thread
import time
from update import *

class DataWorker(Thread):
    def __init__(self):
        super().__init__()
        self.name = 'Worker'
        self.queue = Queue(maxsize=10)

    def add_item(self,item):
        self.queue.put(item)

    def run(self):
        data_changed =False
        while True:
            if not self.queue.empty():
                data = self.queue.get()
                print('Trying to update dwh with: ' + data['name'])
                if update_dwh(data):
                    print('Success')
                    data_changed=True
                else: print('Failure')
            else:
                if data_changed:
                    if update_vicube():
                        print('Success')
                    else: print('Failure')
                    data_changed = False
            time.sleep(2)


