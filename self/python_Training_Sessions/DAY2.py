import glob  # dir in python
import os.path
path = r"D:\handson"
#r"" - raw string
print(len("\n"))
# 1
#\n \r \t \v ...
print(len(r"\n"))
# 2
#escape seq - no meaning
# raw string - file path, regex
files = glob.glob(os.path.join(path, "*"))
print(files)
# ['D:\\handson\\DAY1', 'D:\\handson\\DAY1.py', 'D:\\handson\\DAY1.txt', 'D:\\ha
# ndson\\DAY2', 'D:\\handson\\DAY2.txt', 'D:\\handson\\DAY3', 'D:\\handson\\DAY3
# .txt', 'D:\\handson\\DAY4', 'D:\\handson\\DAY4.txt', 'D:\\handson\\dec_example
# .py', 'D:\\handson\\ref_links.html']
def get_files(path, ed={}): #empty dict
    files = glob.glob(os.path.join(path, "*"))
    for file in files:
        if os.path.isfile(file):
            ed[file] = os.path.getsize(file)
    for file in files:
        if not os.path.isfile(file):
            get_files(file, ed)
    return ed
# ...
# >>>
allfiles = get_files(path)
print(allfiles)
# {'D:\\handson\\DAY1.py': 3236, 'D:\\handson\\DAY1.txt': 26722, 'D:\\handson\\D
# AY2.txt': 0, 'D:\\handson\\DAY3.txt': 0, 'D:\\handson\\DAY4.txt': 0, 'D:\\hand
# son\\dec_example.py': 1082, 'D:\\handson\\ref_links.html': 3771, 'D:\\handson\
# \DAY1\\conftest.py': 561, 'D:\\handson\\DAY1\\ref_meta.py': 1675, 'D:\\handson
# \\DAY1\\test_userh.py': 2411, 'D:\\handson\\DAY1\\userh.py': 4049, 'D:\\handso
# n\\DAY2\\ref_Concurrent_otherways.py': 7585, 'D:\\handson\\DAY2\\ref_dec_class
# _based.py': 1116, 'D:\\handson\\DAY2\\ref_quick_tco.py': 8871, 'D:\\handson\\D
# AY3\\Pandas_Cheat_Sheet.pdf': 339134, 'D:\\handson\\DAY3\\data\\boston.csv': 3
# 6244, 'D:\\handson\\DAY3\\data\\example-handson.csv': 75, 'D:\\handson\\DAY3\\
# data\\example-handson.xml': 571, 'D:\\handson\\DAY3\\data\\example.csv': 76, '
# D:\\handson\\DAY3\\data\\example.html': 411, 'D:\\handson\\DAY3\\data\\example
# .json': 2674, 'D:\\handson\\DAY3\\data\\example.pptx': 30469, 'D:\\handson\\DA
# Y3\\data\\example.xml': 687, 'D:\\handson\\DAY3\\data\\example1.html': 500, 'D
# :\\handson\\DAY3\\data\\example1.xml': 571, 'D:\\handson\\DAY3\\data\\iris.csv
# ': 4600, 'D:\\handson\\DAY3\\data\\Nifty-17_Years_Data-V1.xlsx': 338269, 'D:\\
# handson\\DAY3\\data\\q.html': 76, 'D:\\handson\\DAY3\\data\\sales_transactions
# .xlsx': 5463, 'D:\\handson\\DAY3\\data\\weather.json': 4026, 'D:\\handson\\DAY
# 3\\data\\window.csv': 464, 'D:\\handson\\DAY4\\flaskWithfrontend.zip': 7361, '
# D:\\handson\\DAY4\\web.zip': 40415}
# >>>
ed = { 'ok' : 1, 'nok': 2}
print(sorted(ed))
# ['nok', 'ok']
#sort keys by string sorting order
print(sorted(allfiles)[-1])
# 'D:\\handson\\ref_links.html'
print(allfiles[sorted(allfiles)[-1]])
# 3771
def p(k):
    return ed[k]
# ...
print(sorted(ed, key=p))
# ['ok', 'nok']
def pp(k):
    return allfiles[k]
