# -*- coding: utf-8 -*-
# coding='utf-8'
import sys
import logging
from helpers.helperlib import *
from pipelines import *
import json

from multiprocessing import Process, Queue
from items import Webbot2Item
import pika
import time


logging.basicConfig(level=logging.DEBUG)

class QueueWorkerTemplate( object ):
    def __init__(self, input_queue=None, output_queue=None):
        self.input_queue = input_queue
        self.output_queue = output_queue

    def process_item( self, item ):

        return item

    def main_loop(self):
        if self.input_queue is None or self.output_queue is None:
            assert(False)
        while True:
            input = self.input_queue.get()
            output = self.process_item(input)
            self.output_queue.put(output)

    def createinstance(self):
        p = Process(target=self.main_loop)
        return p

class MyQueueGetter(QueueWorkerTemplate):
    
    def main_loop(self):

        self.hostname           = '27.254.142.36'
        self.username           = u'thothoffice'
        self.password           = u'thothoffice!'
        self.queue_name         = u'NickQueue'
        self.credentials        = pika.PlainCredentials(self.username,self.password)
        self.connection_parameters   = pika.ConnectionParameters( host=self.hostname, virtual_host='/', port=5672, socket_timeout=60, credentials=self.credentials)
        self.worker_name = 'MyQueueGetter'
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('pika').setLevel(logging.INFO)

        self.connection = pika.BlockingConnection(self.connection_parameters) 
        self.channel    = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name, durable=True)

        logging.info("Connected")
        self.channel.basic_qos( prefetch_count=20 )
        self.channel.basic_consume( self.process_item_from_MQ, queue=self.queue_name, consumer_tag=self.worker_name )
        while True:
            self.channel.start_consuming()
    
    def process_item_from_MQ( self, channel, method, properties, body ):
        msg = json.loads(body)
        #item = Webbot2Item()
        item ={}
        for key in msg:
            item[key] = msg[key]

        self.output_queue.put( item )
        self.channel.basic_ack( delivery_tag = method.delivery_tag )
    
class MyTextSegmentation(QueueWorkerTemplate):
    def __init__(self, input_queue=None, output_queue=None):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.myTextSegmentation = TextSegmentation()
    def main_loop(self):
        if self.input_queue is None or self.output_queue is None:
            assert(False)
        while True:
            input = self.input_queue.get()
            output = self.process_item(input)
            self.output_queue.put(output)
    def process_item( self, item ):
        item = self.myTextSegmentation.process_item( item=item, spider=None )
        Print( item['text'] )
        Print( item['text_segmented'] )
        return item






