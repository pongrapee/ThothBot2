# -*- coding: utf-8 -*-
# coding='utf-8'

from QueueWorkerTemplate import *

import time

DEBUG = False

class MyDataProcessing(QueueWorkerTemplate):
    workertype = 'MyDataProcessing'
    def __init__(self, input_queue=None, output_queue=None, name='MyDataProcessing', id=0, rules_file=None):
        super(MyDataProcessing,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)

    def process_item( self, item ):
        #item['subject'] = item['region']+"_"+item['name']
        pass
    
class MyDataValidation(QueueWorkerTemplate):
    workertype = 'MyDataValidation'
    def __init__(self, input_queue=None, output_queue=None, name='MyDataValidation', id=0, rules_file=None):
        super(MyDataValidation,self).__init__(input_queue=input_queue, output_queue=output_queue, name=name, id=id)
        self.rules_file = rules_file
        self.validation_rules = None
    
    def load_rules( self ):
        #TODO
        #load rules from self.rules_file
        self.validation_rules = [
            #column_name, checking_function (must return T/F), other params
            ["datetime",        is_datetime_str,            None],
            ["datetime",        is_not_null_or_blank,       None],
            ["subject",         is_within_choices,          [   "SCB",
                                                                "KBANK",
                                                                "Krung Sri",
                                                                "KTB",
                                                                "Thanachart"]],
            #["post_id",         is_unique,                  "post_id"],
        ]


    def process_item( self, item ):
        if self.validation_rules is None:
            self.load_rules()
        for [column_name, validation_function, additional] in self.validation_rules:
            try:
                if validation_function(item[column_name],additional):
                    if DEBUG: print "OK    :",column_name, validation_function.__doc__, item[column_name]
                else:
                    print "Error :",column_name, validation_function.__doc__, item[column_name]

            except KeyError as e:

                logging.error( str(e) )

        self.msgcounter.value+=1
        return item


def is_within_choices(var, choices):
    """is_within_choices"""
    if var in choices:
        return True
    return False

def is_not_null(var, additional):
    """is_not_null"""
    if var is not None:
        return True
    return False

def is_not_blank(var, additional):
    """is_not_blank"""
    if var != "":
        return True
    return False

def is_not_null_or_blank(var, additional):
    """is_not_null_or_blank"""
    if is_not_null(var,additional) and is_not_blank(var,additional):
        return True
    return False

collection_list = {}
def is_unique(var, collection_list_name):
    """is_unique"""
    try:
        collection_list[collection_list_name]
    except KeyError:
        collection_list[collection_list_name] = []

    if var not in collection_list[collection_list_name]:
        collection_list[collection_list_name].append(var)
        return True
    return False 

def is_date_str(var, additional):
    """is_date"""
    try:
        datetime.strptime(str(var), '%Y-%m-%d')
    except ValueError:
        return False
        #raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    return True

def is_datetime_str(var, additional):
    """is_datetime"""
    try:
        datetime.strptime(str(var), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False
        #raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    return True

if __name__ == "__main__":
    myDataValidation = MyDataValidation()

    item = Webbot2Item()
    item['datetime'] = '2015-01-01 10:00:00'
    item['subject'] = "SCB"
    item['post_id']  = '1234'

    item2 = Webbot2Item()
    item2['datetime'] = '2015-01-01 11:00:00'
    item2['subject'] = "KBANK"
    item2['post_id']  = '1234'

    item3 = Webbot2Item()
    item3['datetime'] = '2015-01-01 01:00:00'
    item3['subject'] = "XXX"
    item3['post_id']  = '5678'


    myDataValidation.process_item( item )
    myDataValidation.process_item( item2 )
    myDataValidation.process_item( item3 )