# ...
print(sorted(allfiles, key=pp)[-1])
# 'D:\\handson\\DAY3\\Pandas_Cheat_Sheet.pdf'
#sortbykey
print(p('ok'))
# 1
print(pp('D:\\handson\\DAY3\\Pandas_Cheat_Sheet.pdf'))
# 339134
print(sorted(allfiles, key=lambda k: allfiles[k])[-1])
# 'D:\\handson\\DAY3\\Pandas_Cheat_Sheet.pdf'
# >>> quit()
def add(x,y):
    return x+y
# ...
print(add(2,3)  ) # positional
# 5
print(add(y=3, x=2)  ) # keyword based arg passing
# 5
print(add(2, y=3)  ) # positional first
# 5
print(1,2,3,4)
# 1 2 3 4
print(1)
# 1
#var args - positional - *, keyword - **
def add2(*args):
    print(args)
    s = 0
    for e in args:
            s +=e
    return s
# ...
print(add2(1))
# (1,)
# 1
print(add2(1,2,3,4))
# (1, 2, 3, 4)
# 10
t = (1, 2, 3)
print(add2(t[0], t[1], t[2]))
# (1, 2, 3)
# 6
#shortcut syntax of above
print(add2(*t))
# (1, 2, 3)
# 6
##complete def
def fun(a,b=2,*args, d, e=3, **kwargs):
    print(a,b,args,d,e,kwargs)
# ...
print(fun(1,d=2))
# 1 2 () 2 3 {}
print(fun(1,2,3,4,d=2, h=3,r=3))
# 1 2 (3, 4) 2 3 {'h': 3, 'r': 3}
t = (1,2,3,4)
d = {'h': 3, 'r': 3, 'd': 2}
print(fun(*t, **d))
# 1 2 (3, 4) 2 3 {'h': 3, 'r': 3}
# fun(1)
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # TypeError: fun() missing 1 required keyword-only argument: 'd'
# fun(1,2,3,4)
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # TypeError: fun() missing 1 required keyword-only argument: 'd'
print(fun(1,d=2))
# 1 2 () 2 3 {}
# >>> quit()
lst = [1,2,3]
o = []
for e in lst:
    o.append( e*e)
# ...
print(o)
# [1, 4, 9]
lst = [1,2,3]
o = [e*e for e in lst] #list comprehension
print(o)
# [1, 4, 9]
print({e*e for e in lst})
# {1, 4, 9}
print({e:e*e for e in lst})
# {1: 1, 2: 4, 3: 9}
g = (e*e for e in lst)
print(g)
# <generator object <genexpr> at 0x000000B2F86ED6C8>
print(list(g))
# [1, 4, 9]
#version-1
o = [e*e for e in lst] #list comprehension
print(o)
# [1, 4, 9]
#version-2
g = (e*e for e in lst)
print(g)
# <generator object <genexpr> at 0x000000B2F86ED548>
print(list(g))
# [1, 4, 9]
#list compre - eager computation
#generator expr - lazy computation
#eager vs lazy
#lazy - convert to eager to see result or ???
#lazy - NEVER EVER convert to EAGER
#Lazy - chunk or pagination or LIMIT and OFFSET
# Iterators
g = (e*e for e in lst)
i = iter(g)
print(next(i))
# 1
print(next(i))
# 4
print(next(i))
# 9
# next(i)
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # StopIteration
#API - for
g = (e*e for e in lst)
for e in g:
    print(e)
