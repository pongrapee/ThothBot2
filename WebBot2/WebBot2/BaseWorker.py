# -*- coding: utf-8 -*-
# coding='utf-8'
import sys
import logging
import pika
import json
logging.basicConfig(level=logging.DEBUG)


class ConsumerWorkersTemplate( object ):
    def __init__(   self, 
                    hostname     = '27.254.142.36', 
                    username     = u'thothoffice',
                    password     = u'thothoffice!',
                    queue_name   = 'NickQueue', 
                    worker_class = 'DefaultWorker',
                    worker_id    = 1,
                    num_theads   = 1,
                    use_queue    = False,
                    use_json     = True,
                    ):
        self.hostname       = hostname
        self.username       = username
        self.password       = password
        self.queue_name     = queue_name
        self.worker_class   = worker_class
        self.worker_id      = worker_id
        self.worker_name    = self.worker_class+":"+str(self.worker_id)
        self.num_theads     = num_theads 
        self.use_queue      = use_queue 
        self.use_json       = use_json  
        self.input_internam_queue=input_internam_queue, 
        self.output_internam_queue=output_internam_queue    

        self.credentials    = pika.PlainCredentials(username,password)
        self.connection_parameters = pika.ConnectionParameters( host=self.hostname, virtual_host='/', port=5672, socket_timeout=60, credentials=self.credentials)

        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('pika').setLevel(logging.INFO) #INFO

        self.connection     = None
        self.channel        = None
        self.msg_count      = 0

    def QueueConnect(self):
        
        self.connection = pika.BlockingConnection(self.connection_parameters) 
        self.channel    = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name, durable=True)

        logging.info("Connected")

    def QueuePublish(self, message):
        if self.use_json:
            message_txt = json.dumps(message, separators=(',',':'))
        else:
            message_txt = str(message)
        self.channel.basic_publish(exchange='',routing_key=self.queue_name, body=message_txt)
        
    def RunCallback(self):
        if self.use_queue:
            self.QueueConnect()
        else:
            assert(False)
        self.channel.basic_qos( prefetch_count=20 )
        if self.use_json:
            self.channel.basic_consume( self.WorkerCallbackUndecoded, queue=self.queue_name, consumer_tag=self.worker_name )
        else:
            self.channel.basic_consume( self.WorkerCallback, queue=self.queue_name, consumer_tag=self.worker_name )
        while(True):
            try:
                try:
                    self.channel.start_consuming()
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print e
                    self.channel.stop_consuming()
            except KeyboardInterrupt:
                logging.info( "====INTERRUPTED====" )
                break
            except Exception as e:
                print e
                pass
        self.connection.close()
        print "self.msg_count", self.msg_count
        exit()

    def WorkerCallbackUndecoded(self, channel, method, properties, body):
        self.msg_count += 1
        try:
            body_decoded = json.loads(body)
        except ValueError:
            logging.error(  "DecodeError : " + body + "\n" )
            logging.error(  "==================" )
            channel.basic_reject( delivery_tag = method.delivery_tag, requeue=False )
            
        self.WorkerCallback( channel, method, properties, body_decoded )

    def WorkerCallback(self, channel, method, properties, body):
        logging.info( "WorkerCallback : "+body )
        print "BaseWorkerCallback"

    def WorkerFunction(self, *arglist):
        logging.info( "WorkerFunction" )

    def Run(self):
        if self.use_queue:
            self.QueueConnect()    

        try:
            while( True ):
                self.WorkerFunction()
        except KeyboardInterrupt:
            logging.info( "====INTERRUPTED====" )
            if self.use_queue:
                self.connection.close()
            exit()







if __name__ == "__main__":
    worker = WorkersTemplate()
    worker.Run()

