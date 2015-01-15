# -*- coding: utf-8 -*-
# coding='utf-8'

from pipelines import *
from helpers.helperlib import *
from BaseInMemQueueWorker import *

if __name__ == "__main__":
    
    jobs=[]
    Q1 = Queue()
    Q2 = Queue()
    Q3 = Queue()
    
    myQueueWorker = MyQueueGetter(input_queue=None, output_queue=Q1)
    jobs.append(myQueueWorker.createinstance())
    
    myTextSegmentation = MyTextSegmentation(input_queue=Q1, output_queue=Q2)
    jobs.append(myTextSegmentation.createinstance())


    for job in jobs:
        job.start()

    try:
        while True:
            for job in jobs:
                job.join(30)
    except KeyboardInterrupt:
        print "TERMINATING"

    for job in jobs:
        job.terminate()
