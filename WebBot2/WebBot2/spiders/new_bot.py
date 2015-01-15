# -*- coding: utf-8 -*-
# coding='utf-8'

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from WebBot2.items import Webbot2Item
import re
from siteconfig import *
from extractfunction import *
from helpers.helperlib import *
from datetime import *
import sys

DEBUG=False
SYSTEMDEBUG=False

TEST_CONFIGFILE = r'C:\\Git\\backend\\SpiderGeneric\\Generic\\Config\\thaimtb.cfg'

class NewBotSpider(CrawlSpider):
    name = 'new_bot'
    
    rules = (
        Rule(SgmlLinkExtractor(), follow=False),
        )

    def __init__(
        self, 
        ConfigFile='',
        Debug=-1,
        SystemDebug=-1,
        ExtractMode=-1,
        Botname='',
        *args, **kw 
        ):

        global DEBUG
        global SYSTEMDEBUG

        self.num_pages = 0
        self.num_posts = 0
        self.start_time = datetime.utcnow() + timedelta(hours=7)
        self.page_already_visited = []

        if Debug !=-1:
            DEBUG = int(Debug)
        if SystemDebug != -1:
            SYSTEMDEBUG = int(SystemDebug)
        if DEBUG: Print( "** DEBUG is Enabled **" )
        if SYSTEMDEBUG: Print( "** SYSTEMDEBUG is Enabled **" )
        
        if ConfigFile != "":
            self.ConfigFile = ConfigFile
        else:
            self.ConfigFile = TEST_CONFIGFILE
        ReadConfig(self.ConfigFile)
        self.currentconfig = SiteConfig['FromFile']
        
        #for testing mock config
        #self.currentconfig = SiteConfig['jeban_test']

        self.allowed_domains = self.currentconfig['allowed_domains']
        self.start_urls = self.currentconfig['start_urls']

        self.rules = (
            Rule(
                SgmlLinkExtractor(
                    allow=self.currentconfig['allow'],
                    deny=self.currentconfig['deny'],
                    unique=True, ), 
                callback='parse_page', 
                follow=True, ),
        )
  
        if DEBUG:
            Print( "=======" )
            Print( "configname", self.currentconfig['configname'] )
            Print( "allowed_domains", self.allowed_domains )
            Print( "start_urls", self.start_urls )
            Print( "allow", self.currentconfig['allow'] )
            Print( "deny", self.currentconfig['deny'] )
        if SYSTEMDEBUG:
            for ConnfigurationName in self.currentconfig:
                print ConnfigurationName, self.currentconfig[ConnfigurationName]

        CrawlSpider.__init__( self, *args, **kw )
        self.Extractor = Extractor( self.currentconfig )
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse_page(self, response):
        
        self.num_pages += 1
        if self.num_pages % 10 == 0:
            sys.stdout.write('.')

        if DEBUG: print response.url
        
        url_parse_mainpage  = re.compile( self.currentconfig['url_parse_mainpage'], re.I|re.U )
        url_parse_subpage   = re.compile( self.currentconfig['url_parse_subpage'], re.I|re.U )

        if self.currentconfig['clean'] != None:
            clean_url = response.url
            for expression in self.currentconfig['clean']:
                clean = re.compile( expression, re.I|re.U )
                clean_url = clean.sub("", clean_url)
        else:
            clean_url = response.url

        if DEBUG: 
            Print( "==================================================" )
            Print( clean_url )

        m = url_parse_subpage.search( clean_url )
        if m is None:
            m = url_parse_mainpage.search( clean_url )
        
        if m is not None:
            try:
                site      = m.group('SITE')
            except IndexError:
                site      = 0
            try:
                forum     = m.group('FORUM')
            except IndexError:
                forum     = 0
            
            thread_id = m.group('THREAD_ID')

            #if len(m.groups()) >=4:
            try: 
                page  = self.convert_page_id(int(m.group('PAGE')))
            except IndexError: 
                page  = self.convert_page_id(0)
        else:
            #not a page we want
            return

        sig=str(forum)+"_"+str(thread_id)+"_"+str(page)

        if sig in self.page_already_visited:
            #already visit this round, skip
            if DEBUG:
                Print( "OLD :",site, forum, thread_id, page , "[", self.num_pages, self.num_posts, "]")
            return
        else:
            if DEBUG or 1:
                Print( "NEW :",site, forum, thread_id, page , "[", self.num_pages, self.num_posts, "]")
            self.page_already_visited.append( sig )



        #===== Parse Routine =====
        parsedate = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
        parsedate_dateonly = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d")
        
        items = []
        self.Extractor.ParseResponse( 
            response=response, 
            items=items, 
            currentconfig=self.currentconfig,
            site=site,
            forum=forum,
            thread_id=thread_id,
            page=page )

        for item in items:
            if SYSTEMDEBUG: print(item)
        self.num_posts += len(items)
        return items

    def convert_page_id (self, raw_page_id):
        if self.currentconfig['convert_post_to_page_id'] is not None and self.currentconfig['convert_post_to_page_id'] != '' and self.currentconfig['convert_post_to_page_id'] != 'None':
            return self.currentconfig['convert_post_to_page_id'](raw_page_id)
        else:
            return raw_page_id

    def spider_closed(self, spider):
        self.end_time = datetime.utcnow() + timedelta(hours=7)
        print "Start Time      :", self.start_time
        print "End Time        :", self.end_time
        print "Elasped Time    :", self.end_time - self.start_time
        print "Pages Processed :", self.num_pages
        print "Posts Processed :", self.num_posts


