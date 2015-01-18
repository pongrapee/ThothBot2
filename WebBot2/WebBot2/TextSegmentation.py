# -*- coding: utf-8 -*-
# coding='utf-8'

from helpers.helperlib import *
import logging

from subprocess import Popen, PIPE, STDOUT

DEBUG = False

class TextSegmentation(object):
    
    def __init__(self):
        pass

    def process_item(self,item):
        exe = Popen(['swath.exe'], cwd=r'C:\\temp\\swath', stdout=PIPE, stdin=PIPE, stderr=None)
        if exe is not None:
            swathinput = item['text']
            swathoutput = "Error Calling Swath"
            if DEBUG: Print( swathinput )
            swathoutput = (exe.communicate( swathinput.decode('utf-8','ignore').encode('tis-620','ignore') )[0]).decode('tis-620','ignore').encode('utf-8','ignore')
            item['text_segmented'] = ' '.join(swathoutput.split('|'))
            item['text_segmented'] = re.sub('([\s]){2,}', ' ', item['text_segmented'] )
            if DEBUG: Print( item['text_segmented'] )
        else:
            if DEBUG: print "Error openning SWATH"
        return item

if __name__ == "__main__":

    item = {}
    item['text'] = '''ทดสอบภาษาไทย'''
    myTextSegmentation = TextSegmentation()
    myTextSegmentation.process_item(item)
    Print(item)
