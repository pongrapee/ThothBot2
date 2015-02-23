# -*- coding: utf-8 -*-
# coding='utf-8'

from helpers.helperlib import *
import logging
import os
import tfidf
from datetime import *
import sqlite3
from multiprocessing import Value
import md5

DEBUG = False
THRESHOLD = 0.03
SECOND_LEVEL_KW = True

class Keyword(object):
    def __init__(self, forum_name):
        self.forum_name = forum_name
        
        self.corpus = 'tfidf_corpus.txt'
        self.stop = 'tfidf_new_stop.txt'

        self.corpus_files_list = self.get_corpus_files_list()
        self.current_run_tfidf = None
        self.recent_forum_tfidf = None
        self.global_keyword_list = None

        self.memdb = None
        self.counter = Value('i',0)

    def get_corpus_files_list(self):

        files_with_path = []
        for file in [f for f in os.listdir('c:\\temp\\idf') if re.match(self.forum_name+'_[0-9_]*.txt',f)]:
            files_with_path.append('c:\\temp\\idf\\'+file)
        files_with_path.sort(key=lambda x: os.path.getmtime(x))
        files_with_path.reverse()

        for file in files_with_path[:25]:
            logging.debug("open file",file)

        return files_with_path[:25]

    def save_file(self):
        now = datetime.utcnow() + timedelta(hours=7)
        now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
     
        if self.current_run_tfidf is not None:
            self.current_run_tfidf.save_corpus_to_file( 'c:\\temp\\idf\\'+self.forum_name+"_"+now_str+".txt", 'c:\\temp\\stop\\'+self.forum_name+"_stop_diff_"+now_str+".txt", find_diff_only=True )

        if self.global_keyword_list is not None:
            output_file = open("c:\\temp\\keywords\\"+self.forum_name+"keywords_tf_"+now_str+".txt", "w")
            for term, total_tf in sorted(self.global_keyword_list.items(),key=lambda x:x[1],reverse=True):
                output_file.write(term + ": " + str(total_tf) + "\n")

        if SECOND_LEVEL_KW:
            output_file = open("c:\\temp\\keywords\\"+self.forum_name+"keywords_secondlevel_"+now_str+".txt", "w")
            #print "saving 2nd level"
            cursor = self.memdb.cursor()
            final_list = sorted(self.global_keyword_list.items(),key=lambda x:x[1],reverse=True)[0:300]
            for word in final_list:
                for word2 in final_list:
                    if word[0].find(word2[0]) != -1:
                        final_list.remove(word2)
            for word in final_list:
                sqlstatement = "select `word1`, `word2`, `link_count` from wordlink where `word1` = '{word1}' or `word2` = '{word1}' order by `link_count` desc limit 200;".format(word1=word[0])

                cursor.execute( sqlstatement )
                results = cursor.fetchall()
                
                baseword = word[0]
                total=0
                # for result in results:
                #     total+=result[2]
                total = self.global_keyword_list[baseword]
                output_file.write( baseword+":"+str(total)+"\n" )
                for result in results:
                    if 1:
                        try:
                            out1 = result[0]
                            out2 = result[1]
                            # Print("======") 
                            # Print(baseword)
                            # Print( out1 )
                            # Print( out2 )
                            # Print("------") 
                            if out1 == baseword:  
                                output_file.write( "\t> "+out2+":"+str(result[2])+"\n" )
                                #Print(out2)
                            else:
                                output_file.write( "\t> "+out1+":"+str(result[2])+"\n" )
                                #Print(out1)
                            #Print("------") 
                        except:
                             pass
            cursor.close()
                
    def process_item(self, item):
        if self.current_run_tfidf == None:
            self.current_run_tfidf = tfidf.TfIdf( corpus_filename = None, stopword_filename = 'c:\\temp\\tfidf_stop.txt', DEFAULT_IDF = 1.5, prefix=self.forum_name )
        if self.recent_forum_tfidf == None:
            self.recent_forum_tfidf = tfidf.TfIdf( corpus_filename = self.corpus_files_list, stopword_filename = 'c:\\temp\\tfidf_stop.txt', DEFAULT_IDF = 1.5, prefix=self.forum_name )
        if self.global_keyword_list == None:
            self.global_keyword_list = {}


        self.current_run_tfidf.add_input_document(item['text_segmented'])
        keywords = self.recent_forum_tfidf.add_input_document_and_get_keywords(item['text_segmented'])
        
        keywordlist = []
        for key, value in keywords[0:59]:
            if value >= THRESHOLD:
                keywordlist.append( key )
        
        list1 = []
        list2 = []
        for word1 in keywordlist:
            list1.append(word1)
            list2.append(word1)

        for word1 in list1:
            #PrintWithLabel("checking",word1)
            for word2 in list2:
                if word1 != word2:
                    if word1.find(word2) != -1:
                        try:
                            #PrintWithLabel("Remove",word1)
                            keywordlist.remove(word1)
                        except ValueError:
                            pass

        logging.debug("keyword :")
        for keyword in keywordlist:
            logging.debug(keyword.decode('utf-8','ignore').encode('tis-620','ignore'))
            if keyword in self.global_keyword_list:
                self.global_keyword_list[keyword] += 1
            else:
                self.global_keyword_list[keyword] = 1

        if SECOND_LEVEL_KW:
            if self.memdb == None:
                self.memdb = sqlite3.connect(":memory:")
                cursor = self.memdb.cursor()
                sqlstatement = "CREATE TABLE IF NOT EXISTS wordlink( \
                                    `word_pair` VARCHAR(200) PRIMARY KEY NOT NULL,\
                                    `word1` VARCHAR(100) NOT NULL,\
                                    `word2` VARCHAR(100) NOT NULL,\
                                    `link_count` INTEGER DEFAULT '0');"
                cursor.execute( sqlstatement )
                sqlstatement = "Delete from wordlink;"
                cursor.execute( sqlstatement )
                self.memdb.commit()
                cursor.close()

            cursor = self.memdb.cursor()
            for keyword in keywordlist:
                if len(keyword) <= 1:
                    continue
                for keyword2 in keywordlist:
                    if len(keyword2) <= 1:
                        continue
                    if keyword != keyword2 and (keyword.find(keyword2)==-1) and (keyword2.find(keyword)==-1) :
                        if keyword < keyword2:
                            word1 = keyword
                            word2 = keyword2
                        else:
                            word2 = keyword
                            word1 = keyword2
                        
                        if DEBUG:
                            PrintNoNewLine(word1)
                            PrintNoNewLine("->")
                            Print(word2)
                        digest = md5.new((word1+word2)).hexdigest()
                        sqlstatement = "insert or ignore into wordlink (`word_pair`, `word1`, `word2`) values ( '{word3}', '{word1}', '{word2}');".format(
                            word1=word1,
                            word2=word2,
                            word3=digest,
                            )
                        
                        cursor.execute( sqlstatement )
                        sqlstatement = "update wordlink set `link_count`=`link_count`+1 where `word_pair`='{word3}';".format(
                            word3=digest,
                            )
                        cursor.execute( sqlstatement )
            self.memdb.commit()       
            cursor.close()
            self.counter.value += 1
            if self.counter.value % 1000 == 0:
                cursor = self.memdb.cursor()
                sqlstatement = "delete from wordlink where link_count <= 5;"
                cursor.execute( sqlstatement )
                self.memdb.commit()
                cursor.close()
        keywordlist=sorted(keywordlist)
        item['keywordlist'] = ' '.join(keywordlist)
        if DEBUG:
            Print( item )

        return item

if __name__ == "__main__":
    item = {}
    item['text_segmented'] = '''ผม อ่าน คอมเม้นท์ แล้ว รู้สึก ไม่ สบาย ใจ อยาก จะ บอก ว่า ไม่ เคย คิด ดิสเครดิส ใคร
ดี ใจ และ ขอบคุณ ด้วย ซ้ำ ที่ รัฐ และ กทม. เริ่ม ส่งเสริม เรื่อง จักรยาน อย่าง จริง จัง
แต่ ไหน ไหน ก็ ทำ แล้ว ก็ เลย อยาก ให้ ทาง ใช้ งาน ได้ จริง บกพร่อง ตรง ไหน เรา
เป็น ประชาชน หาก แจ้ง กระจาย ข่าว ได้ ก็ ช่วย กัน ถือ ว่า เป็น หน้า ที่ พลเมือง'''
    myKeyword = Keyword( forum_name='test' )
    myKeyword.process_item(item)
    myKeyword.save_file()
    Print(item)
