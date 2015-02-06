# -*- coding: utf-8 -*-
# coding='utf-8'

from QueueWorkerTemplate import *

from TextSegmentation import *
from Keyword import *
from SentimentFeatures import *
from pipelines import *
import time

class MyTextSegmentation(QueueWorkerTemplate):
    workertype = 'MyTextSegmentation'
    def __init__(self, input_queue=None, output_queue=None, name='MyTextSegmentation', id=0):
        super(MyTextSegmentation,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.myTextSegmentation = None
        
    def process_item( self, item ):
        if self.myTextSegmentation == None:
            self.myTextSegmentation = TextSegmentation()
        item = self.myTextSegmentation.process_item( item=item )
        try:
            logging.debug(self.worker_name+' :: item[text] : '+item['text'].decode('utf-8','ignore').encode('tis-620','ignore'))
            logging.debug(self.worker_name+' :: item[text_segmented] : '+item['text_segmented'].decode('utf-8','ignore').encode('tis-620','ignore'))
        except KeyError:
            pass
        self.msgcounter.value+=1
        return item

class MyKeyword(QueueWorkerTemplate):
    workertype = 'MyKeyword'
    def __init__(self, input_queue=None, output_queue=None, name='MyKeyword', id=0):
        super(MyKeyword,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.myKeyword = None
    
    def process_item( self, item ):
        
        if self.myKeyword == None:
            self.myKeyword = Keyword(forum_name=self.worker_name)
        
        item = self.myKeyword.process_item( item=item )
        try:
            logging.debug(self.worker_name+' :: item[keywordlist] : ')
            for row in item['keywordlist']:
                logging.debug(self.worker_name+'\t\t'+row.decode('utf-8','ignore').encode('tis-620','ignore'))
        except KeyError:
            pass
        self.msgcounter.value+=1
        return item

    def on_quit(self):
        print "mykeyword onquit"
        if self.myKeyword is not None:
            self.myKeyword.save_file()
     

class MySentimentFeatures(QueueWorkerTemplate):
    workertype = 'MySentimentFeatures'
    def __init__(self, input_queue=None, output_queue=None, name='MySentimentFeatures', id=0):
        super(MySentimentFeatures,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.mySentimentFeatures = None
        
    def process_item( self, item ):
        if self.mySentimentFeatures == None:
            self.mySentimentFeatures = SentimentFeatures()
        item = self.mySentimentFeatures.process_item( item=item )
        self.msgcounter.value+=1
        return item

class MyDebugPrinter(QueueWorkerTemplate):
    workertype = 'MyDebugPrinter'
    def __init__(self, input_queue=None, output_queue=None, name='MyDebugPrinter', id=0, hostname='27.254.142.36', username=u'thothoffice', password=u'thothoffice!', queue_name=u'NickQueue' ):

        super(MyDebugPrinter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)

    def process_item( self, item ):  
        Print( item )
        self.msgcounter.value+=1
        return item


def START_MQ_CONFIRM_WORK_PIPELINE_ST( worker_list=[], confirm_needed=False, client_id='c153', silent=False, ):
    msg_processed=0
    _start = datetime.utcnow() + timedelta(hours=7)
    if not silent: print _start
    pipeline = []
    first_worker = None
    last_worker  = None
    for workerclass, numworker in worker_list:
        if not silent: print workerclass.workertype
        worker = workerclass( name=client_id )
        pipeline.append( worker )
        if first_worker == None: first_worker = worker
        last_worker = worker
    input = Webbot2Item()
    try:
        while True:
            input = Webbot2Item()
            for pipelinestep in pipeline: 
                input = pipelinestep.process_item(input)
                if input == 'QUIT':
                    break #for loop
            try:
                if confirm_needed: 
                    first_worker.confirm_msg( output )
            except AttributeError: 
                pass
            msg_processed = last_worker.msgcounter.value
            if msg_processed % 10 == 0:
                #print time.utcnow() + timedelta(hours=7), "- Processed :", msg_processed
                if not silent: 
                    print '.',
            if msg_processed % 100 == 0:
                #print time.utcnow() + timedelta(hours=7), "- Processed :", msg_processed
                if not silent: 
                    print "Processed :", "{0:5d}".format(msg_processed), "[", datetime.utcnow() + timedelta(hours=7), "]"
            if input == 'QUIT':
                break #while loop 
    except KeyboardInterrupt:
        if not silent: print "TERMINATING"

    for pipelinestep in pipeline: 
        pipelinestep.on_quit()
                
    _end = datetime.utcnow() + timedelta(hours=7)
    duration = _end - _start
    print "Start    :", _start
    print "End      :", _end
    print "Duration :", duration
    print "Msg      :", msg_processed
    print "Msg/Sec  :", float(int(msg_processed *10 / (duration.total_seconds()))) / 10

def START_MQ_CONFIRM_WORK_PIPELINE_MT( worker_list, confirm_needed=False, client_id='c153', silent=False, ):

    _start = datetime.utcnow() + timedelta(hours=7)
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
            current_worker = worker[0](input_queue=input_queue, output_queue=output_queue, name=client_id )
            if not silent: print current_worker.worker_name
            current_class_workerlist.append(current_worker)
            jobs.append(current_worker.createinstance())
        queue_list.append([worker[0],input_queue,output_queue,current_class_workerlist])
        previous_queue = output_queue

    if confirm_needed:
        myLoopback = QueueWorkerTemplate( input_queue=last_queue, output_queue=first_queue, )
        myLoopback.worker_name = "XX_LoopBack"
        if not silent: print myLoopback.worker_name
        jobs.append(myLoopback.createinstance())
        queue_list.append([QueueWorkerTemplate,last_queue,first_queue,[myLoopback]])
    else:
        myDrainer = QueueWorkerTemplate( input_queue=last_queue, output_queue=None,)
        myDrainer.worker_name = "XX_Drainer"
        if not silent: print myDrainer.worker_name
        jobs.append(myDrainer.createinstance())
        queue_list.append([QueueWorkerTemplate,last_queue,first_queue,[myDrainer]])
    
    for job in jobs:
        #print job
        job.start()

    try:
        time.sleep(1)
        CONTINUE = True
        while CONTINUE:
            CONTINUE = False
            output = ''
            for job in jobs:
                #job.join(0)
                CONTINUE = CONTINUE | job.is_alive()
                #output += str(job) + ":" + str(job.is_alive()) + "\n"
            if True:
                
                
                output+= "===============================================================\n"
                for row in queue_list:
                    output+= '\t{0:3d} : [{1:5d}] : {2} \n'.format(row[1].qsize(), sum(worker.msgcounter.value for worker in row[3]), row[0].workertype)
                    for worker in row[3]:
                        output+= '\t\t{0:5d} : {1}\n'.format(worker.msgcounter.value, worker.worker_name)
                output+= "--------------------------------------------------------------\n"
                msg_processed = sum( worker.msgcounter.value for worker in queue_list[len(queue_list)-1][3] )
                output+= "total msgs :"+str(msg_processed)+"\n"
                output+= "===============================================================\n"

                if not silent: 
                    os.system('cls')
                    print output
                if silent:
                    print "total msgs :"+str(msg_processed)
                time.sleep(1)

    except KeyboardInterrupt:
        if not silent: print "TERMINATING"

    try:
        for job in jobs:
            job.terminate()
    except KeyboardInterrupt:
        for job in jobs:
            job.terminate()

    _end = datetime.utcnow() + timedelta(hours=7)
    duration = _end - _start
    print "Start    :", _start
    print "End      :", _end
    print "Duration :", duration
    print "Msg      :", msg_processed
    print "Msg/Sec  :", float(int(msg_processed *10 / (duration.total_seconds()))) / 10

if __name__ == "__main__":
    
    workpipeline = [
    
        [MyQueueGetter,         1,  ],
        [MyTextSegmentation,    1,  ],
        [MyKeyword,             1,  ],
        [MySentimentFeatures,   1,  ],
        [MyQueuePutter,         1,  ],

    ]

    START_MQ_CONFIRM_WORK_PIPELINE_ST( workpipeline, False)

    START_MQ_CONFIRM_WORK_PIPELINE_MT( workpipeline, False )

