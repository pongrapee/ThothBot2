# -*- coding: utf-8 -*-
# coding='utf-8'

# Scrapy settings for WebBot2 project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'WebBot2'

SPIDER_MODULES = ['WebBot2.spiders']
NEWSPIDER_MODULE = 'WebBot2.spiders'
CONCURRENT_REQUESTS = 60
CONCURRENT_REQUESTS_PER_DOMAIN = 30
DEPTH_LIMIT = 10
DEPTH_PRIORITY = 0

LOG_ENABLED = True
LOG_STDOUT = False
LOG_LEVEL = "ERROR" #CRITICAL, ERROR, WARNING, INFO, DEBUG. For more info see 

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'WebBot2'

ITEM_PIPELINES = {
    #'myproject.pipelines.PricePipeline': 300,
    #'myproject.pipelines.JsonWriterPipeline': 800,
    #'WebBot2.pipelines.CheckIfAlreadyDone':10,
    'WebBot2.pipelines.TextSegmentation':20,
    'WebBot2.pipelines.Keyword':30,
    'WebBot2.pipelines.ToFile':100,
}

EXTENSIONS = {
    'scrapy.contrib.closespider.CloseSpider':500,
}

#CLOSESPIDER -- 0 means no limit
CLOSESPIDER_TIMEOUT = 600 #10minutes #number of seconds
CLOSESPIDER_ERRORCOUNT = 10
CLOSESPIDER_PAGECOUNT = 5000

#LOG_FORMATTER = 'WebBot2.spiders.PoliteLogFormatter.PoliteLogFormatter'