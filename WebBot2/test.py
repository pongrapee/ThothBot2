import os
import re
from datetime import datetime
now = datetime.utcnow()
now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
x = {
    'asdf':[1,0],
    'qwer':[2,3],
    'ghjk':[4,5],
    'zxcv':[6,7],
    }
y = [
    ['asdf',1,0],
    ['qwer',2,3],
    ['ghjk',4,5],
    ['zxcv',6,7],
    ]
sorted_x = sorted(x.items(), key=lambda x:x[1][1])
for val in x:
    print val
for val in y:
    print val
for val in sorted_x:
    print val