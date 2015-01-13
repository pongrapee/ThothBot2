# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Webbot2Item(Item):
    # define the fields for your item here like:
    # name = Field()
    url             = Field()
    author          = Field()
    title           = Field()
    text            = Field()
    text_segmented  = Field()
    date            = Field()
    time            = Field()
    datetime        = Field()
    rawdatetime     = Field()
    type            = Field()
    page_id         = Field()
    parse_date      = Field()
    post_id         = Field()
    pagesignature   = Field()
    postsignature   = Field()
    digest          = Field()
    sale            = Field()
    spam            = Field()
    sellscore       = Field()
    spamscore       = Field()
    keywordlist     = Field()
    total_len       = Field()
    all_emo_word_count      = Field()
    