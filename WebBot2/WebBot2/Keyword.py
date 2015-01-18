# -*- coding: utf-8 -*-
# coding='utf-8'

from helpers.helperlib import *
import logging
import os
import tfidf
from datetime import *


DEBUG = False
THRESHOLD = 0.03

class Keyword(object):
    def __init__(self, forum_name):
        self.forum_name = forum_name
        
        self.corpus = 'tfidf_corpus.txt'
        self.stop = 'tfidf_new_stop.txt'

        self.corpus_files_list = self.get_corpus_files_list()

        self.current_run_tfidf = tfidf.TfIdf( corpus_filename = None, stopword_filename = 'c:\\temp\\tfidf_stop.txt', DEFAULT_IDF = 1.5 )
        self.recent_forum_tfidf = tfidf.TfIdf( corpus_filename = self.corpus_files_list, stopword_filename = 'c:\\temp\\tfidf_stop.txt', DEFAULT_IDF = 1.5 )

    def get_corpus_files_list(self):

        files_with_path = []
        for file in [f for f in os.listdir('c:\\temp') if re.match(self.forum_name+'_[0-9_]*.txt',f)]:
            files_with_path.append('c:\\temp\\'+file)
        files_with_path.sort(key=lambda x: os.path.getmtime(x))
        files_with_path.reverse()

        for file in files_with_path[:25]:
            logging.debug("open file",file)

        return files_with_path[:25]

    def save_file(self):
        now = datetime.utcnow() + timedelta(hours=7)
        now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
     
        if self.current_run_tfidf is not None:
            self.current_run_tfidf.save_corpus_to_file( 'c:\\temp\\'+self.forum_name+"_"+now_str+".txt", "currentrun_stop_diff.txt", find_diff_only=True )

    def process_item(self,item):
        self.current_run_tfidf.add_input_document(item['text_segmented'])
        self.recent_forum_tfidf.add_input_document(item['text_segmented'])
        
        keywords = self.recent_forum_tfidf.get_doc_keywords(item['text_segmented'])
        keywordlist = []
        for key, value in keywords[0:14]:
            if value >= THRESHOLD:
                keywordlist.append( key )
        logging.debug("keyword :")
        for keyword in keywordlist:
            logging.debug(keyword.decode('utf-8','ignore').encode('tis-620','ignore'))
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
