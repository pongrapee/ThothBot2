# -*- coding: utf-8 -*-
# coding='utf-8'

from WorkerImport import *

if __name__ == "__main__":
    
    for client_id in [141]: #range(141, 142): #[156]: #range(140, 141):
        print client_id
        workpipeline = [
            
            [MySQLGetter,          1],
            #[MyTextSegmentation,   5],
            #[MyDebugFilePutter,    1],
            #[MyTextSegmentationKUCUT, 2],
            #[MyKeyword,            3],
            #[MyDebugFilePutter,    1],
            [MyDataValidation,     1],
            #[MyCSVPutter,          1],
            #[MySentimentFeatures,  1],
            #[MyDebugPrinter,       1],
            
        ]

        #START_MQ_CONFIRM_WORK_PIPELINE_MT( worker_list=workpipeline, confirm_needed=False, client_id='c'+str(client_id), silent=True )

        START_MQ_CONFIRM_WORK_PIPELINE_ST( worker_list=workpipeline, confirm_needed=False, client_id='c'+str(client_id), silent=False )