# ...
# 1
# 4
# 9
#Iterarators - generator expr, generator fn, oops-generator
print(range(10))
# range(0, 10)
print(list(range(10)))
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(zip)
# <class 'zip'>
print(enumerate)
# <class 'enumerate'>
print(map)
# <class 'map'>
print(filter)
# <class 'filter'>
#file is Iterator
##Chunkwise proc
import itertools
print(dir(itertools))
# ['__doc__', '__loader__', '__name__', '__package__', '__spec__', '_grouper', '
# _tee', '_tee_dataobject', 'accumulate', 'chain', 'combinations', 'combinations
# _with_replacement', 'compress', 'count', 'cycle', 'dropwhile', 'filterfalse',
# 'groupby', 'islice', 'permutations', 'product', 'repeat', 'starmap', 'takewhil
# e', 'tee', 'zip_longest']
from it_example import Files
i = Files(r"C:\Windows")
print(list(itertools.islice(i, 20)))
# ['C:\\Windows\\AmazonBrowserBar.ico', 'C:\\Windows\\atiogl.xml', 'C:\\Windows\
# \bfsvc.exe', 'C:\\Windows\\bootstat.dat', 'C:\\Windows\\CoreSingleLanguage.xml
# ', 'C:\\Windows\\CSUP.TXT', 'C:\\Windows\\Desktop-fav-icon-poketalk.ico', 'C:\
# \Windows\\diagerr.xml', 'C:\\Windows\\diagwrn.xml', 'C:\\Windows\\dumpbin.exe'
# , 'C:\\Windows\\explorer.exe', 'C:\\Windows\\find.exe', 'C:\\Windows\\FTData.x
# ml', 'C:\\Windows\\FTDataP.xml', 'C:\\Windows\\FTDataR0.xml', 'C:\\Windows\\FT
# DataR1.xml', 'C:\\Windows\\HelpPane.exe', 'C:\\Windows\\hh.exe', 'C:\\Windows\
# \Lenovo telephony.ico', 'C:\\Windows\\lib.exe']
print(list(itertools.islice(i, 20)))
# ['C:\\Windows\\AmazonBrowserBar.ico', 'C:\\Windows\\atiogl.xml', 'C:\\Windows\
# \bfsvc.exe', 'C:\\Windows\\bootstat.dat', 'C:\\Windows\\CoreSingleLanguage.xml
# ', 'C:\\Windows\\CSUP.TXT', 'C:\\Windows\\Desktop-fav-icon-poketalk.ico', 'C:\
# \Windows\\diagerr.xml', 'C:\\Windows\\diagwrn.xml', 'C:\\Windows\\dumpbin.exe'
# , 'C:\\Windows\\explorer.exe', 'C:\\Windows\\find.exe', 'C:\\Windows\\FTData.x
# ml', 'C:\\Windows\\FTDataP.xml', 'C:\\Windows\\FTDataR0.xml', 'C:\\Windows\\FT
# DataR1.xml', 'C:\\Windows\\HelpPane.exe', 'C:\\Windows\\hh.exe', 'C:\\Windows\
# \Lenovo telephony.ico', 'C:\\Windows\\lib.exe']
i = iter(Files(r"C:\Windows"))
print(list(itertools.islice(i, 20)))
# ['C:\\Windows\\AmazonBrowserBar.ico', 'C:\\Windows\\atiogl.xml', 'C:\\Windows\
# \bfsvc.exe', 'C:\\Windows\\bootstat.dat', 'C:\\Windows\\CoreSingleLanguage.xml
# ', 'C:\\Windows\\CSUP.TXT', 'C:\\Windows\\Desktop-fav-icon-poketalk.ico', 'C:\
# \Windows\\diagerr.xml', 'C:\\Windows\\diagwrn.xml', 'C:\\Windows\\dumpbin.exe'
# , 'C:\\Windows\\explorer.exe', 'C:\\Windows\\find.exe', 'C:\\Windows\\FTData.x
# ml', 'C:\\Windows\\FTDataP.xml', 'C:\\Windows\\FTDataR0.xml', 'C:\\Windows\\FT
# DataR1.xml', 'C:\\Windows\\HelpPane.exe', 'C:\\Windows\\hh.exe', 'C:\\Windows\
# \Lenovo telephony.ico', 'C:\\Windows\\lib.exe']
i = iter(Files(r"C:\Windows"))
##Chunkwise proc
import itertools
print(dir(itertools))
# ['__doc__', '__loader__', '__name__', '__package__', '__spec__', '_grouper', '
# _tee', '_tee_dataobject', 'accumulate', 'chain', 'combinations', 'combinations
# _with_replacement', 'compress', 'count', 'cycle', 'dropwhile', 'filterfalse',
# 'groupby', 'islice', 'permutations', 'product', 'repeat', 'starmap', 'takewhil
# e', 'tee', 'zip_longest']
from it_example import Files
i = iter(Files(r"C:\Windows"))
print(list(itertools.islice(i, 20)))
# ['C:\\Windows\\AmazonBrowserBar.ico', 'C:\\Windows\\atiogl.xml', 'C:\\Windows\
# \bfsvc.exe', 'C:\\Windows\\bootstat.dat', 'C:\\Windows\\CoreSingleLanguage.xml
# ', 'C:\\Windows\\CSUP.TXT', 'C:\\Windows\\Desktop-fav-icon-poketalk.ico', 'C:\
# \Windows\\diagerr.xml', 'C:\\Windows\\diagwrn.xml', 'C:\\Windows\\dumpbin.exe'
# , 'C:\\Windows\\explorer.exe', 'C:\\Windows\\find.exe', 'C:\\Windows\\FTData.x
# ml', 'C:\\Windows\\FTDataP.xml', 'C:\\Windows\\FTDataR0.xml', 'C:\\Windows\\FT
# DataR1.xml', 'C:\\Windows\\HelpPane.exe', 'C:\\Windows\\hh.exe', 'C:\\Windows\
# \Lenovo telephony.ico', 'C:\\Windows\\lib.exe']
print(list(itertools.islice(i, 20)))
# ['C:\\Windows\\MFGSTAT.zip', 'C:\\Windows\\mib.bin', 'C:\\Windows\\notepad.exe
# ', 'C:\\Windows\\ODBC.INI', 'C:\\Windows\\ODBCINST.INI', 'C:\\Windows\\PFRO.lo
# g', 'C:\\Windows\\PidVid_List.txt', 'C:\\Windows\\py.exe', 'C:\\Windows\\pyshe
# llext.amd64.dll', 'C:\\Windows\\pyw.exe', 'C:\\Windows\\regedit.exe', 'C:\\Win
# dows\\RtCamU64.exe', 'C:\\Windows\\RTFTrack.exe', 'C:\\Windows\\runSW.exe', 'C
# :\\Windows\\setupact.log', 'C:\\Windows\\setuperr.log', 'C:\\Windows\\splwow64
# .exe', 'C:\\Windows\\Starter.xml', 'C:\\Windows\\SwUSB.exe', 'C:\\Windows\\sys
# tem.ini']
# Processing of element - Map and Reduce
#map - transforming each element
print(list(itertools.islice(i, 5)))
# ['C:\\Windows\\twain_32.dll', 'C:\\Windows\\unins000.dat', 'C:\\Windows\\unins
# 000.exe', 'C:\\Windows\\win.ini', 'C:\\Windows\\WIN8_1_64']
print(list(map(lambda e: len(e), itertools.islice(i, 5))))
# [32, 28, 23, 23, 20]
print(list(map(lambda e: len(e), itertools.islice(i, 20))))
# [28, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 6
# 1]
print(list(map(lambda e: len(e), itertools.islice(i, 20))))
# [61, 61, 61, 61, 64, 61, 61, 61, 61, 69, 61, 61, 61, 61, 66, 66, 64, 58, 72, 5
# 8]
#filter
print(list(filter(lambda e: e%2==1, map(lambda e: len(e), itertools.islice(i, 20)))))
# [67, 67, 67, 63, 69]
print(list(filter(lambda e: e%2==1, map(lambda e: len(e), itertools.islice(i, 20)))))
# [43, 43, 43]
print(list(filter(lambda e: e%2==1, map(lambda e: len(e), itertools.islice(i, 20)))))
# [29, 31, 31, 31, 31, 31, 31, 31, 43, 43, 43, 43, 69]
#LAZY - NEVER EVER convert to EAGER
#USe map, filter to do the processing
##Understanding yield
def f():
    yield 1
    yield 2
    yield 3
    yield [1,2,3]
    for e in [1,2,3]:
            yield e
# ...
#Yield converts fn to generator
print(f())
# <generator object f at 0x000000B2F8819DC8>
for e in f():
    print(e)
# ...
# 1
# 2
# 3
# [1, 2, 3]
# 1
# 2
# 3
#yield - return with memory
def f():
    yield 1
    yield 2
    yield 3
    yield [1,2,3]
    yield from [1,2,3]
# ...
for e in f():
    print(e)
# ...
# 1
# 2
# 3
# [1, 2, 3]
# 1
# 2
# 3
# >>> quit()
# typle( () )
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # NameError: name 'typle' is not defined
print(type( () ))
# <class 'tuple'>
print(type( (1) ))
# <class 'int'>
print((1+2)*2)
# 6
print(type( (1,) ))
# <class 'tuple'>
# >>> quit()
