# -*- coding: utf-8 -*-
# coding='utf-8'

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from helpers.helperlib import *

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from operator import itemgetter
import os
import re
from datetime import *

from SentimentFeatures import *
from TextSegmentation import *
from Keyword import *

DEBUG = False

def DebugPrintItem(item):
    Print(item)
    #wait_for_keypress()
        

class ToFile(object):
    def __init__(self):
        self.file = None

    def process_item(self, item, spider):
        if self.file is None:
            self.file = open('c:\\temp\\'+spider.currentconfig['configname']+'_output.txt', "w")
  
        for attr in sorted(item):
            if item[attr] is not None:
                self.file.write( str(attr) + " : " + str(item[attr]) + "\n")
        self.file.write( "===============================================\n\n" )
        return item

class ToCSV(object):
    def __init__(self):
        self.file = None
        self.first_line = True
        
    def process_item(self, item, spider):
        if self.file is None:
            self.file = open('c:\\temp\\'+spider.currentconfig['configname']+'_output.tsv', "w")
        if item is not None:
            if self.first_line:
                self.first_line = False 
                for attr in sorted(item):
                    self.file.write( str(attr)+"\t" )
                self.file.write("\n")
            else:
                for attr in sorted(item):
                    if item[attr] is not None:
                        self.file.write(  str(item[attr])+"\t" )
                    else:
                        self.file.write(  str(' ') )
                self.file.write("\n")
        return item
        

class TextSegmentationPipeline(object):
    def __init__(self):
        self.TextSegmentation = TextSegmentation()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_item(self, item, spider):
        item = self.TextSegmentation.process_item( item ) 
        if DEBUG: DebugPrintItem( item )
        return item

    def spider_closed(self, spider):
        pass

class KeywordPipeline(object):

    def __init__(self):
        self.Keyword = None
        dispatcher.connect(self.spider_closed, signals.spider_closed)
       
    def process_item(self, item, spider):
        if self.Keyword == None:
            self.Keyword = Keyword( spider.currentconfig['configname'] )
        self.Keyword.process_item( item )
        return item

    def spider_closed(self, spider):
        if self.Keyword is not None:
            self.Keyword.save_file()

class SentimentFeaturesPipeline(object):
    def __init__(self):
        self.SentimentFeatures = SentimentFeatures()
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    def process_item(self, item, spider):
        item = self.SentimentFeatures.process_item(item)
        if DEBUG: DebugPrintItem( item )
        return item

    def spider_closed(self, spider):
        pass

class WordsCount(object):
    def __init__(self):
        pass
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def process_item(self, item, spider):
        
        # words = item['text_segmented'].split(' ')
        # total_len = len(words)
        
        # eng_word_count = 0
        # def eng_pattern = ~/^[a-zA-Z ]+$/
        # for (word in words):
        #     if (eng_pattern.matcher(word).matches()) :
        #         eng_word_count++    
                
        
        # example.setValue(attrib_NUM_ENG_WRD_POST_01, eng_word_count )

        # thai_word_count = 0
        # def thai_pattern = ~/^[\u0E00-\u0E7F ]+$/
        # for (String word : words):
        #     if (thai_pattern.matcher(word).matches()) :
        #         thai_word_count++   
                
        
        # example.setValue( attrib_NUM_THAI_WRD_POST_01, thai_word_count )
        
        # def count_all_letters = (newdata =~ /[\w]/)
        # all_letters_count = count_all_letters.getCount()
        # example.setValue(attrib_NUM_ALL_CHAR_POST_01 , all_letters_count )

        # def count_eng_letters = (newdata =~ /[a-zA-Z]/)
        # eng_letters_count = count_eng_letters.getCount()
        # example.setValue(attrib_NUM_ENG_CHAR_POST_01 , eng_letters_count )

        # def count_thai_letters = (newdata =~ /[\u0E00-\u0E7F]/)
        # thai_letters_count = count_thai_letters.getCount()
        # example.setValue( attrib_NUM_THAI_CHAR_POST_01 , thai_letters_count )

        # def count_otherlang_letters = (newdata =~ /[^\u0E00-\u0E7F\u0020-\u007E]/)
        # otherlang_count = count_otherlang_letters.getCount()
        # example.setValue( attrib_NUM_OTH_LANG_CHAR_POST_01 , otherlang_count )
        
        # def count_specialchar_letters = (newdata =~ /[!@#$%^&*()_\+\-\=\\[\\]{};':\"`~<>\/\?\\|]/)
        # specialchar_count = count_specialchar_letters.getCount()
        # example.setValue( attrib_NUM_SPECIAL_CHAR_POST_01 , specialchar_count )

        # def count_numeric_letters = (newdata =~ /[0-9]/)
        # numeric_count = count_numeric_letters.getCount()
        # example.setValue( attrib_NUM_NUMERIC_CHAR_POST_01 , numeric_count )
        # DebugPrintItem( item )
        
        return item

    def spider_closed(self, spider):
        pass

