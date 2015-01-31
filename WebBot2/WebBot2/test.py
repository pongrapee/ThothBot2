# -*- coding: utf-8 -*-
# coding='utf-8'

from WorkerImport import *


# def MySQLGetterSpeficClient(clientid):
#     SQLSTATEMENT = 'SELECT `post_id`, `subject_name` as `subject`, `post_date` as `datetime`, `body` as `text`, `type`, `author`, `group`, `facebook_page_name` as `page_id`, `likes`, `shares`, `mood` as `mood_original` FROM facebook_c'+str(clientid)+' LIMIT 1000;'
        
#     MySQLGetter(SQLSTATEMENT=SQLSTATEMENT,)

if __name__ == "__main__":
    
    for clientid in range(140, 150):
        print clientid
        class MySQLGetterCurrentClient(MySQLGetter):
            def __init__(self):
                super(MySQLGetterCurrentClient,self).__init__(
                    SQLSTATEMENT='SELECT `post_id`, `subject_name` as `subject`, `post_date` as `datetime`, `body` as `text`, `type`, `author`, `group`, `facebook_page_name` as `page_id`, `likes`, `shares`, `mood` as `mood_original` FROM facebook_c'+str(clientid)+' LIMIT 1000;')
        class MyKeywordCurrentClient(MyKeyword):
            def __init__(self):
                super(MyKeywordCurrentClient,self).__init__(name='c'+str(clientid))
        class MyCSVPutterCurrentClient(MyCSVPutter):
            def __init__(self):
                super(MyCSVPutterCurrentClient,self).__init__(name='c'+str(clientid))

        workpipeline = [
            
            [MySQLGetterCurrentClient,          1],
            [MyTextSegmentation,                1],
            [MyKeywordCurrentClient,            1],
            [MyCSVPutterCurrentClient,          1],
            #[MyDebugPrinter,        1],
        ]

        START_MQ_CONFIRM_WORK_PIPELINE_ST( workpipeline, False)

        #START_MQ_CONFIRM_WORK_PIPELINE_MT( workpipeline, False )
