# -*- coding: utf-8 -*-
# coding='utf-8'
import sys
sys.path.append('C:\Users\Pongrapee\Desktop\TEMP\spider2\WebBot2')

from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector


from WebBot2.items import Webbot2Item
from helpers.helperlib import *
from helpers.DateHelper.DateHelper import *
from SpamSell import *
from cleantext import *
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from datetime import *
import md5
import operator

DEBUG = False
systemdebug = False

def Extract( anchor, xpathparam, token=None, nfrom=0, nto=0 ):
    temp = anchor.xpath(xpathparam).extract()
    temptext = ''
    for text in temp:
        text = text.replace("'","").replace('"',"").replace("`","")
        temptext=temptext + " " + text.encode("utf-8",'ignore').strip(' \t\n\r')
    if systemdebug :
        print "temptext = " + temptext
    if token != None and token != "" and token != "None":
        if token == '" "' :
            token = " ";
        splitedtext = multisplit(temptext,token)
        splitedtext = filter(None, splitedtext)
        if nfrom < 0:
            nfrom = len(splitedtext) + nfrom + 1
        if nto < 0:
            nto = len(splitedtext) + nto + 1
        finaltext = ''
        i = 1
        for ntoken in splitedtext :
            if i >= nfrom and i <= nto :
                finaltext = finaltext + ntoken + " "
            i+=1
    else:
        finaltext = temptext
    finaltext = finaltext.strip(' \t\n\r')
    if systemdebug :
        print "finaltext = " + finaltext
    return finaltext

def Extract2Options( anchor, xpathparam="./h3", token=None, nfrom=0, nto=0, xpathparam2="./h3", token2=None, nfrom2=0, nto2=0 ):
    value1          = Extract( anchor, xpathparam, token, nfrom, nto )
    value2          = Extract( anchor, xpathparam2, token2, nfrom2, nto2 )
    finalvalue = value1
    if value1 == "" :
        finalvalue = value2
    return finalvalue

