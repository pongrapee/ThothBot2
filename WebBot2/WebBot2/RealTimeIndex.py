# -*- coding: utf-8 -*-
# coding='utf-8'

import MySQLdb
from helpers.helperlib import *
from datetime import datetime
import time

class RealTimeIndexInsert( object ):
    
    def __init__(self, host="", port="", user="", passwd="", db=""):
        self.rt_host = "27.254.95.52"
        self.rt_port = 9307
        self.rt_user = "root"
        self.rt_pass = ""
        self.sqldb = MySQLdb.connect(   host=self.rt_host,
                                        port=self.rt_port,
                                        user=self.rt_user,
                                        passwd=self.rt_pass,
                                        db=db,
                                        use_unicode=True,
                                        charset="utf8",
                                            )
    
    def process_item(self, item):
        try:
            item['post_id']
            item['datetime']
            item['text_segmented']
            item['title_segmented']
            item['facebook_id']
            item['author']
            item['channel']

        except KeyError:
            return item
        cursor = self.sqldb.cursor()
        try:
            parse_date = datetime.strptime(item['datetime'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except:
            parse_date = datetime.strptime(item['datetime'], " %Y - %m - %d %H : %M : %S ").strftime("%Y-%m-%d %H:%M:%S")
        parse_date_unix = int(time.mktime(datetime.strptime(parse_date, "%Y-%m-%d %H:%M:%S").timetuple()) + 25200)

        #print parse_date_unix

        SQLStatement = "replace into rt_index_channel (id, parse_date, body, title, facebook_id, author, channel) VALUES ('{id}', '{parse_date}', '{body}', '{title}', '{facebook_id}' , '{author}' , '{channel}')".format(
                id=item['post_id'], 
                parse_date=parse_date_unix, 
                body=item['text_segmented'], 
                title=item['title_segmented'], 
                facebook_id=item['facebook_id'], 
                author=item['author'], 
                channel=item['channel'],
                )
                
        cursor.execute(SQLStatement.format())
        #Print( SQLStatement )
        #cursor.close()
        return item

if __name__ == "__main__":
    
    rtindex = RealTimeIndexInsert()

    item = {}
    item['title']       = 'ทดสอบภาษาไทย'
    item['text']        = 'ทดสอบภาษาไทย2'
    item['title_segmented'] = 'ทดสอบ ภาษา ไทย'
    item['text_segmented']  = 'ทดสอบ ภาษา ไทย 2'
    item['post_id']     = '1234'
    item['datetime']    = '2015-03-12 14:58:00'
    item['facebook_id'] = 'F1234567890'
    item['author']      = 'ThothMediaUser'
    item['channel']     = 'Facebook'
    
    rtindex.process_item( item )
