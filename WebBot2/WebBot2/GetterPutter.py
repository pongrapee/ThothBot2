# -*- coding: utf-8 -*-
# coding='utf-8'

from pipelines import *
from QueueWorkerTemplate import *

import pika
import MySQLdb

class MyQueueGetter(QueueWorkerTemplate):
    workertype = 'MyQueueGetter'
    def __init__(self, input_queue=None, output_queue=None, name='MyQueueGetter', id=0, hostname='27.254.142.36', username=u'thothoffice', password=u'thothoffice!', queue_name=u'NickQueue' ):

        super(MyQueueGetter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.hostname           = hostname
        self.username           = username
        self.password           = password
        self.queue_name         = queue_name
        self.credentials        = pika.PlainCredentials(self.username,self.password)
        self.connection_parameters   = pika.ConnectionParameters( host=self.hostname, virtual_host='/', port=5672, socket_timeout=60, credentials=self.credentials) 
        self.connection = None
        self.channel    = None

    def main_loop(self):
        while True:
            self.connection = pika.BlockingConnection(self.connection_parameters) 
            self.channel    = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.basic_qos( prefetch_count=PRE_FETCH_SIZE )
            try:
                while True:
                    #input queue is confirm queue
                    while (self.input_queue.qsize()>0):
                        to_confirm = self.input_queue.get()
                        self.channel.basic_ack( delivery_tag=to_confirm['delivery_tag'] )
                    if self.output_queue.qsize() >= MAX_QUEUE_SIZE:
                        continue
                    item = None
                    output = self.process_item( item )
                    if output is None: 
                        continue
                    self.output_queue.put( output )
            except pika.exceptions.ConnectionClosed:
                assert(False)
                #TODO: handle disconnect
        self.on_quit()

    def getchannel(self):
        if self. connection is None:
            self.connection = pika.BlockingConnection(self.connection_parameters) 
        if self.channel is None:
            self.channel    = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
        return self.channel

    def process_item(self, item):
        if self. connection is None:
            self.connection = pika.BlockingConnection(self.connection_parameters) 
        if self.channel is None:
            self.channel    = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
        while True:
            method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
            if method_frame:
                item = Webbot2Item()
                msg = json.loads(body)
                for key in msg:
                    item[key] = msg[key]
                item['delivery_tag'] = method_frame.delivery_tag  
                logging.debug(self.worker_name+' :: input from :'+self.queue_name)    
                self.msgcounter.value+=1
                break
            else:
                if self.output_queue is None and self.output_queue is None:
                    break
            pass
        #if method_frame is None, then the return item should be None
        return item

    def confirm_msg(self,item ):
        if self.channel == None:
            assert(False)
        self.channel.basic_ack( delivery_tag=item['delivery_tag'] )

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
        self.connection = None
        self.channel    = None
            
    def main_loop(self):
        while(True):
            self.connection = pika.BlockingConnection(self.connection_parameters) 
            self.channel    = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            try:
                if self.input_queue is None:
                    assert(False)
                while True:
                    input = self.input_queue.get()
                    if input == 'QUIT':
                        self.send_to_next_queue('QUIT')
                        self.input_queue.put('QUIT')
                        break
                    output = self.process_item(input)
                    self.output_queue.put(output) 
            except pika.exceptions.ConnectionClosed:
                assert(False)
                #TODO: handle disconnect
            if input == 'QUIT':
                break
        self.on_quit()

    def process_item( self, item ):
        if self. connection is None:
            self.connection = pika.BlockingConnection(self.connection_parameters) 
        if self.channel is None:
            self.channel    = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
        logging.debug(self.worker_name+' :: output to :'+self.queue_name)
        self.channel.basic_publish( exchange='', routing_key=self.queue_name, body=json.dumps(str(item), separators=(',',':')))
        self.msgcounter.value+=1
        return item

class MySQLGetter(QueueWorkerTemplate):
    ##TODO TODO TODO
    workertype = 'MySQLGetter'
    def __init__(   self, 
                    input_queue=None, 
                    output_queue=None, 
                    name='MySQLGetter', 
                    id=0, 
                    host="27.254.95.44",
                    user="kpiowrdb",
                    passwd="g8ruFv;viNi^,",
                    db="kpiology",
                    SQLSTATEMENT=''):
        super(MySQLGetter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        # connect to DB
        self.sqldb = None
        self.cursor = None
        self.column_list = [
                        'post_id', 
                        'subject_name', 
                        'post_date', 
                        'body', 
                        'type', 
                        'author', 
                        'group', 
                        'facebook_page_name', 
                        'likes', 
                        'shares', 
                        'mood',
                        ]
        self.item_column_list = [
                        'post_id', 
                        'subject', 
                        'datetime', 
                        'text', 
                        'type', 
                        'author', 
                        'group', 
                        'page_id', 
                        'likes', 
                        'shares', 
                        'mood_original',
                        ]

        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        if SQLSTATEMENT == '':
            self.SQLSTATEMENT = "SELECT `post_id`, `subject_name` as `subject`, `post_date` as `datetime`, `body` as `text`, `type`, `author`, `group`, `facebook_page_name` as `page_id`, `likes`, `shares`, `mood` as `mood_original` FROM facebook_c149 WHERE `post_id` {0} AND `post_date` > '2015-01-01' ORDER BY `post_id` DESC LIMIT 100;"
        else:
            self.SQLSTATEMENT = SQLSTATEMENT
        self.execute_sql = True
        self.at_least_some_data = False
        self.minidprocessed = 0
        self.more_data = True

    def main_loop(self):
        if self.input_queue is None or self.output_queue is None:
            assert(False)
        while True:
            input = Webbot2Item()
            output = self.process_item(input)
            if output == 'QUIT':
                self.send_to_next_queue('QUIT')
                self.input_queue.put('QUIT')
                break
            self.send_to_next_queue(output)
                
    def process_item( self, item ):
        if item is None:
            assert False
        while self.more_data:
            if self.execute_sql == True:
                if self.minidprocessed == False: #initial run
                    post_id_filter = ">'0'"
                else:
                    post_id_filter = "<'"+str(self.minidprocessed)+"'"

                self.sqldb = MySQLdb.connect(   host=self.host,
                                                user=self.user,
                                                passwd=self.passwd,
                                                db=self.db,
                                                use_unicode=True,
                                                charset="utf8",
                                            )
                self.cursor = self.sqldb.cursor()
                #print self.SQLSTATEMENT.format(post_id_filter)
                self.cursor.execute(self.SQLSTATEMENT.format(post_id_filter))
                self.execute_sql = False
                self.at_least_some_data = False
                
            row = self.cursor.fetchone()

            if row is not None:
                self.at_least_some_data = True
                for i in range(len(row)):
                    item[self.item_column_list[i]] = row[i]
                if self.minidprocessed == 0 or self.minidprocessed > item['post_id']:
                    self.minidprocessed = item['post_id']
                #print item['post_id']
                self.msgcounter.value+=1
                break
            else:
                if self.at_least_some_data:
                    self.execute_sql = True
                    self.at_least_some_data = False
                    continue
                else:
                    item = 'QUIT'
                    self.more_data = False
                    break

        return item

class MyCSVPutter(QueueWorkerTemplate):
    workertype = 'MyCSVPutter'
    def __init__(self, input_queue=None, output_queue=None, name='MyCSVPutter', id=0, hostname='27.254.142.36', username=u'thothoffice', password=u'thothoffice!', queue_name=u'NickQueue' ):

        super(MyCSVPutter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.file = None
        self.first_line = True
        

    def process_item( self, item ):  
        #Print( item )
        
        if self.file is None:
            self.file = open('c:\\temp\\csv\\'+self.worker_name+'_output.tsv', "w")
        if item is not None:
            if self.first_line:
                self.first_line = False 
                for attr in sorted(item):
                    self.file.write( str(attr)+"\t" )
                self.file.write("\n")
          
            for attr in sorted(item):
                if item[attr] is not None:
                    self.file.write(  str(item[attr]).replace("\r"," ").replace("\n"," ").replace("\t"," ")+"\t" )
                else:
                    self.file.write(  str(' ') )
            self.file.write("\n")
        self.msgcounter.value+=1
        
        return item