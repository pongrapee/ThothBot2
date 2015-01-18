# -*- coding: utf-8 -*-
# coding='utf-8'

from pipelines import *
from helpers.helperlib import *
from BaseInMemQueueWorker import *
from items import Webbot2Item
import time


if __name__ == "__main__":
    
    workpipeline = [
    
        [MyQueueGetter,         1],
        [MyTextSegmentation,    2],
        [MyKeyword,             2],
        [MySentimentFeatures,   2],
        [MyQueuePutter,         2],

    ]

    START_WORK_PIPELINE( workpipeline )

