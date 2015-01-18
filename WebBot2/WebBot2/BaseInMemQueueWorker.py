# -*- coding: utf-8 -*-
# coding='utf-8'
import sys
import logging
from helpers.helperlib import *

import json

from multiprocessing import Process, Queue, Value, Lock
from items import Webbot2Item
import pika
import time

from TextSegmentation import *
from Keyword import *
from SentimentFeatures import *

import time
import os

logging.basicConfig(level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)

MAX_QUEUE_SIZE = 10
PRE_FETCH_SIZE = 20

class QueueWorkerTemplate( object ):
    workertype = 'QueueWorkerTemplate'
    static_id = 0
    def __init__(self, input_queue, output_queue, name='DefaultName', id=None):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.name = name
        QueueWorkerTemplate.static_id+=1
        self.id = QueueWorkerTemplate.static_id
        self.worker_name = str(self.id)+'_'+self.name
        self.msgcounter=Value('i',0)

    def process_item( self, item ):
        self.msgcounter.value+=1
        return item

    def send_to_next_queue( self, item ):
        while(self.output_queue.qsize() >= MAX_QUEUE_SIZE):
            time.sleep(50/1000) #pause for 50ms
        if self.output_queue is not None:
            self.output_queue.put(item)

    def main_loop(self):
        if self.input_queue is None or self.output_queue is None:
            assert(False)
        while True:
            input = self.input_queue.get()
            output = self.process_item(input)
            self.send_to_next_queue(output)
            
    def createinstance(self):
        p = Process(target=self.main_loop)
        return p

