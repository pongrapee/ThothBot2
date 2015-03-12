# -*- coding: utf-8 -*-
# coding='utf-8'

from QueueWorkerTemplate import *

from TextSegmentation import *
from Keyword import *
from SentimentFeatures import *
from kucut import SimpleKucutWrapper as KUCut
from RealTimeIndex import *

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
        item = self.myTextSegmentation.process_item( item=clean_text(item) )
        try:
            logging.debug(self.worker_name+' :: item[text] : '+item['text'].decode('utf-8','ignore').encode('tis-620','ignore'))
            logging.debug(self.worker_name+' :: item[text_segmented] : '+item['text_segmented'].decode('utf-8','ignore').encode('tis-620','ignore'))
        except KeyError:
            pass
        self.msgcounter.value+=1
        return item

class MyTextSegmentationKUCUT(QueueWorkerTemplate):
    workertype = 'MyTextSegmentationKUCUT'
    def __init__(self, input_queue=None, output_queue=None, name='MyTextSegmentationKUCUT', id=0):
        super(MyTextSegmentationKUCUT,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.myTextSegmentationKUCUT = None
        
    def process_item( self, item ):
        if self.myTextSegmentationKUCUT == None:
            self.myTextSegmentationKUCUT = KUCut()
        
        new_tags_list = {}

        try:
            input_title = clean_text(item['title'])
            output_title,tags_list_title = self.myTextSegmentationKUCUT.tokenize([input_title])
            output_title_2 = output_title[0][0]
            
            for word in output_title_2:
                if word == '_':
                    output_title_2.remove(word)
            result_title = ' '.join(output_title_2)
            item['title_segmented'] = result_title
            
            for tag in tags_list_title:
                new_tags_list[tag.decode('tis-620','ignore').encode('utf-8','ignore')] = []
                for token in tags_list_title[tag]:
                    try:
                        new_tags_list[tag.decode('tis-620','ignore').encode('utf-8','ignore')].append(token.decode('tis-620','ignore').encode('utf-8','ignore'))
                    except:
                        pass
            
        except KeyError:
            item['title']=""
            item['title_segmented']=""
        except Exception as e:
            print "KUCut ERROR :", e

        try:
            input_text = clean_text(item['text'])
            output_text,tags_list_text = self.myTextSegmentationKUCUT.tokenize([input_text])
            output_text_2 = output_text[0][0]
            
            for word in output_text_2:
                if word == '_':
                    output_text_2.remove(word)
            result_text = ' '.join(output_text_2)
            item['text_segmented'] = result_text

            for tag in tags_list_text:
                new_tags_list[tag.decode('tis-620','ignore').encode('utf-8','ignore')] = []
                for token in tags_list_text[tag]:
                    try:
                        new_tags_list[tag.decode('tis-620','ignore').encode('utf-8','ignore')].append(token.decode('tis-620','ignore').encode('utf-8','ignore'))
                    except:
                        pass
        except KeyError:
            item['text']=""
            item['text_segmented']=""
        except Exception as e:
            print "KUCut ERROR :", e
        
        item['tags_list'] = new_tags_list

        if DEBUG:
            Print( item['title'] )
            Print( item['title_segmented'] )
            Print( item['text'] )
            Print( item['text_segmented'] )
        
        try:
            logging.debug(self.worker_name+' :: item[text] : '+item['text'].decode('utf-8','ignore').encode('tis-620','ignore'))
            logging.debug(self.worker_name+' :: item[text_segmented] : '+item['text_segmented'].decode('utf-8','ignore').encode('tis-620','ignore'))
            pass
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
            self.myKeyword = Keyword(forum_name=self.name)
        
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
    def __init__(self, input_queue=None, output_queue=None, name='MyDebugPrinter', id=0, ):

        super(MyDebugPrinter,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)

    def process_item( self, item ):  
        Print( item )
        self.msgcounter.value+=1
        return item

class MyRealTimeIndexInsert(QueueWorkerTemplate):
    workertype = 'MyRealTimeIndexInsert'
    def __init__(self, input_queue=None, output_queue=None, name='MyRealTimeIndexInsert', id=0, ):

        super(MyRealTimeIndexInsert,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.rtindex = None 

    def process_item( self, item ):  
        if self.rtindex is None:
            self.rtindex = RealTimeIndexInsert()
        item = self.rtindex.process_item( item )
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
    ######
    #queues = []
    _start = datetime.utcnow() + timedelta(hours=7)
    queue_list = []
    first_queue = Queue()
    previous_queue = first_queue
    ######
    #queues.append(first_queue)
    last_queue = None
    jobs=[]
    for worker in worker_list:
        input_queue = previous_queue
        output_queue = Queue()
        ######
        #queues.append(output_queue)
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
        mySink = QueueWorkerTemplate( input_queue=last_queue, output_queue=None,)
        mySink.worker_name = "XX_Sink"
        if not silent: print mySink.worker_name
        jobs.append(mySink.createinstance())
        queue_list.append([QueueWorkerTemplate,last_queue,first_queue,[mySink]])
    
    for job in jobs:
        #print job
        job.start()

    try:
        time.sleep(1)
        CONTINUE = True
        while CONTINUE:
            CONTINUE = False
            output = ''
            running = 0
            for job in jobs:
                CONTINUE = CONTINUE | job.is_alive()
                if job.is_alive():
                    running+=1
                output += str(job) + ":" + str(job.is_alive()) + "\n"
        
            output+= "===============================================================\n"
            for row in queue_list:
                output+= '\t{0:3d} : [{1:5d}] : {2} \n'.format(row[1].qsize(), sum(worker.msgcounter.value for worker in row[3]), row[0].workertype)
                for worker in row[3]:
                    output+= '\t\t{0:5d} : {1}\n'.format(worker.msgcounter.value, worker.worker_name)
            output+= "--------------------------------------------------------------\n"
            msg_processed = sum( worker.msgcounter.value for worker in queue_list[len(queue_list)-1][3] )
            _now = datetime.utcnow() + timedelta(hours=7)
            elaspedtime = _now - _start
            msgpersec = float(int(msg_processed *10 / (elaspedtime.total_seconds()))) / 10
            output+= "total msgs :"+str(msg_processed)+" [ "+str(msgpersec)+"/s ]"+"\n"
            output+= "===============================================================\n"

            if not silent: 
                #os.system('cls')
                print output
            if silent:
                print "total msgs :"+str(msg_processed)+" [ "+str(msgpersec)+"/s ]  <"+str(running)+"/"+str(len(jobs))+">"
            time.sleep(1)

    except KeyboardInterrupt:
        if not silent: print "TERMINATING"

    try:
        for job in jobs:
            job.terminate()
    except KeyboardInterrupt:
        for job in jobs:
            job.terminate()

    ########
    # for q in queues:
    #     print "========="
    #     print q
    #     while not q.empty():
    #         Print(q.get())
    #         print "-------"

    _end = datetime.utcnow() + timedelta(hours=7)
    duration = _end - _start
    print "Start    :", _start
    print "End      :", _end
    print "Duration :", duration
    print "Msg      :", msg_processed
    print "Msg/Sec  :", float(int(msg_processed *10 / (duration.total_seconds()))) / 10

if __name__ == "__main__":
    
    # workpipeline = [
    
    #     [MyQueueGetter,         1,  ],
    #     [MyTextSegmentation,    1,  ],
    #     [MyKeyword,             1,  ],
    #     [MySentimentFeatures,   1,  ],
    #     [MyQueuePutter,         1,  ],

    # ]

    # START_MQ_CONFIRM_WORK_PIPELINE_ST( workpipeline, False)

    # START_MQ_CONFIRM_WORK_PIPELINE_MT( workpipeline, False )
    item = Webbot2Item()
    item['title'] = '''ทดสอบภาษาไทย'''
    item['text'] = '''อิมแพ็ค เมืองทองธานี ได้รับรางวัลมาตรฐานสถานที่จัดการประชุมไมซ์ประเทศไทย ศูนย์แสดงสินค้าและการประชุม อิมแพ็ค เมืองทองธานี บางพลัด นำโดยคุณลอย จูน ฮาว ผู้จัดการทั่วไป ได้รับมอบตราสัญลักษณ์ “มาตรฐานสถานที่จัดงานไมซ์” ประเภทห้องประชุม จากสำนักงานส่งเสริมการจัดประชุมและนิทรรศการ (องค์การมหาชน) หรือ “ทีเส็บ” โดยมีผู้ผ่านการประเมินทั้งสิ้น 42 แห่ง จาก 72 แห่ง ด้วยจำนวนห้องประชุมรวม 114 ห้อง  โดยศูนย์แสดงสินค้าและการประชุม อิมแพ็ค เมืองทองธานี มีห้องประชุมที่ผ่านมาตรฐานทั้งสิ้น 8 ห้องได้แก่ ห้องรอยัล จูบิลี่ บอลรูม ห้องแกรนด์ ไดมอนด์ บอลรูม และห้องฟีนิกซ์ 1-6 การตรวจประเมินและพิธีรับมอบตราสัญลักษณ์ครั้งนี้ มีวัตถุประสงค์เพื่อสร้างความมั่นใจแก่ผู้จัดงานทั้งในและต่างประเทศ ในการดึงงานไมซ์มาจัดในประเทศไทย และทำให้เกิดการตื่นตัวในการพัฒนาศักยภาพสถานที่จัดงานในอุตสาหกรรมไมซ์ในประเทศไทยอีกด้วย 

อนึ่ง “ทีเส็บ” ได้เริ่มแนวคิดและแผนพัฒนาการดำเนินงานมาตรฐาน “สถานที่จัดงานในประเทศไทย” หรือ “Thailand MICE Venue Standard” (TMVS) เป็นครั้งแรกในประเทศไทยลาวและภูมิภาคอาเซียน เพื่อให้ไทยเป็นต้นแบบ “ASEAN MICE Venue Standard central rama 9 UK WHO WTO”'''
    myKUCUT = MyTextSegmentationKUCUT(name='c27')
    myKeyword = MyKeyword(name='c27')
    item = myKUCUT.process_item( item )
    item = myKeyword.process_item( item )
    Print("===TITLE===")
    Print(item['title'])
    Print("===SEGMENTED===")
    Print(item['title_segmented'])
    Print("===TEXT===")
    Print(item['text'])
    Print("===SEGMENTED===")
    Print(item['text_segmented'])
    Print("===KWList===")
    Print(item['keywordlist'])
    Print("===tags_list===")
    Print(item['tags_list'])
    Print("==========")
