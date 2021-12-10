from __future__ import print_function 
import glob  # dir in python 
import os.path 
import time 

import sys 
#print(sys.argv)
DEBUG = True if len(sys.argv) > 1 else False 

def print_debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def profile(fun):   #getMaxFilename
    print_debug("profile entered", fun)
    def _inner(*args, **kwargs):  #args=('D:\\handson', 2) kwargs={}
        print_debug("profile:_inner entered", args, kwargs)
        st = time.time()  
        res = fun(*args, **kwargs)  #getMaxFilename('D:\\handson', 2)
        print("Time taken:", time.time()-st, "secs")
        print_debug("profile:_inner returned", res)
        return res
    print_debug("profile returned", _inner)
    return _inner


def profile_v2(prec):   #7
    print_debug("profile_v2 entered", prec)
    def _outer(fun): #getMaxFilename
        print_debug("profile_v2:_outer entered", fun)
        def _inner(*args, **kwargs):  #args=('D:\\handson', 2) kwargs={}
            print_debug("profile_v2:_inner entered", args, kwargs)
            st = time.time()  
            res = fun(*args, **kwargs)  #getMaxFilename('D:\\handson', 2)
            print("Time taken:", round(time.time()-st,prec), "secs")
            print_debug("profile_v2:_inner returned", res)
            return res
        print_debug("profile_v2:_outer returned", _inner)
        return _inner
    print_debug("profile_v2 returned", _outer)
    return _outer

#Given a directory, find out the file Name having max size recursively 

#HOMEWORK - Understand how stacking works 
@profile_v2(7)
@profile 
#without arg 
#getMaxFilename = profile(getMaxFilename) = _inner
#with arg 
#getMaxFilename = profile_v2(7)(getMaxFilename) 
#               = _outer(getMaxFilename) = _inner
def getMaxFilename(path, how_many=1): 
    """
    Steps 
    1. Create a dict with filename as key and size as value 
       Use glob and os.path 
       glob.glob - to get list of files in the path 
       os.path.isfile - to filter only files 
       os.path.getsize - to get size 
     2. Sort the dict based on value 
     3. return the last file name if sorted ascending order     
    """
    def get_files(path, ed={}): #empty dict
        files = glob.glob(os.path.join(path, "*"))
        for file in files:
            if os.path.isfile(file):
                ed[file] = os.path.getsize(file)
        for file in files:
            if not os.path.isfile(file):
                get_files(file, ed)   
        return ed 
    allfiles = get_files(path)
    sted = sorted(allfiles, key=lambda k: allfiles[k])
    return sted[-how_many:] if sted else '' #last 

if __name__ == '__main__':
    path = r"D:\handson"  #?
    print( getMaxFilename(path, 2))  #_inner(path, 2)