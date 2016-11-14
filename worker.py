from queue import Queue
from threading import Thread
import time
from update import *
import log
logger = log.getMyLogger(__name__)

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
                logger.info('Trying to update dwh with: ' + data['name'])
                if update_dwh(data):
                    logger.info('SUCCESS: ' + data['name'])
                    data_changed=True
                else: logger.error('FAILURE: ' + data['name'])
            else:
                if data_changed:
                    if update_vicube():
                        logger.info('SUCCESS UPDATE VICUBE')
                    else: logger.error('FAILURE UPDATE VICUBE')
                    data_changed = False
            time.sleep(2)


