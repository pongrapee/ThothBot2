# -*- coding: utf-8 -*-
# coding='utf-8'

import re

def is_array(var):
    return isinstance(var, (list, tuple))

def is_int(var):
    return isinstance(var, (int, long, float))

def PrintNoNewLine( *arglist ):
    for arg in list (arglist):
        if not is_array( arg ):
            if is_int( arg ):
                print str( arg ),
            else:
                print arg.decode( "utf-8", "ignore" ).encode( "tis-620", "ignore" ),
        else:
            for item in list(arg): 
                PrintNoNewLine( item )

def Print( *arglist ):
    for arg in list (arglist):
        if not is_array( arg ):
            if is_int( arg ):
                print str( arg ),
            else:
                print arg.decode( "utf-8", "ignore" ).encode( "tis-620", "ignore" ),
        else:
            for item in list(arg): 
                PrintNoNewLine( item )
    print 

def multisplit(s, seps):
    res = re.split(seps,s)
    return res


if __name__ == "__main__":
    Print ("abc")
    Print ("ฟหกด")
    Print ("ฟหกด", "=", "asdf")
    Print (u"ฟหกด", r"ฟหกด", "ฟหกด", "ฟหกด", "ฟหกด")
    print multisplit( "Beautiful, is; better*than\nugly", "; |, |\*|\n")