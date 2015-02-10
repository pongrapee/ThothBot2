
import sys
import logging
from helpers.helperlib import *

import json
from multiprocessing import Process, Queue, Value, Lock
import time
import os
from datetime import datetime, timedelta

from items import Webbot2Item

logging.basicConfig(level=logging.INFO)
logging.getLogger('pika').setLevel(logging.INFO)

MAX_QUEUE_SIZE = 50
PRE_FETCH_SIZE = 20

class QueueWorkerTemplate( object ):
    workertype = 'QueueWorkerTemplate'
    static_id = 0
    def __init__(self, input_queue=None, output_queue=None, name='DefaultName', id=None):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.name = name
        QueueWorkerTemplate.static_id+=1
        self.id = QueueWorkerTemplate.static_id
        self.worker_name = self.name+'_'+str(self.id)
        self.msgcounter=Value('i',0)

    def process_item(self, item):
        self.msgcounter.value+=1
        return item

    def send_to_next_queue(self, item):
        if self.output_queue is not None:
            while(self.output_queue.qsize() >= MAX_QUEUE_SIZE):
                time.sleep(50/1000) #pause for 50ms
            self.output_queue.put(item)

    def main_loop(self):
        if self.input_queue is None: #or self.output_queue is None:
            assert(False)
        while True:
            input = self.input_queue.get()
            if input == 'QUIT':
                time.sleep(5)
                if self.output_queue: self.output_queue.put('QUIT')
                if self.input_queue: self.input_queue.put('QUIT')
                break
            output = self.process_item(input)
            # if output == 'QUIT':
            #     if self.output_queue: self.output_queue.put('QUIT')
            #     if self.input_queue: self.input_queue.put('QUIT')
            #     break
            self.send_to_next_queue(output)
        self.on_quit()
        
    def on_quit(self):
        pass
            
    def createinstance(self):
        return Process(target=self.main_loop)
    