class MyQueueGetter_old(QueueWorkerTemplate):
    workertype = 'MyQueueGetter'
    def __init__(self, input_queue=None, output_queue=None, name='MyQueueGetter', id=0, hostname='27.254.142.36', username=u'thothoffice', password=u'thothoffice!', queue_name=u'NickQueue' ):

        super(MyQueueGetter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        print "MyQueueGetter INIT"
        self.hostname           = hostname
        self.username           = username
        self.password           = password
        self.queue_name         = queue_name
        self.worker_name        = self.name+"_"+str(self.id)
        self.credentials        = pika.PlainCredentials(self.username,self.password)
        self.connection_parameters   = pika.ConnectionParameters( host=self.hostname, virtual_host='/', port=5672, socket_timeout=60, credentials=self.credentials) 
        

    def main_loop(self):
        while(True):
            try:
                self.connection = pika.BlockingConnection(self.connection_parameters) 
                self.channel    = self.connection.channel()

                self.channel.queue_declare(queue=self.queue_name, durable=True)

                self.channel.basic_qos( prefetch_count=PRE_FETCH_SIZE )
                self.channel.basic_consume( self.process_item_from_MQ, queue=self.queue_name, consumer_tag=self.worker_name )
                while True:
                    self.channel.start_consuming( )
            except pika.exceptions.ConnectionClosed:
                pass
            except:
                break
        
    def process_item_from_MQ( self, channel, method, properties, body ):
        msg = json.loads(body)
        item = Webbot2Item()
        for key in msg:
            item[key] = msg[key]
        logging.debug(self.worker_name+' :: input from :'+self.queue_name)
        item['delivery_tag'] = method.delivery_tag
        self.send_to_next_queue( item ) 
        #self.channel.basic_ack( delivery_tag = method.delivery_tag )
        self.msgcounter.value+=1
    
class MyQueueGetter(QueueWorkerTemplate):
    workertype = 'MyQueueGetter'
    def __init__(self, input_queue=None, output_queue=None, name='MyQueueGetter', id=0, hostname='27.254.142.36', username=u'thothoffice', password=u'thothoffice!', queue_name=u'NickQueue' ):

        super(MyQueueGetter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.hostname           = hostname
        self.username           = username
        self.password           = password
        self.queue_name         = queue_name
        self.worker_name        = str(self.id)+'_'+self.name
        self.credentials        = pika.PlainCredentials(self.username,self.password)
        self.connection_parameters   = pika.ConnectionParameters( host=self.hostname, virtual_host='/', port=5672, socket_timeout=60, credentials=self.credentials) 
        

    def main_loop(self):
        while(True):
            try:
                self.connection = pika.BlockingConnection(self.connection_parameters) 
                self.channel    = self.connection.channel()

                self.channel.queue_declare(queue=self.queue_name, durable=True)

                self.channel.basic_qos( prefetch_count=PRE_FETCH_SIZE )
                #self.channel.basic_consume( self.process_item_from_MQ, queue=self.queue_name, consumer_tag=self.worker_name )
                while True:
                    #self.channel.start_consuming()
                    #get from confirm queue
                    #and send confirm back to MQ
                    #while(not self.input_queue.empty()):
                    while (self.input_queue.qsize()>0):
                        item = self.input_queue.get()
                        #print "DONE :", item['delivery_tag']
                        self.channel.basic_ack( delivery_tag=item['delivery_tag'] )
                    #get next item from MQ but only if output queue is not full
                    if self.output_queue.qsize() >= MAX_QUEUE_SIZE:
                        continue
                    for i in range(PRE_FETCH_SIZE):
                        method_frame, header_frame, body =self.channel.basic_get(self.queue_name)
                        if method_frame:
                            item = Webbot2Item()
                            msg = json.loads(body)
                            for key in msg:
                                item[key] = msg[key]
                            item['delivery_tag'] = method_frame.delivery_tag  
                            #print "NEW  :", item['delivery_tag']                    
                            self.process_item_from_MQ( item )

            except pika.exceptions.ConnectionClosed:
                pass
            # except:
            #     print "ERROR"
            #     break
        
    def process_item_from_MQ( self, item ):
        logging.debug(self.worker_name+' :: input from :'+self.queue_name)
        self.output_queue.put( item ) 
        self.msgcounter.value+=1

class MyTextSegmentation(QueueWorkerTemplate):
    workertype = 'MyTextSegmentation'
    def __init__(self, input_queue=None, output_queue=None, name='MyTextSegmentation', id=0):
        super(MyTextSegmentation,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.myTextSegmentation = TextSegmentation()
        
    def process_item( self, item ):
        item = self.myTextSegmentation.process_item( item=item )
        logging.debug(self.worker_name+' :: item[text] : '+item['text'].decode('utf-8','ignore').encode('tis-620','ignore'))
        logging.debug(self.worker_name+' :: item[text_segmented] : '+item['text_segmented'].decode('utf-8','ignore').encode('tis-620','ignore'))
        self.msgcounter.value+=1
        return item

class MyKeyword(QueueWorkerTemplate):
    workertype = 'MyKeyword'
    def __init__(self, input_queue=None, output_queue=None, name='MyKeyword', id=0):
        super(MyKeyword,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.myKeyword = Keyword(forum_name='KeywordNickQueue')
        
    def process_item( self, item ):
        item = self.myKeyword.process_item( item=item )
        logging.debug(self.worker_name+' :: item[keywordlist] : ')
        for row in item['keywordlist']:
            logging.debug(self.worker_name+'\t\t'+row.decode('utf-8','ignore').encode('tis-620','ignore'))
        self.msgcounter.value+=1
        return item

class MySentimentFeatures(QueueWorkerTemplate):
    workertype = 'MySentimentFeatures'
    def __init__(self, input_queue=None, output_queue=None, name='MySentimentFeatures', id=0):
        super(MySentimentFeatures,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.mySentimentFeatures = SentimentFeatures()
        
    def process_item( self, item ):
        item = self.mySentimentFeatures.process_item( item=item )
        self.msgcounter.value+=1
        return item


class MyQueuePutter(QueueWorkerTemplate):
    workertype = 'MyQueuePutter'
    def __init__(self, input_queue=None, output_queue=None, name='MyQueuePutter', id=0, hostname='27.254.142.36', username=u'thothoffice', password=u'thothoffice!', queue_name=u'NickQueue2', original_queue_name=u'NickQueue' ):

        super(MyQueuePutter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.hostname           = hostname
        self.username           = username
        self.password           = password
        self.queue_name         = queue_name
        self.original_queue_name = original_queue_name
        self.credentials        = pika.PlainCredentials(self.username,self.password)
        self.connection_parameters   = pika.ConnectionParameters( host=self.hostname, virtual_host='/', port=5672, socket_timeout=60, credentials=self.credentials)
        
    def process_item( self, item ):
        logging.debug(self.worker_name+' :: output to :'+self.queue_name)
        self.channel.basic_publish( exchange='', routing_key=self.queue_name, body=json.dumps(str(item), separators=(',',':')))
        self.output_queue.put(item) 
        return item

    def main_loop(self):
        while(True):
            try:
                self.connection = pika.BlockingConnection(self.connection_parameters) 
                self.channel    = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                #self.channel2.queue_declare(queue=self.original_queue_name, durable=True)

                if self.input_queue is None:
                    assert(False)
                while True:
                    input = self.input_queue.get()
                    self.process_item(input)
                    self.msgcounter.value+=1

            except pika.exceptions.ConnectionClosed:
                pass
            except:
                break


def START_WORK_PIPELINE( worker_list ):

    queue_list = []
    first_queue = Queue()
    previous_queue = first_queue
    last_queue = None
    jobs=[]
    for worker in worker_list:
        input_queue = previous_queue
        output_queue = Queue()
        last_queue = output_queue
        current_class_workerlist=[]
        for num in range(worker[1]):
            current_worker = worker[0](input_queue=input_queue, output_queue=output_queue, )
            print current_worker.worker_name
            current_class_workerlist.append(current_worker)
            jobs.append(current_worker.createinstance())
        queue_list.append([worker[0],input_queue,output_queue,current_class_workerlist])
        previous_queue = output_queue

    myLoopback = QueueWorkerTemplate( input_queue=last_queue, output_queue=first_queue, )
    myLoopback.worker_name = "XX_LoopBack"
    print myLoopback.worker_name
    jobs.append(myLoopback.createinstance())
    queue_list.append([QueueWorkerTemplate,last_queue,first_queue,[myLoopback]])

    for job in jobs:
        job.start()

    try:
        time.sleep(1)
        while True:
            for job in jobs:
                job.join(0)
            if True:
                #os.system('cls')
                print "==============================================================="
                for row in queue_list:
                    print '\t{0:3d} : [{1:5d}] : {2}  '.format(row[1].qsize(), sum(worker.msgcounter.value for worker in row[3]), row[0].workertype)
                    for worker in row[3]:
                        print '\t\t{0:5d} : {1}'.format(worker.msgcounter.value, worker.worker_name)
                print "---------------------------------------------------------------"
                print "total msgs :", sum( worker.msgcounter.value for worker in queue_list[len(queue_list)-1][3] )
                print "==============================================================="
                time.sleep(1)

    except KeyboardInterrupt:
        print "TERMINATING"
    try:
        for job in jobs:
            job.terminate()
    except:
        for job in jobs:
            job.terminate()

if __name__ == "__main__":
    
    workpipeline = [
    
        [MyQueueGetter,         1],
        [MyTextSegmentation,    3],
        [MyKeyword,             1],
        [MySentimentFeatures,   1],
        [MyQueuePutter,         1],

    ]

    START_WORK_PIPELINE( workpipeline )


    # jobs=[]
    # Q1 = Queue()
    # Q2 = Queue()
    # Q3 = Queue()
    # Q4 = Queue()
    
    # myQueueWorker = MyQueueGetter(input_queue=None, output_queue=Q1)
    # jobs.append(myQueueWorker.createinstance())
    
    # myTextSegmentation = MyTextSegmentation(input_queue=Q1, output_queue=Q2)
    # jobs.append(myTextSegmentation.createinstance())

    # myKeyword = MyKeyword(input_queue=Q2, output_queue=Q3)
    # jobs.append(myKeyword.createinstance())

    # mySentimentFeatures = MySentimentFeatures(input_queue=Q3, output_queue=Q4)
    # jobs.append(mySentimentFeatures.createinstance())

    # myQueuePutter = MyQueuePutter(input_queue=Q4, output_queue=None)
    # jobs.append(myQueuePutter.createinstance())

    # for job in jobs:
    #     job.start()

    # try:
    #     while True:
    #         for job in jobs:
    #             print myQueuePutter.msgcounter
    #             job.join(1)

    # except KeyboardInterrupt:
    #     print "TERMINATING"

    # for job in jobs:
    #     job.terminate()
