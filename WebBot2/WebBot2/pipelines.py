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

    # Print( 'URL          :', item['url'] )
    # Print( 'PageSig      :', item['pagesignature'] )
    # Print( 'PostSig      :', item['postsignature'] )
    # Print( 'Title        :', item['title'] )    
    # Print( 'Text         :', item['text'] )
    # Print( 'TxtSegmented :', item['text_segmented'] )
    # Print( 'Keywordlist  :', item['keywordlist'] )
    # Print( 'Author       :', item['author'] )
    # Print( 'Raw Datetime :', item['rawdatetime'] )
    # Print( 'PostDate     :', item['datetime'] )
    # Print( 'ParseDate    :', item['parse_date'] )
    # Print( 'Type         :', item['type'] )
    # Print( 'Digest       :', item['digest'] )
    # Print( 'Sale         :', item['sale'] )
    # Print( 'Spam         :', item['spam'] )
    # Print( 'SellScore    :', item['sellscore'] )
    # Print( 'SpamScore    :', item['spamscore'] )
    for attr in sorted(item):
        PrintNoNewLine( attr )
        PrintNoNewLine( ":" )
        Print(item[attr])
        

class ToFile(object):
    def __init__(self):
        self.num_docs = 0
        self.file = None

    def process_item(self, item, spider):
        if self.file is None:
            self.file = open(spider.currentconfig['configname']+'_output.txt', "w")
        # self.file.write(
            # 'URL          :'+ item['url'] + "\n" + 
            # 'PageSig      :'+ item['pagesignature'] + "\n" + 
            # 'PostSig      :'+ item['postsignature'] + "\n" +
            # 'Title        :'+ item['title'] + "\n" +    
            # 'Text         :'+ item['text'] + "\n" +
            # 'TxtSegmented :'+ item['text_segmented'] + "\n" +
            # 'Keywordlist  :'+ item['keywordlist'] + "\n" +
            # 'Author       :'+ item['author'] + "\n" +
            # 'Raw Datetime :'+ item['rawdatetime'] + "\n" +
            # 'PostDate     :'+ item['datetime'] + "\n" +
            # 'ParseDate    :'+ item['parse_date'] + "\n" +
            # 'Type         :'+ item['type'] + "\n" +
            # 'Digest       :'+ str(item['digest']) + "\n" +
            # 'Sale         :'+ str(item['sale']) + "\n" +
            # 'Spam         :'+ str(item['spam']) + "\n" +
            # 'SellScore    :'+ str(item['sellscore']) + "\n" +
            # 'SpamScore    :'+ str(item['spamscore']) + "\n" +
            # "==========================================\n\n"
            # )
        for attr in sorted(item):
            self.file.write( "%s : %s\n" % attr % item[attr])
            self.file.write( "===============================================\n\n"


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
        pass
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def process_item(self, item, spider):
        good_emo_wordlist = { 
            ur'good':3,  
            ur'ok':1, 
            ur'ดี':3, 
            ur'ชอบ':2,
            ur'เฟรม':2,
            ur'จักรยาน':2,
            ur'เป็น':2,
            ur'ครับ':2,
            ur'ค่ะ':2,
            ur'สนุก':2,
            ur'เสือ':2,
            ur'ภูเขา':2,
            ur'รัก':3,
        }

        bad_emo_wordlist = {
            ur'แย่':1,
            ur'ห่วย':1,
        }

        words = item['text_segmented'].split(' ')
        #words = '''
        #ลอง ที่ไหน ยัง ไง ต้อง ชอบ เอา ดี รถ ไป เอง มี ราย ละเอียด มั้
        #- - ปั่น วัน ละ นิด จิต แจ่มใส -
        #'''.split(' ')
        #Print( words )
        total_len = len(words)

        all_emo_word_count = 0
        all_emo_word_count_f_10 = 0
        all_emo_word_count_f_20 = 0
        all_emo_word_count_f_30 = 0
        all_emo_word_count_f_60 = 0
        all_emo_word_count_f_100 = 0
        all_emo_word_count_f_150 = 0
        all_emo_word_count_l_10 = 0
        all_emo_word_count_l_20 = 0
        all_emo_word_count_l_30 = 0
        all_emo_word_count_l_60 = 0
        all_emo_word_count_l_100 = 0
        all_emo_word_count_l_150 = 0

        pos_emo_word_count = 0
        pos_emo_word_count_f_10 = 0
        pos_emo_word_count_f_20 = 0
        pos_emo_word_count_f_30 = 0
        pos_emo_word_count_f_60 = 0
        pos_emo_word_count_f_100 = 0
        pos_emo_word_count_f_150 = 0
        pos_emo_word_count_l_10 = 0
        pos_emo_word_count_l_20 = 0
        pos_emo_word_count_l_30 = 0
        pos_emo_word_count_l_60 = 0
        pos_emo_word_count_l_100 = 0
        pos_emo_word_count_l_150 = 0

        neg_emo_word_count = 0
        neg_emo_word_count_f_10 = 0
        neg_emo_word_count_f_20 = 0
        neg_emo_word_count_f_30 = 0
        neg_emo_word_count_f_60 = 0
        neg_emo_word_count_f_100 = 0
        neg_emo_word_count_f_150 = 0
        neg_emo_word_count_l_10 = 0
        neg_emo_word_count_l_20 = 0
        neg_emo_word_count_l_30 = 0
        neg_emo_word_count_l_60 = 0
        neg_emo_word_count_l_100 = 0
        neg_emo_word_count_l_150 = 0

        i = 0
        j = total_len
        avg_pos_dist = 0
        last_pos_emo_pos = 0
        for word in words:
            j-=1
            for row in good_emo_wordlist:
                # print "DEBUG : Checking : "
                # print word.decode('utf-8','ignore').encode('tis-620','ignore')
                # print row.decode('utf-8','ignore').encode('tis-620','ignore')
                if word == row:
                    pos_emo_word_count+=1
                    all_emo_word_count+=1

                    ##find distance between pos emo
                    if (pos_emo_word_count == 1):
                        last_pos_emo_pos = i
                    
                    if (pos_emo_word_count > 1):
                        avg_pos_dist = (((avg_pos_dist * (pos_emo_word_count-2)) + (i - last_pos_emo_pos))/(pos_emo_word_count-1))
                        last_pos_emo_pos = i
                    
                    if (i<10):
                        pos_emo_word_count_f_10+=1
                        all_emo_word_count_f_10+=1
                    
                    if (i<20):
                        pos_emo_word_count_f_20+=1
                        all_emo_word_count_f_20+=1
                    
                    if (i<30):
                        pos_emo_word_count_f_30+=1
                        all_emo_word_count_f_30+=1
                    
                    if (i<60):
                        pos_emo_word_count_f_60+=1
                        all_emo_word_count_f_60+=1
                    
                    if (i<100):
                        pos_emo_word_count_f_100+=1
                        all_emo_word_count_f_100+=1
                    
                    if (i<150):
                        pos_emo_word_count_f_150+=1
                        all_emo_word_count_f_150+=1
                    
                    if (j<10):
                        pos_emo_word_count_l_10+=1
                        all_emo_word_count_l_10+=1
                    
                    if (j<20):
                        pos_emo_word_count_l_20+=1
                        all_emo_word_count_l_20+=1
                    
                    if (j<30):
                        pos_emo_word_count_l_30+=1
                        all_emo_word_count_l_30+=1
                    
                    if (j<60):
                        pos_emo_word_count_l_60+=1
                        all_emo_word_count_l_60+=1
                    
                    if (j<100):
                        pos_emo_word_count_l_100+=1
                        all_emo_word_count_l_100+=1
                    
                    if (j<150):
                        pos_emo_word_count_l_150+=1
                        all_emo_word_count_l_150+=1
            i+=1

        i = 0
        j = total_len
        avg_neg_dist = 0
        last_neg_emo_pos = 0
        for word in words:
            j-=1
            for row in bad_emo_wordlist:
                if word == row:
                    neg_emo_word_count+=1
                    all_emo_word_count+=1

                    ##find distance between neg emo
                    if( neg_emo_word_count == 1 ):
                        last_neg_emo_pos = i
                    
                    if( neg_emo_word_count > 1 ):
                        avg_neg_dist = (((avg_neg_dist * (neg_emo_word_count-2)) + (i - last_neg_emo_pos))/(neg_emo_word_count-1))
                        last_neg_emo_pos = i
                    

                    if (i<10):
                        neg_emo_word_count_f_10+=1
                        all_emo_word_count_f_10+=1
                    
                    if (i<20):
                        neg_emo_word_count_f_20+=1
                        all_emo_word_count_f_20+=1
                    
                    if (i<30):
                        neg_emo_word_count_f_30+=1
                        all_emo_word_count_f_30+=1
                    
                    if (i<60):
                        neg_emo_word_count_f_60+=1
                        all_emo_word_count_f_60+=1
                    
                    if (i<100):
                        neg_emo_word_count_f_100+=1
                        all_emo_word_count_f_100+=1
                    
                    if (i<150):
                        neg_emo_word_count_f_150+=1
                        all_emo_word_count_f_150+=1
                    
                    if (j<10):
                        neg_emo_word_count_l_10+=1
                        all_emo_word_count_l_10+=1
                    
                    if (j<20):
                        neg_emo_word_count_l_20+=1
                        all_emo_word_count_l_20+=1
                    
                    if (j<30):
                        neg_emo_word_count_l_30+=1
                        all_emo_word_count_l_30+=1
                    
                    if (j<60):
                        neg_emo_word_count_l_60+=1
                        all_emo_word_count_l_60+=1

                    if (j<100):
                        neg_emo_word_count_l_100+=1
                        all_emo_word_count_l_100+=1

                    if (j<150):
                        neg_emo_word_count_l_150+=1
                        all_emo_word_count_l_150+=1
            i+=1      

        if (total_len > 0): 
            ratio_all_emo_vs_total = all_emo_word_count / total_len
            ratio_pos_emo_vs_total = pos_emo_word_count / total_len
            ratio_neg_emo_vs_total = neg_emo_word_count / total_len
        else:
            ratio_all_emo_vs_total = 0
            ratio_pos_emo_vs_total = 0
            ratio_neg_emo_vs_total = 0
        

        if (neg_emo_word_count > 0):
            ratio_pos_emo_vs_neg_emo = pos_emo_word_count / neg_emo_word_count 
        else:
            ratio_pos_emo_vs_neg_emo = 999
        

        if (neg_emo_word_count_f_10 > 0):
            ratio_pos_emo_vs_neg_emo_f_10 = pos_emo_word_count_f_10 / neg_emo_word_count_f_10   
        else:
            ratio_pos_emo_vs_neg_emo_f_10 = 999

        if (neg_emo_word_count_f_20 > 0):
            ratio_pos_emo_vs_neg_emo_f_20 = pos_emo_word_count_f_20 / neg_emo_word_count_f_20   
        else:
            ratio_pos_emo_vs_neg_emo_f_20 = 999

        if (neg_emo_word_count_f_30 > 0):
            ratio_pos_emo_vs_neg_emo_f_30 = pos_emo_word_count_f_30 / neg_emo_word_count_f_30   
        else:
            ratio_pos_emo_vs_neg_emo_f_30 = 999

        if (neg_emo_word_count_f_60 > 0):
            ratio_pos_emo_vs_neg_emo_f_60 = pos_emo_word_count_f_60 / neg_emo_word_count_f_60   
        else:
            ratio_pos_emo_vs_neg_emo_f_60 = 999

        item['all_emo_word_count'] = all_emo_word_count 
        item['all_emo_word_count_f_10'] = all_emo_word_count_f_10 
        item['all_emo_word_count_f_20'] = all_emo_word_count_f_20 
        item['all_emo_word_count_f_30'] = all_emo_word_count_f_30 
        item['all_emo_word_count_f_60'] = all_emo_word_count_f_60 
        item['all_emo_word_count_f_100'] = all_emo_word_count_f_100 
        item['all_emo_word_count_f_150'] = all_emo_word_count_f_150 
        item['all_emo_word_count_l_10'] = all_emo_word_count_l_10 
        item['all_emo_word_count_l_20'] = all_emo_word_count_l_20 
        item['all_emo_word_count_l_30'] = all_emo_word_count_l_30 
        item['all_emo_word_count_l_60'] = all_emo_word_count_l_60 
        item['all_emo_word_count_l_100'] = all_emo_word_count_l_100 
        item['all_emo_word_count_l_150'] = all_emo_word_count_l_150 

        item['pos_emo_word_count'] = pos_emo_word_count 
        item['pos_emo_word_count_f_10'] = pos_emo_word_count_f_10 
        item['pos_emo_word_count_f_20'] = pos_emo_word_count_f_20 
        item['pos_emo_word_count_f_30'] = pos_emo_word_count_f_30 
        item['pos_emo_word_count_f_60'] = pos_emo_word_count_f_60 
        item['pos_emo_word_count_f_100'] = pos_emo_word_count_f_100 
        item['pos_emo_word_count_f_150'] = pos_emo_word_count_f_150 
        item['pos_emo_word_count_l_10'] = pos_emo_word_count_l_10 
        item['pos_emo_word_count_l_20'] = pos_emo_word_count_l_20 
        item['pos_emo_word_count_l_30'] = pos_emo_word_count_l_30 
        item['pos_emo_word_count_l_60'] = pos_emo_word_count_l_60 
        item['pos_emo_word_count_l_100'] = pos_emo_word_count_l_100 
        item['pos_emo_word_count_l_150'] = pos_emo_word_count_l_150 

        item['neg_emo_word_count'] = neg_emo_word_count 
        item['neg_emo_word_count_f_10'] = neg_emo_word_count_f_10 
        item['neg_emo_word_count_f_20'] = neg_emo_word_count_f_20 
        item['neg_emo_word_count_f_30'] = neg_emo_word_count_f_30 
        item['neg_emo_word_count_f_60'] = neg_emo_word_count_f_60 
        item['neg_emo_word_count_f_100'] = neg_emo_word_count_f_100 
        item['neg_emo_word_count_f_150'] = neg_emo_word_count_f_150 
        item['neg_emo_word_count_l_10'] = neg_emo_word_count_l_10 
        item['neg_emo_word_count_l_20'] = neg_emo_word_count_l_20 
        item['neg_emo_word_count_l_30'] = neg_emo_word_count_l_30 
        item['neg_emo_word_count_l_60'] = neg_emo_word_count_l_60 
        item['neg_emo_word_count_l_100'] = neg_emo_word_count_l_100 
        item['neg_emo_word_count_l_150'] = neg_emo_word_count_l_150 

        item['avg_pos_dist'] = avg_pos_dist 
        item['avg_neg_dist'] = avg_neg_dist 
        item['ratio_all_emo_vs_total'] = ratio_all_emo_vs_total 
        item['ratio_pos_emo_vs_total'] = ratio_pos_emo_vs_total 
        item['ratio_neg_emo_vs_total'] = ratio_neg_emo_vs_total 
        item['ratio_pos_emo_vs_neg_emo'] = ratio_pos_emo_vs_neg_emo 
        item['ratio_pos_emo_vs_neg_emo_f_10'] = ratio_pos_emo_vs_neg_emo_f_10 
        item['ratio_pos_emo_vs_neg_emo_f_20'] = ratio_pos_emo_vs_neg_emo_f_20 
        item['ratio_pos_emo_vs_neg_emo_f_30'] = ratio_pos_emo_vs_neg_emo_f_30 
        item['ratio_pos_emo_vs_neg_emo_f_60'] = ratio_pos_emo_vs_neg_emo_f_60 
        
        DebugPrintItem( item )
        
        return item

    def spider_closed(self, spider):
        pass

class WordsCount(object):
    def __init__(self):
        pass
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def process_item(self, item, spider):
        
        words = item['text_segmented'].split(' ')
        total_len = len(words)
        
        eng_word_count = 0
        def eng_pattern = ~/^[a-zA-Z ]+$/
        for (word in words):
            if (eng_pattern.matcher(word).matches()) :
                eng_word_count++    
                
        
        example.setValue(attrib_NUM_ENG_WRD_POST_01, eng_word_count )

        thai_word_count = 0
        def thai_pattern = ~/^[\u0E00-\u0E7F ]+$/
        for (String word : words):
            if (thai_pattern.matcher(word).matches()) :
                thai_word_count++   
                
        
        example.setValue( attrib_NUM_THAI_WRD_POST_01, thai_word_count )
        
        def count_all_letters = (newdata =~ /[\w]/)
        all_letters_count = count_all_letters.getCount()
        example.setValue(attrib_NUM_ALL_CHAR_POST_01 , all_letters_count )

        def count_eng_letters = (newdata =~ /[a-zA-Z]/)
        eng_letters_count = count_eng_letters.getCount()
        example.setValue(attrib_NUM_ENG_CHAR_POST_01 , eng_letters_count )

        def count_thai_letters = (newdata =~ /[\u0E00-\u0E7F]/)
        thai_letters_count = count_thai_letters.getCount()
        example.setValue( attrib_NUM_THAI_CHAR_POST_01 , thai_letters_count )

        def count_otherlang_letters = (newdata =~ /[^\u0E00-\u0E7F\u0020-\u007E]/)
        otherlang_count = count_otherlang_letters.getCount()
        example.setValue( attrib_NUM_OTH_LANG_CHAR_POST_01 , otherlang_count )
        
        def count_specialchar_letters = (newdata =~ /[!@#$%^&*()_\+\-\=\\[\\]{};':\"`~<>\/\?\\|]/)
        specialchar_count = count_specialchar_letters.getCount()
        example.setValue( attrib_NUM_SPECIAL_CHAR_POST_01 , specialchar_count )

        def count_numeric_letters = (newdata =~ /[0-9]/)
        numeric_count = count_numeric_letters.getCount()
        example.setValue( attrib_NUM_NUMERIC_CHAR_POST_01 , numeric_count )
        DebugPrintItem( item )
        
        return item

    def spider_closed(self, spider):
        pass