class Extractor:
    
    def __init__(self, currentconfig):
        
        self.currentconfig = currentconfig
        self.ids_seen = {}
        self.text_seen = {}

        try:
            self.ids_seen_file = open(self.currentconfig['configname']+'_pagelist.txt', "r")
        except IOError:
            self.ids_seen_file = []

        for line in self.ids_seen_file:
            tokens = line.split(":")
            self.ids_seen[tokens[0].strip()]=[int(tokens[1].strip()),0]
        
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        


    def spider_closed(self, spider):
        
        sorted_ids_seen = sorted(self.ids_seen.items(), key=lambda x: x[1][1], reverse=True)

        print "writing",self.currentconfig['configname']+'_pagelist.txt'
        output_file = open(self.currentconfig['configname']+'_pagelist.txt', "w")
        #for pagesigature, currentmaxpostid in self.ids_seen.items():
            #output_file.write(pagesigature + ":" + str(currentmaxpostid[0])+ ":" + str(currentmaxpostid[1]) + "\n")
        for row in sorted_ids_seen:
            output_file.write(row[0] + ":" + str(row[1][0])+ ":" + str(row[1][1]) + "\n")

        now = datetime.utcnow() + timedelta(hours=7)
        now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
        print "writing",self.currentconfig['configname']+'_pagelist'+now_str+'.txt'
        output_file = open(self.currentconfig['configname']+'_pagelist_'+now_str+'.txt', "w")
        #for pagesigature, currentmaxpostid in self.ids_seen.items():
            #output_file.write(pagesigature + ":" + str(currentmaxpostid[0])+ ":" + str(currentmaxpostid[1]) + "\n")
        for row in sorted_ids_seen:
            output_file.write(row[0] + ":" + str(row[1][0])+ ":" + str(row[1][1]) + "\n")

    def IsRecent( self, postdateraw ):
        postdate = datetime.strptime(postdateraw, "%Y-%m-%d %H:%M:%S")
        cutoffdate = datetime.utcnow() + timedelta(hours=7) - timedelta(days=90)
        if postdate >= cutoffdate:
            if DEBUG: print "Recent :", postdate
            return True
        else:
            if DEBUG: print  "Old   :", postdate
            return False

    def IsSPAM( self, item ):
        if item['digest'] in self.text_seen:
            if item['postsignature'] not in self.text_seen[item['digest']]:
                if DEBUG: 
                    print "SPAM :",item['postsignature'],item['digest']
                    print item['url']
                    Print(item['text'])
                    print self.text_seen[item['digest']]
                    print "=========="  
                self.text_seen[item['digest']].append(item['postsignature'])
            return True
        else:
            if DEBUG: print "ADD  :",item['postsignature'],item['digest']
            self.text_seen[item['digest']]=[item['postsignature']]
            return False

    def IsNew( self, page_id, item_id ):
        ISNEWDEBUG = False
            
        if page_id in self.ids_seen:
            if self.ids_seen[page_id][0] < int(item_id):
                self.ids_seen[page_id] = [int(item_id),self.ids_seen[page_id][1]+int(item_id)-self.ids_seen[page_id][0]]
                
                if DEBUG or ISNEWDEBUG: print "new        :", page_id, item_id
                return True
            else:
                if DEBUG or ISNEWDEBUG: print "duplicated :", page_id, item_id
                return False
        else:
            self.ids_seen[page_id] = [int(item_id),0]
            return True

    def ParseResponse( self, response, items, currentconfig, site, forum, thread_id, page ):

        if DEBUG: print "============start post================="

        post_is_sell = False
        post_is_spam = False

        parsedate = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
        #hxs = HtmlXPathSelector( response )
        #posts = hxs.select( currentconfig['PostAnchor'] )
        posts = Selector( response=response ).xpath( currentconfig['PostAnchor'] )

        for post in posts:
            item = Webbot2Item()
            item['url'] = response.url
            item['title'] = clean_text( Extract( post, currentconfig['PostTitle'] ))
            item['text'] = clean_text( Extract( post, currentconfig['PostText'] ))
            item['author'] = Extract2Options ( 
                    post, 
                    currentconfig['PostAuthor'], 
                    currentconfig['PostAuthorDelim'], 
                    currentconfig['PostAuthorStart'], 
                    currentconfig['PostAuthorEnd'],
                    currentconfig['PostAuthor2'], 
                    currentconfig['PostAuthor2Delim'], 
                    currentconfig['PostAuthor2Start'], 
                    currentconfig['PostAuthor2End'] )     
            DateTime = Extract2Options( post, xpathparam=currentconfig['PostDateTime'], xpathparam2=currentconfig['PostDateTime2'])
            item['rawdatetime'] = DateTime
            item['datetime'] = DecodeDateTime( input=DateTime, preferreddateformat=currentconfig['PreferredDateFormat'] )
            item['type'] = "post"
            item['page_id'] = str(page)
            item['post_id'] = str(0)
            item['parse_date'] = str(parsedate)  
            item['pagesignature'] = str(site) + '_' + str(forum) + '_' + str(thread_id)
            item['postsignature'] = str(site) + '_' + str(forum) + '_' + str(thread_id) + '_' + item['post_id']
            digest = md5.new(item['text'][0:500]).hexdigest()
            item['digest'] = digest

            if self.IsSPAM( item ) is True:
                possible_spam=True 
            else:
                possible_spam=False

            item['sellscore'] = sellvaluescore( item['text'] )
            item['spamscore'] = spamvaluescore( item['text'] )
            item['sale'] = str(1) if item['sellscore'] <=-45 else str(0)
            item['spam'] = str(1) if item['spamscore'] <=-45 or possible_spam else str(0)
            
            post_is_sell = item['sale']
            post_is_spam = item['spam']

            if DEBUG:
                Print( 'URL          :', item['url'] )
                Print( 'PostSig      :', item['postsignature'] )
                Print( 'PostSig      :', item['postsignature'] )
                Print( 'Title        :', item['title'] )    
                Print( 'Text         :', item['text'] )
                Print( 'Author       :', item['author'] )
                Print( 'Raw Datetime :', item['rawdatetime'] )
                Print( 'PostDate     :', item['datetime'] )
                Print( 'ParseDate    :', item['parse_date'] )
                Print( 'Type         :', item['type'] )
                Print( 'Digest       :', item['digest'] )
                Print( 'Sale         :', item['sale'] )
                Print( 'Spam         :', item['spam'] )
                Print( 'SellScore    :', item['sellscore'] )
                Print( 'SpamScore    :', item['spamscore'] )

            #check duplicate
            if self.IsNew( thread_id, item['post_id'] ):
                if self.IsRecent( item['datetime'] ):
                    items.append( item )
            
            if DEBUG: print "---------------------------------"
            break

        if DEBUG: print "============end post================="
        if DEBUG: print "============start comment================="

        parsedate = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
        #hxs = HtmlXPathSelector( response )
        #comments = hxs.select( currentconfig['CommentAnchor'] )
        comments = Selector( response=response ).xpath( currentconfig['CommentAnchor'] )
        

        if currentconfig['convert_page_id_to_post'] is not None and currentconfig['convert_page_id_to_post'] != '' and currentconfig['convert_page_id_to_post'] != 'None':
            starting_comment_id = currentconfig['convert_page_id_to_post'](page)
        else:
            starting_comment_id = 0

        comment_id = 1
        first_comment = True
        for comment in comments:
            if first_comment and currentconfig['FirstCommentAndPostIsTheSame']:
                first_coment = False
                continue
            if first_comment:
                first_comment = False
            item = Webbot2Item()
            item['url'] = response.url
            item['title'] = ''
            item['text'] = clean_text( Extract( comment, currentconfig['CommentText'] ) )
            item['author'] = Extract2Options ( 
                    comment, 
                    currentconfig['CommentAuthor'], 
                    currentconfig['CommentAuthorDelim'], 
                    currentconfig['CommentAuthorStart'], 
                    currentconfig['CommentAuthorEnd'],
                    currentconfig['CommentAuthor2'], 
                    currentconfig['CommentAuthor2Delim'], 
                    currentconfig['CommentAuthor2Start'], 
                    currentconfig['CommentAuthor2End'] )     
            DateTime = Extract2Options( comment, xpathparam=currentconfig['CommentDateTime'], xpathparam2=currentconfig['CommentDateTime2'])
            item['rawdatetime'] = DateTime
            item['datetime'] = DecodeDateTime( input=DateTime, preferreddateformat=currentconfig['PreferredDateFormat'] )
            item['type'] = "comment"
            item['page_id'] = str(page)
            if currentconfig['CommentID'] != "":
                item['post_id'] = Extract( comment, currentconfig['CommentID'] )
            else:
                item['post_id'] = str(starting_comment_id+comment_id) ##TODO
            item['parse_date'] = str(parsedate)  
            item['pagesignature'] = str(site) + '_' + str(forum) + '_' + str(thread_id)
            item['postsignature'] = str(site) + '_' + str(forum) + '_' + str(thread_id) + '_' + item['post_id']
            digest = md5.new(item['text'][0:500]).hexdigest()
            item['digest'] = digest 
            item['sellscore'] = sellvaluescore( item['text'] )
            item['spamscore'] = spamvaluescore( item['text'] )

            if self.IsSPAM( item ) is True:
                possible_spam=True 
            else:
                possible_spam=False

            item['sale'] = str(1) if item['sellscore'] <=-30 or post_is_sell else str(0)
            item['spam'] = str(1) if item['spamscore'] <=-30 or post_is_spam or possible_spam else str(0)

            if DEBUG:
                Print( 'PageSig      :', item['pagesignature'] )
                Print( 'PostSig      :', item['postsignature'] )   
                Print( 'Text         :', item['text'] )
                Print( 'Author       :', item['author'] )
                Print( 'Page ID      :', item['page_id'] )
                Print( 'Post ID      :', item['post_id'] )
                Print( 'Raw Datetime :', item['rawdatetime'] )
                Print( 'PostDate     :', item['datetime'] )
                Print( 'ParseDate    :', item['parse_date'] )
                Print( 'Type         :', item['type'] )
                Print( 'Digest       :', item['digest'] )
                Print( 'Sale         :', item['sale'] )
                Print( 'Spam         :', item['spam'] )
                Print( 'SellScore    :', item['sellscore'] )
                Print( 'SpamScore    :', item['spamscore'] )

            if self.IsNew( thread_id, item['post_id'] ):
                if self.IsRecent( item['datetime'] ):
                    items.append( item )
            comment_id+=1
            if DEBUG: print "---------------------------------"
        
        if DEBUG: print "============end comment================="

if __name__ == "__main__":
    
    import urllib2
    from scrapy.http import HtmlResponse
    from siteconfig import *
    
    #url = "http://www.thaimtb.com/forum/viewtopic.php?f=53&t=1132015"
    url = "http://www.jeban.com/viewtopic.php?t=195397"
    
    contents = urllib2.urlopen(url).read()
    response = HtmlResponse(url=url, body=contents)
    currentconfig = SiteConfig['jeban_test']
    extractor = Extractor( currentconfig )
    items = []
    extractor.ParseResponse( 
            response=response, 
            items=items, 
            currentconfig=currentconfig,
            site='www.thaimtb.com',
            forum='53',
            thread_id='1132015',
            page='0' )
    for item in items:
        for key in item:
            PrintNoNewLine( key )
            PrintNoNewLine( ":" )
            Print( item[key] )
        print "=================="
    print "\n"

