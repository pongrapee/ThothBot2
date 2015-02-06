# -*- coding: utf-8 -*-
# coding='utf-8'

from WorkerImport import *

if __name__ == "__main__":
    
    for client_id in [27]: #range(141, 142): #[156]: #range(140, 141):
        print client_id
        workpipeline = [
            
            [MySQLGetter,          1],
            [MyTextSegmentation,   5],
            [MyKeyword,            5],
            #[MyCSVPutter,          1],
            #[MySentimentFeatures,  1],
            #[MyDebugPrinter,        1],
            #[MyDebugFilePutter,    1],
        ]

        START_MQ_CONFIRM_WORK_PIPELINE_MT( worker_list=workpipeline, confirm_needed=False, client_id='c'+str(client_id), silent=False )

        #START_MQ_CONFIRM_WORK_PIPELINE_ST( worker_list=workpipeline, confirm_needed=False, client_id='c'+str(client_id), silent=False )
