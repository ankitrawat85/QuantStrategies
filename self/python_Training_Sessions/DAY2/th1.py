#Given directory - get total size recursively 
#Map/Reduce-fork/join - Divide and Conq
# Given dir - find all subdir 
#N threads - mapping - each subdir gives size 
#Main threading - Reducing - summing those sizes 
#concurrent 
import threading , time 
import concurrent.futures
import os, os.path 

def  profile(fun):
    def _inner(*args, **kargs):
        import time
        now = time.time()
        dont_print = 'dont_print' in kargs
        res = fun(*args,**kargs)
        if not dont_print:
            print(fun.__name__, "(", threading.current_thread().getName(), 
                "): ", round(time.time() - now, 2), " secs")
        return res
    return _inner

class FileUtil:    
    def __init__(self, path):
        self.path = path
    def get_size(self, rootpath,files):
        ed = {}
        for file in files:
            try:
                ed[file] = os.path.getsize(os.path.join(rootpath,file))
            except Exception as ex:
                pass
        return ed
        
    @profile
    def getDirSize(self, **kwargs):
        s = 0
        #(directorypath, subdirs, files)
        for rootpath, dirs, files in os.walk(self.path):
            el = self.get_size(rootpath, files)
            #print(el, files,rootpath)
            s += sum(el.values())
        return s 
        
    @profile    
    def getDirSizeThreaded(self, ws=4): # ~ 2-3 times of no of cores 
        s = 0
        rootpath, dirs, files = next( os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())      
        #HOMEWORK - convert to ProcessPoolExecutor - might face one error-try to solve it 
        ex = concurrent.futures.ThreadPoolExecutor(max_workers=ws) #how many threads
        #for each subdir- one thread
        res = ex.map( lambda p: FileUtil(p).getDirSize(dont_print=True), #remove 'dont_print=True' to see thread related info
                    [os.path.join(rootpath,d) for d in dirs])        
        #main thread - summing 
        s += sum(res)
        return s        
        
       
if __name__ == '__main__':
    path = r"C:\windows\system32"
    fiu = FileUtil(path)
    #first time more for cache operations, so do after one time     
    print("sequential")
    r = fiu.getDirSize() 
    print(r)
    print("parallely")
    r = fiu.getDirSizeThreaded() 
    print(r)
    print("parallely")
    r = fiu.getDirSizeThreaded(6) 
    print(r)