# -*- coding: utf-8 -*-
# coding='utf-8'
import re

def replace_all(text, replace_dict):
    for k, v in replace_dict:
        text = text.replace(k, v)
    return text


def clean_text(text):
    text = " ".join(text.splitlines())
    text = text.strip()

    #remove url from body
    text = re.sub(r'http:\/\/.*?\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'http:\/\/.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'https:\/\/.*?\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'https:\/\/.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'.*\.php.*\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'.*\.php.*$', '', text, flags=re.MULTILINE)

    replace_dict = [
        ("|",' '), 
        ("\r",' '),
        ("\n",' '),
        ("\t",' '), 
        ('"',' '), 
        ("'",' '), 
        ('(',' '), 
        (')',' '),
        ('~',' '), 
        ('!',' '),
        ('&nbsp;',' '), 
        ('&amp;',' '), 
        ('&gt;',' '),
        ('&lt;',' '), 
        ('&','& '), 
        ('gt;',' '),
        ('?','? '), 
        ('^',' '), 
        ('lt;',' '), 
        (u'ค่ะ','ค่ะ '),
        (u'ครับ','ครับ '), 
        (u'ก็','ก็ '), 
        (u'หรือ','หรือ '), 
        (u'และ','และ '), 
        ("`"," "),
        ('...',' '),
    ]

    #replace all with mapping
    text = replace_all(text, replace_dict)
    
    #replace spaces with 1 space
    text = re.sub(r'([\s])\1{1,}', r'\1', text)

    #replace non-thai non-english character with blank
    pattern = ur'[^\u0E00-\u0E7F\u0020-\u007F ]'
    text = re.sub(pattern, "", text, flags=re.U)

    #replace 'ๆ'
    pattern = ur'[\u0E46]' 
    text = re.sub(pattern, " ", text, flags=re.U)

    #replace duplicated thai character e.g. มาาาาาาาาาาาาาาาาาาาาาาากกกกกกกกก -> มาก
    pattern = ur'([\u0E00-\u0E7F\u0020-\u002F\u0040-\u007F])\1{2,}'
    text = re.sub(pattern, ur'\1\1', text, flags=re.U)
    text = re.sub(ur'([\u0E00-\u0E7F\u0020-\u002F\u0040-\u007F])([\d])', ur'\1 \2', text, flags=re.U)
    text = re.sub(ur'([\d])([\u0E00-\u0E7F\u0020-\u002F\u0040-\u007F])', ur'\1 \2', text, flags=re.U)
    text = re.sub(ur'([!@#$%^&*()_+-=\\/|{}\[\]<>,\.\?])([\u0E00-\u0E7F\u0020-\u002F\u0040-\u007F]*)', ur'\2', text, flags=re.U)
    text = re.sub(ur'([\u0E00-\u0E7F\u0020-\u002F\u0040-\u007F]*)([!@#$%^&*()_+-=\\/|{}\[\]<>,\.\?])', ur'\1', text, flags=re.U)

    return text