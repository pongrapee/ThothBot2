# -*- coding: utf-8 -*-
# coding='utf-8'

from helpers.helperlib import *
import logging
from items import Webbot2Item

DEBUG = False

WORD  = 0
TYPE  = 1
VALUE = 2



class SentimentFeatures(object):
    
    def __init__(self):
        self.emo_word_list = []
        self.amp_word_list = {}
        emo_word_list_file = open(r'c:\temp\emo_word_list.csv', "r")
        first_line = True
        for line in emo_word_list_file:
            tokens = line.split(",")
            if first_line:
                first_line = False
                continue
            if len(tokens)>=3:
                self.emo_word_list.append( [tokens[WORD],tokens[TYPE],float(tokens[VALUE])] )
                if tokens[TYPE] == 'amp':
                    self.amp_word_list[tokens[WORD]] = float(tokens[VALUE])
    def process_item(self,item):

        words = item['text_segmented'].split(' ')
        #words = '''
        #ลอง ที่ไหน ยัง ดี ไง ต้อง ชอบ เอา ดี รถ ไป เอง มี ราย ละเอียด มั้
        #- - ปั่น เมพ วัน ละ นิด จิต แจ่มใส ไม่ ชอบ -
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

        pos_amp_val=0
        neg_amp_val=0

        pos_amp_val_per_word = 0
        neg_amp_val_per_word = 0

        i = 0
        j = total_len
        avg_pos_dist = 0
        last_pos_emo_pos = 0
        avg_neg_dist = 0
        last_neg_emo_pos = 0
        p_word = ''
        p_p_word = ''
        p_p_p_word = ''
        item['pos_words_list'] = ''
        item['neg_words_list'] = '' 
        for word in words:
            j-=1

            for row in self.emo_word_list:
                #positive
                if  ( row[TYPE] == 'emo' and row[VALUE] > 0 and (p_word != 'ไม่' and p_p_word != 'ไม่' and p_p_p_word != 'ไม่')) or (row[TYPE] == 'emo' and row[VALUE] < 0 and (p_word == 'ไม่' or p_p_word == 'ไม่' or p_p_p_word == 'ไม่')):
                        
                    if word == row[WORD]:
                        if p_word == 'ไม่':
                            fullword = 'ไม่'+word
                        elif p_p_word == 'ไม่':
                            fullword = 'ไม่'+p_word+word
                        elif p_p_p_word == 'ไม่':
                            fullword = 'ไม่'+p_p_word+p_word+word
                        else:
                            fullword = word
                        if DEBUG:
                            Print('POS: '+fullword)
                        item['pos_words_list'] = item['pos_words_list']+fullword+' '

                        amplifier = 1
                        if p_word in self.amp_word_list:
                            amplifier *= self.amp_word_list[p_word]
                        if p_p_word in self.amp_word_list:
                            amplifier *= self.amp_word_list[p_p_word]
                        if p_p_p_word in self.amp_word_list:
                            amplifier *= self.amp_word_list[p_p_p_word]
                        pos_amp_val += abs(row[VALUE])*amplifier

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
                if  ( row[TYPE] == 'emo' and row[VALUE] < 0 and (p_word != 'ไม่' and p_p_word != 'ไม่' and p_p_p_word != 'ไม่')) or (row[TYPE] == 'emo' and row[VALUE] > 0 and (p_word == 'ไม่' or p_p_word == 'ไม่' or p_p_p_word == 'ไม่')):
                    if word == row[WORD]:
                        if p_word == 'ไม่':
                            fullword = 'ไม่'+word
                        elif p_p_word == 'ไม่':
                            fullword = 'ไม่'+p_word+word
                        elif p_p_p_word == 'ไม่':
                            fullword = 'ไม่'+p_p_word+p_word+word
                        else:
                            fullword = word
                        if DEBUG:
                            Print('NEG: '+fullword)
                        item['neg_words_list'] = item['neg_words_list']+fullword+' '

                        amplifier = 1
                        if p_word in self.amp_word_list:
                            amplifier *= self.amp_word_list[p_word]
                        if p_p_word in self.amp_word_list:
                            amplifier *= self.amp_word_list[p_p_word]
                        if p_p_p_word in self.amp_word_list:
                            amplifier *= self.amp_word_list[p_p_p_word]
                        neg_amp_val += -1*abs(row[VALUE])*amplifier

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
            p_p_p_word = p_p_word
            p_p_word = p_word
            p_word = word    

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

        item['total_len'] = total_len
        item['all_emo_word_count'] = all_emo_word_count 
        # item['all_emo_word_count_f_10'] = all_emo_word_count_f_10 
        # item['all_emo_word_count_f_20'] = all_emo_word_count_f_20 
        # item['all_emo_word_count_f_30'] = all_emo_word_count_f_30 
        # item['all_emo_word_count_f_60'] = all_emo_word_count_f_60 
        # item['all_emo_word_count_f_100'] = all_emo_word_count_f_100 
        # item['all_emo_word_count_f_150'] = all_emo_word_count_f_150 
        # item['all_emo_word_count_l_10'] = all_emo_word_count_l_10 
        # item['all_emo_word_count_l_20'] = all_emo_word_count_l_20 
        # item['all_emo_word_count_l_30'] = all_emo_word_count_l_30 
        # item['all_emo_word_count_l_60'] = all_emo_word_count_l_60 
        # item['all_emo_word_count_l_100'] = all_emo_word_count_l_100 
        # item['all_emo_word_count_l_150'] = all_emo_word_count_l_150 

        item['all_emo_word_count_multi'] = [
            all_emo_word_count_f_10,
            all_emo_word_count_f_20,
            all_emo_word_count_f_30,
            all_emo_word_count_f_60,
            all_emo_word_count_f_100,
            all_emo_word_count_f_150,
            all_emo_word_count_l_10,
            all_emo_word_count_l_20,
            all_emo_word_count_l_30,
            all_emo_word_count_l_60,
            all_emo_word_count_l_100,
            all_emo_word_count_l_150 
            ]


        item['pos_emo_word_count'] = pos_emo_word_count 
        # item['pos_emo_word_count_f_10'] = pos_emo_word_count_f_10 
        # item['pos_emo_word_count_f_20'] = pos_emo_word_count_f_20 
        # item['pos_emo_word_count_f_30'] = pos_emo_word_count_f_30 
        # item['pos_emo_word_count_f_60'] = pos_emo_word_count_f_60 
        # item['pos_emo_word_count_f_100'] = pos_emo_word_count_f_100 
        # item['pos_emo_word_count_f_150'] = pos_emo_word_count_f_150 
        # item['pos_emo_word_count_l_10'] = pos_emo_word_count_l_10 
        # item['pos_emo_word_count_l_20'] = pos_emo_word_count_l_20 
        # item['pos_emo_word_count_l_30'] = pos_emo_word_count_l_30 
        # item['pos_emo_word_count_l_60'] = pos_emo_word_count_l_60 
        # item['pos_emo_word_count_l_100'] = pos_emo_word_count_l_100 
        # item['pos_emo_word_count_l_150'] = pos_emo_word_count_l_150 
        item['pos_emo_word_count_multi'] = [
            pos_emo_word_count_f_10,
            pos_emo_word_count_f_20,
            pos_emo_word_count_f_30,
            pos_emo_word_count_f_60,
            pos_emo_word_count_f_100,
            pos_emo_word_count_f_150,
            pos_emo_word_count_l_10,
            pos_emo_word_count_l_20,
            pos_emo_word_count_l_30,
            pos_emo_word_count_l_60,
            pos_emo_word_count_l_100,
            pos_emo_word_count_l_150 
            ]

        item['neg_emo_word_count'] = neg_emo_word_count 
        # item['neg_emo_word_count_f_10'] = neg_emo_word_count_f_10 
        # item['neg_emo_word_count_f_20'] = neg_emo_word_count_f_20 
        # item['neg_emo_word_count_f_30'] = neg_emo_word_count_f_30 
        # item['neg_emo_word_count_f_60'] = neg_emo_word_count_f_60 
        # item['neg_emo_word_count_f_100'] = neg_emo_word_count_f_100 
        # item['neg_emo_word_count_f_150'] = neg_emo_word_count_f_150 
        # item['neg_emo_word_count_l_10'] = neg_emo_word_count_l_10 
        # item['neg_emo_word_count_l_20'] = neg_emo_word_count_l_20 
        # item['neg_emo_word_count_l_30'] = neg_emo_word_count_l_30 
        # item['neg_emo_word_count_l_60'] = neg_emo_word_count_l_60 
        # item['neg_emo_word_count_l_100'] = neg_emo_word_count_l_100 
        # item['neg_emo_word_count_l_150'] = neg_emo_word_count_l_150 
        item['neg_emo_word_count_multi'] = [
            neg_emo_word_count_f_10,
            neg_emo_word_count_f_20,
            neg_emo_word_count_f_30,
            neg_emo_word_count_f_60,
            neg_emo_word_count_f_100,
            neg_emo_word_count_f_150,
            neg_emo_word_count_l_10,
            neg_emo_word_count_l_20,
            neg_emo_word_count_l_30,
            neg_emo_word_count_l_60,
            neg_emo_word_count_l_100,
            neg_emo_word_count_l_150 
            ]

        item['avg_pos_dist'] = avg_pos_dist 
        item['avg_neg_dist'] = avg_neg_dist 
        item['ratio_all_emo_vs_total'] = ratio_all_emo_vs_total 
        item['ratio_pos_emo_vs_total'] = ratio_pos_emo_vs_total 
        item['ratio_neg_emo_vs_total'] = ratio_neg_emo_vs_total 
        item['ratio_pos_emo_vs_neg_emo'] = ratio_pos_emo_vs_neg_emo 
        # item['ratio_pos_emo_vs_neg_emo_f_10'] = ratio_pos_emo_vs_neg_emo_f_10 
        # item['ratio_pos_emo_vs_neg_emo_f_20'] = ratio_pos_emo_vs_neg_emo_f_20 
        # item['ratio_pos_emo_vs_neg_emo_f_30'] = ratio_pos_emo_vs_neg_emo_f_30 
        # item['ratio_pos_emo_vs_neg_emo_f_60'] = ratio_pos_emo_vs_neg_emo_f_60 
        
        item['pos_amp_val'] = pos_amp_val
        item['neg_amp_val'] = neg_amp_val

        item['pos_amp_val_per_word'] = int(pos_amp_val / total_len * 1000)/10
        item['neg_amp_val_per_word'] = int(neg_amp_val / total_len * 1000)/10
        
        if item['pos_amp_val_per_word'] - item['neg_amp_val_per_word'] > 0.1:
            item['mood'] = 'positive'
        elif item['pos_amp_val_per_word'] - item['neg_amp_val_per_word'] < -0.1:
            item['mood'] = 'negative'
        else:
            item['mood'] = 'neutral'
        return item

if __name__ == "__main__":

    item = Webbot2Item()
    item['text_segmented'] = '''ผม อ่าน คอมเม้นท์ แล้ว รู้สึก ไม่ สบาย ใจ อยาก จะ บอก ว่า ไม่ เคย คิด ดิสเครดิส ใคร
ดี ใจ และ ขอบคุณ ด้วย ซ้ำ ที่ รัฐ และ กทม. เริ่ม ส่งเสริม เรื่อง จักรยาน อย่าง จริง จัง
แต่ ไหน ไหน ก็ ทำ แล้ว ก็ เลย อยาก ให้ ทาง ใช้ งาน ได้ จริง บกพร่อง ตรง ไหน เรา
เป็น ประชาชน หาก แจ้ง กระจาย ข่าว ได้ ก็ ช่วย กัน ถือ ว่า เป็น หน้า ที่ พลเมือง'''
    mySentimentFeatures = SentimentFeatures()
    mySentimentFeatures.process_item(item)
    Print(item)
