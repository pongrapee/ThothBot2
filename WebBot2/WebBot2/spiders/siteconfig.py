# -*- coding: utf-8 -*-
# coding='utf-8'

import ConfigParser
import codecs
from helpers.helperlib import *

systemdebug=False

config = ConfigParser.ConfigParser(allow_no_value=True)
settingname = "GenericWebSpider"

SiteConfig = {}

def LoadConfig( valuename, defaultvalue = "", settingname = settingname  ):
    try:
        variable        = ""
        variable        = config.get(settingname, valuename, 0)
    except :
        pass
    if variable == "":
        variable = defaultvalue
    if systemdebug:
        print (valuename , " = " , variable)
    return variable

def LoadConfigInt( valuename, defaultvalue = 0, settingname = settingname ):
    try:
        variable        = 0
        variable        = config.getint(settingname, valuename)
    except :
        pass
    if variable == 0:
        variable = defaultvalue
    if systemdebug:
        print valuename + " = " + str(variable)
    return variable

def ReadConfig( filename ):
    config.readfp(codecs.open(filename, "r", "utf8"))
    SiteConfig['FromFile'] = {
        'configname': LoadConfig('AllowedDomains'),
        'allowed_domains': multisplit(LoadConfig('AllowedDomains'),','),
        'start_urls': multisplit(LoadConfig('StartURL',''),','),
        'allow': multisplit(LoadConfig('Allow',''),','), 
        'deny': multisplit(LoadConfig('Deny',''),','), 
        'clean': multisplit(LoadConfig('Clean'),','),
        'url_parse_mainpage': LoadConfig('MainPage'), 
        'url_parse_subpage': LoadConfig('SubPage'), 
        'convert_post_to_page_id': eval(LoadConfig('PostToPageID')),
        'convert_page_id_to_post': eval(LoadConfig('PageToPostID')),
        'PreferredDateFormat': LoadConfig('PreferredDateformat','D-M-Y'),
        'FirstCommentAndPostIsTheSame': LoadConfigInt('FirstCommentAndPostIsTheSame',0),
        'PostAnchor': LoadConfig('PostAnchor'),
        'PostTitle': LoadConfig('PostTitle'),
        'PostText': LoadConfig('PostText'),
        'PostAuthor': LoadConfig('PostAuthor'),
        'PostAuthorDelim': LoadConfig('PostAuthorDelim',' '), 
        'PostAuthorStart': LoadConfigInt('PostAuthorStart',1),
        'PostAuthorEnd': LoadConfigInt('PostAuthorEnd',1),
        'PostAuthor2': LoadConfig('PostAuthor2','./h3'),
        'PostAuthor2Delim': LoadConfig('PostAuthor2Delim',' '), 
        'PostAuthor2Start': LoadConfigInt('PostAuthor2Start',1),
        'PostAuthor2End': LoadConfigInt('PostAuthor2End',1),
        'PostDateTime': LoadConfig('PostDateTime'),
        'PostDateTime2': LoadConfig('PostDateTime2','./h3'),
        'CommentAnchor': LoadConfig('CommentAnchor'),
        'CommentText':  LoadConfig('CommentText'),
        'CommentAuthor': LoadConfig('CommentAuthor'),
        'CommentID': LoadConfig('CommentID',''),
        'CommentAuthorDelim': LoadConfig('CommentAuthorDelim',' '),
        'CommentAuthorStart': LoadConfigInt('CommentAuthorStart',1),
        'CommentAuthorEnd': LoadConfigInt('CommentAuthorEnd',1),
        'CommentAuthor2': LoadConfig('CommentAuthor2','./h3'),
        'CommentAuthor2Delim': LoadConfig('CommentAuthor2Delim',' '),
        'CommentAuthor2Start': LoadConfigInt('CommentAuthor2Start',1),
        'CommentAuthor2End': LoadConfigInt('CommentAuthor2End',1),
        'CommentDateTime': LoadConfig('CommentDateTime'),
        'CommentDateTime2': LoadConfig('CommentDateTime2','./h3'),
    }
    #SiteConfig['FromFile'] = SiteConfig['thaimtb']

