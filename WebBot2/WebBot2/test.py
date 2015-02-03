# -*- coding: utf-8 -*-
# coding='utf-8'

from WorkerImport import *
clientid = 0
class MySQLGetterCurrentClient(MySQLGetter):
    def __init__(self,input_queue=None, output_queue=None):
        super(MySQLGetterCurrentClient,self).__init__(
            SQLSTATEMENT="SELECT `post_id`, `subject_name` as `subject`, `post_date` as `datetime`, `body` as `text`, `type`, `author`, `group`, `facebook_page_name` as `page_id`, `likes`, `shares`, `mood` as `mood_original` FROM facebook_c"+str(clientid)+" WHERE `post_id` {0} AND `post_date` > '2015-01-01' ORDER BY `post_id` DESC LIMIT 1000;",input_queue=input_queue, output_queue=output_queue)
class MyKeywordCurrentClient(MyKeyword):
    def __init__(self,input_queue=None, output_queue=None):
        super(MyKeywordCurrentClient,self).__init__(name='c'+str(clientid),input_queue=input_queue, output_queue=output_queue)
class MyCSVPutterCurrentClient(MyCSVPutter):
    def __init__(self,input_queue=None, output_queue=None):
        super(MyCSVPutterCurrentClient,self).__init__(name='c'+str(clientid),input_queue=input_queue, output_queue=output_queue)


if __name__ == "__main__":
    
    for id in range(140, 141):
        print clientid
        clientid = id
        workpipeline = [
            
            [MySQLGetterCurrentClient,          1],
            [MyTextSegmentation,                2],
            #[MyDebugPrinter,        1],
            [MyKeywordCurrentClient,            2],
            [MyCSVPutterCurrentClient,          1],
            #[MyDebugPrinter,        1],
        ]

        START_MQ_CONFIRM_WORK_PIPELINE_ST( worker_list=workpipeline, confirm_needed=False)

        START_MQ_CONFIRM_WORK_PIPELINE_MT( worker_list=workpipeline, confirm_needed=False)
