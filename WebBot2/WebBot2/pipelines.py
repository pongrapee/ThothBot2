# -*- coding: utf-8 -*-
# coding='utf-8'

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from subprocess import Popen, PIPE, STDOUT
from helpers.helperlib import *
import tfidf
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from operator import itemgetter
import os
import re
from datetime import *
from WordCountFeatures import *

DEBUG = False

def get_corpus_files_list( forum_name = 'tfidf_corpus'):
    files = filter(os.path.isfile, os.listdir('.'))
    files = [f for f in files if re.match(forum_name+'_[0-9_]*.txt',f)]
    files.sort(key=lambda x: os.path.getmtime(x))
    files.reverse()
    if DEBUG:
        print "open file",files[:25]
    return files[:25]

def DebugPrintItem(item):
    for attr in sorted(item):
        if item[attr] is not None:
            PrintNoNewLine( attr )
            PrintNoNewLine( ":" )
            Print(item[attr])
        

class ToFile(object):
    def __init__(self):
        self.file = None

    def process_item(self, item, spider):
        if self.file is None:
            self.file = open(spider.currentconfig['configname']+'_output.txt', "w")
  
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
            self.file = open(spider.currentconfig['configname']+'_output.tsv', "w")
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
        

class TextSegmentation(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        exe = Popen(['swath.exe'], stdout=PIPE, stdin=PIPE, stderr=None)
        
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

class Keyword(object):

    CORPUS = 'tfidf_corpus.txt'
    NEW_STOPWORD = 'tfidf_new_stop.txt'
    FORUM_CORPUS = None

    def __init__(self):
        #self.global_tfidf = None
        self.current_run_tfidf = None
        #self.forum_tfidf = None
        self.five_most_recent_forum_tfidf = None
        self.forum_tfidf_filename = None
        self.corpus_files_list = None

        dispatcher.connect(self.spider_closed, signals.spider_closed)
    def process_item(self, item, spider):
        if self.forum_tfidf_filename is None:
            self.forum_tfidf_filename = spider.currentconfig['configname']+"tfidf"
        if self.corpus_files_list is None:
            self.corpus_files_list = get_corpus_files_list(self.forum_tfidf_filename)
        if self.FORUM_CORPUS is None:
            self.FORUM_CORPUS = self.forum_tfidf_filename+".txt"
        
        #if self.global_tfidf is None:
        #    self.global_tfidf = tfidf.TfIdf( corpus_filename = self.CORPUS, stopword_filename = self.STOPWORD, DEFAULT_IDF = 1.5 )
        if self.current_run_tfidf is None:
            self.current_run_tfidf = tfidf.TfIdf( corpus_filename = None, stopword_filename = 'tfidf_stop.txt', DEFAULT_IDF = 1.5 )
        #if self.forum_tfidf is None:
            #self.forum_tfidf = tfidf.TfIdf( corpus_filename = self.FORUM_CORPUS, stopword_filename = 'tfidf_stop.txt', DEFAULT_IDF = 1.5 )
        if self.five_most_recent_forum_tfidf is None:
            self.five_most_recent_forum_tfidf = tfidf.TfIdf( corpus_filename = self.corpus_files_list, stopword_filename = 'tfidf_stop.txt', DEFAULT_IDF = 1.5 )
        #self.global_tfidf.add_input_document(item['text_segmented'])
        self.current_run_tfidf.add_input_document(item['text_segmented'])
        self.five_most_recent_forum_tfidf.add_input_document(item['text_segmented'])
        #self.forum_tfidf.add_input_document(item['text_segmented'])
        
        active_tfidf = self.five_most_recent_forum_tfidf

        keywords = active_tfidf.get_doc_keywords(item['text_segmented'])
        #sorted(keywords, key=itemgetter(1), reverse=True)
        keywordlist = []
        for k,v in keywords[0:14]:
            #PrintNoNewLine( k )
            keywordlist.append( k )
        if DEBUG :
            print "keyword :",
            Print( keywordlist )

        item['keywordlist'] = ' '.join(keywordlist)
        if DEBUG:
            DebugPrintItem( item )
        return item

    def spider_closed(self, spider):
        now = datetime.utcnow() + timedelta(hours=7)
        now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
     
        #self.global_tfidf.save_corpus_to_file( self.CORPUS, self.NEW_STOPWORD )
        if self.current_run_tfidf is not None:
            self.current_run_tfidf.save_corpus_to_file( self.forum_tfidf_filename+"_"+now_str+".txt", "currentrun_stop_diff.txt", find_diff_only=True )
        #self.forum_tfidf.save_corpus_to_file( self.FORUM_CORPUS, "forum_stop_diff.txt", find_diff_only=True )

class EmoWordsCount(object):
    def __init__(self):
        self.EmoWordsCountFeature = EmoWordsCountFeature()
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    def process_item(self, item, spider):
        self.EmoWordsCountFeature.process_item(item)
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

