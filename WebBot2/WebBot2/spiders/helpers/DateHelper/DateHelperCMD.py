# -*- coding: utf-8 -*-
# coding='utf-8'

global debug
debug=0

import sys
from DateHelper import *

if __name__ == "__main__":
    if len(sys.argv)<=1: print 'No arguments!'
    input = sys.argv[1]
    print 'Processing :', input
    print DecodeDateTime( input=input.decode('tis-620','ignore').encode('utf-8','ignore'), today=datetime.now(), preferreddateformat="" )