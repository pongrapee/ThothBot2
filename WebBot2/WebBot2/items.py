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
    title_segmented = Field()
    text            = Field()
    text_segmented  = Field()
    date            = Field()
    time            = Field()
    datetime        = Field()
    rawdatetime     = Field()
    type            = Field()
    page_id         = Field()
    facebook_id     = Field()
    parse_date      = Field()
    post_id         = Field()
    
    total_len       = Field()
    pagesignature   = Field()
    postsignature   = Field()
    digest          = Field()
    sale            = Field()
    spam            = Field()
    sellscore       = Field()
    spamscore       = Field()
    keywordlist     = Field()
    
    total_len       = Field()

    all_emo_word_count = Field()
    # all_emo_word_count_f_10 = Field()
    # all_emo_word_count_f_20 = Field()
    # all_emo_word_count_f_30 = Field()
    # all_emo_word_count_f_60 = Field()
    # all_emo_word_count_f_100 = Field()
    # all_emo_word_count_f_150 = Field()
    # all_emo_word_count_l_10 = Field()
    # all_emo_word_count_l_20 = Field()
    # all_emo_word_count_l_30 = Field()
    # all_emo_word_count_l_60 = Field()
    # all_emo_word_count_l_100 = Field()
    # all_emo_word_count_l_150 = Field()
    all_emo_word_count_multi = Field()

    pos_emo_word_count = Field()
    # pos_emo_word_count_f_10 = Field()
    # pos_emo_word_count_f_20 = Field()
    # pos_emo_word_count_f_30 = Field()
    # pos_emo_word_count_f_60 = Field()
    # pos_emo_word_count_f_100 = Field()
    # pos_emo_word_count_f_150 = Field()
    # pos_emo_word_count_l_10 = Field()
    # pos_emo_word_count_l_20 = Field()
    # pos_emo_word_count_l_30 = Field()
    # pos_emo_word_count_l_60 = Field()
    # pos_emo_word_count_l_100 = Field()
    # pos_emo_word_count_l_150 = Field()
    pos_emo_word_count_multi = Field()

    neg_emo_word_count = Field()
    # neg_emo_word_count_f_10 = Field()
    # neg_emo_word_count_f_20 = Field()
    # neg_emo_word_count_f_30 = Field()
    # neg_emo_word_count_f_60 = Field()
    # neg_emo_word_count_f_100 = Field()
    # neg_emo_word_count_f_150 = Field()
    # neg_emo_word_count_l_10 = Field()
    # neg_emo_word_count_l_20 = Field()
    # neg_emo_word_count_l_30 = Field()
    # neg_emo_word_count_l_60 = Field()
    # neg_emo_word_count_l_100 = Field()
    # neg_emo_word_count_l_150 = Field()
    neg_emo_word_count_multi = Field()

    avg_pos_dist = Field()
    avg_neg_dist = Field()
    ratio_all_emo_vs_total = Field()
    ratio_pos_emo_vs_total = Field()
    ratio_neg_emo_vs_total = Field()
    ratio_pos_emo_vs_neg_emo = Field()
    # ratio_pos_emo_vs_neg_emo_f_10 = Field()
    # ratio_pos_emo_vs_neg_emo_f_20 = Field()
    # ratio_pos_emo_vs_neg_emo_f_30 = Field()
    # ratio_pos_emo_vs_neg_emo_f_60 = Field()

    pos_words_list = Field() 
    neg_words_list = Field()
    ign_words_list = Field()
    amp_words_list = Field()

    pos_amp_val = Field()
    neg_amp_val = Field()

    pos_amp_val_per_word = Field()
    neg_amp_val_per_word = Field()

    mood = Field()

    delivery_tag = Field()

    group = Field()
    subject = Field()

    likes = Field()
    shares = Field()

    mood_original = Field()

    tags_list = Field()