SiteConfig['thaimtb_test'] = {
    'configname': 'thaimtb.com',
    'allowed_domains': ['thaimtb.com'],
    'start_urls': ['http://www.thaimtb.com/forum'],
    'allow': ['/forum/'],
    'deny': ['memberlist','ucp','posting','previous','next','print'],
    'clean': ['\&sid\=[0-9a-f]+','\&p\=[0-9]+'],
    #http://www.thaimtb.com/forum/viewtopic.php?f=57&t=1027346
    'url_parse_mainpage': ur'http:\/\/(?P<SITE>.*?)\/forum\/viewtopic\.php\?f\=(?P<FORUM>\d*)\&t\=(?P<THREAD_ID>\d*)',
    #http://www.thaimtb.com/forum/viewtopic.php?f=14&t=596584&start=15
    'url_parse_subpage':  ur'http:\/\/(?P<SITE>.*?)\/forum\/viewtopic\.php\?f\=(?P<FORUM>\d*)\&start\=(?P<PAGE>\d*)\&t\=(?P<THREAD_ID>\d*)',
    'convert_post_to_page_id': (lambda x: int(x/15)),
    'convert_page_id_to_post': (lambda x: int(x*15)),
    'PreferredDateFormat': 'D-M-Y',
    'FirstCommentAndPostIsTheSame': False,
    'PostAnchor': '//div[@id="pagecontent"]/table[3]',
    'PostTitle': './../../div[@id="pageheader"]/h2/a/text()',
    'PostText': './tr[3]/td[2]//text()',
    'PostAuthor': './/b[@class="postauthor"]/text()',
    'PostAuthorDelim': ' ', 
    'PostAuthorStart': 1,
    'PostAuthorEnd': 1,
    'PostAuthor2': './h3',
    'PostAuthor2Delim': ' ', 
    'PostAuthor2Start': 1,
    'PostAuthor2End': 1,
    'PostDateTime': './tr[2]/td[2]/table/tr/td/div[1]/text()',
    'PostDateTime2': './h3',
    'CommentAnchor': '//div[@id="pagecontent"]/table[position()>3 and position()<=last()-2]',
    'CommentText':  './/div[@class="postbody"]//text()',
    'CommentAuthor': './/b[@class="postauthor"]/text()',
    'CommentAuthorDelim': ' ',
    'CommentAuthorStart': 1,
    'CommentAuthorEnd': 1,
    'CommentAuthor2': './h3',
    'CommentAuthor2Delim': ' ',
    'CommentAuthor2Start': 1,
    'CommentAuthor2End': 1,
    'CommentID':'',
    'CommentDateTime': './tr[1]/td[2]/table/tr/td/div[1]/text()',
    'CommentDateTime2': './h3',
}

SiteConfig['jeban_test'] = {
    'configname': 'jeban.com',
    'allowed_domains': ['jeban.com'],
    'start_urls': ['http://www.jeban.com/board_all.php'],
    'allow': ['board','viewtopic'],
    'deny': ['mypage'],
    'clean': ['\&sid\=[0-9a-f]+','\&p\=[0-9]+'],
    #http://www.thaimtb.com/forum/viewtopic.php?f=57&t=1027346
    'url_parse_mainpage': ur'http:\/\/(?P<SITE>.*?)\/viewtopic\.php\?t\=(?P<THREAD_ID>\d*)',
    'url_parse_subpage':  ur'http:\/\/(?P<SITE>.*?)\/viewtopic\.php\?t\=(?P<THREAD_ID>\d*)',
    'convert_post_to_page_id': 'None',
    'convert_page_id_to_post': 'None',
    'PreferredDateFormat': 'D-M-Y',
    'FirstCommentAndPostIsTheSame': False,
    'PostAnchor': './/div[4]/div[2]/div[1]',
    'PostTitle': './/article/div/div[1]/div[2]/h1//text()',
    'PostText': './/article/div/div[2]//text()',
    'PostAuthor': './/article/div/div[1]/div[2]/div/ul/li[1]/a/strong/text()',
    'PostAuthorDelim': "None", 
    'PostAuthorStart': 1,
    'PostAuthorEnd': 1,
    'PostAuthor2': './h3',
    'PostAuthor2Delim': "None", 
    'PostAuthor2Start': 1,
    'PostAuthor2End': 1,
    'PostDateTime': './/article/div/div[1]/div[2]/div/ul/li[2]/a//text()',
    'PostDateTime2': './h3',
    'CommentAnchor': '//*[@id="replies"]/div[position()>0]',
    'CommentTitle': './div/div[2]/nav[1]/ul[1]/li[1]/span//text()',
    'CommentText':  './div/div[2]/div//text()',
    'CommentAuthor': './div/div[2]/nav[1]/ul[1]/li[3]/a//text()',
    'CommentAuthorDelim': 'None',
    'CommentAuthorStart': 1,
    'CommentAuthorEnd': 1,
    'CommentAuthor2': './h3',
    'CommentAuthor2Delim': ' ',
    'CommentAuthor2Start': 1,
    'CommentAuthor2End': 1,
    'CommentID':'',
    'CommentDateTime': './div/div[2]/nav[1]/ul[2]/li//text()',
    'CommentDateTime2': './h3',
}

if __name__ == "__main__":
    ReadConfig(r'C:\\Git\\backend\\SpiderGeneric\\Generic\\Config\\Thaimtb.cfg')
    for ConfigName in SiteConfig:
        print ConfigName
        #for ConnfigurationName in SiteConfig[ConfigName]:
        #    print ConnfigurationName, SiteConfig[ConfigName][ConnfigurationName]
    currentconfig   = SiteConfig['FromFile']
    oldconfig       = SiteConfig['thaimtb_test']
    for configitem in currentconfig:
        if currentconfig[configitem] != oldconfig[configitem]:
            print configitem, "is not equal"
            print str(currentconfig[configitem])
            print str(oldconfig[configitem])

