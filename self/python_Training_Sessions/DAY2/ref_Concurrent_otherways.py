import threading , time 
import concurrent.futures
import os, os.path 

from functools import wraps 

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
    
def  aprofile(afun):
    async def _inner(*args, **kargs):
        import time
        now = time.time()
        dont_print = 'dont_print' in kargs
        res = await afun(*args,**kargs)
        if not dont_print:
            print(afun.__name__, "(", threading.current_thread().getName(), 
                "): ", round(time.time() - now, 2), " secs")
        return res
    return _inner
    
#note local lambda can not be prickled , so 
#it is written as top level function which is pickable 
# note run time might be higher than sequential because of process creation
def get_dir_size(p):
    return FileUtil(p).getDirSize(dont_print=True)

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
        for rootpath, dirs, files in os.walk(self.path):
            el = self.get_size(rootpath, files)
            #print(el, files,rootpath)
            s += sum(el.values())
        return s 
    @profile
    def getDirSizeThreaded(self, ws=4):
        import os, os.path 
        s = 0
        ex = concurrent.futures.ThreadPoolExecutor(max_workers=ws)
        rootpath, dirs, files = next(os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #for other dirs 
        res = ex.map(lambda p : FileUtil(p).getDirSize(dont_print=True), 
            [os.path.join(rootpath,d) for d in dirs])
        s += sum(res)
        ex.shutdown()
        return s 
    @profile
    def getDirSizeThreadedSubmit(self, ws=4):
        import os, os.path 
        s = 0
        ex = concurrent.futures.ThreadPoolExecutor(max_workers=ws)
        rootpath, dirs, files = next(os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #for other dirs 
        fs = [ ex.submit( lambda p : FileUtil(p).getDirSize(dont_print=True), 
                    os.path.join(rootpath,d))
              for d in dirs]
        for res in concurrent.futures.as_completed(fs):
            s += res.result()
        ex.shutdown()
        return s 
    @profile
    def getDirSizeThreadedP(self, ws=4):
        import os, os.path 
        s = 0
        ex = concurrent.futures.ProcessPoolExecutor(max_workers=ws)
        rootpath, dirs, files = next(os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #for other dirs 
        res = ex.map(get_dir_size, 
            [os.path.join(rootpath,d) for d in dirs])
        s += sum(res)
        ex.shutdown()
        return s 
    @profile
    def getDirSizeThreadedSubmitP(self, ws=4):
        import os, os.path 
        s = 0
        ex = concurrent.futures.ProcessPoolExecutor(max_workers=ws)
        rootpath, dirs, files = next(os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #for other dirs 
        fs = [ ex.submit( get_dir_size, 
                    os.path.join(rootpath,d))
              for d in dirs]
        for res in concurrent.futures.as_completed(fs):
            s += res.result()
        ex.shutdown()
        return s 
    @profile
    def getDirSizePoolP(self, ws=4):
        import os, os.path 
        s = 0
        rootpath, dirs, files = next(os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #for other dirs 
        with multiprocessing.Pool(processes=ws) as pool: 
            res = pool.map(get_dir_size, 
                [os.path.join(rootpath,d) for d in dirs])
        
        s += sum(res)
        return s 
        
    @profile
    def getDirSizeThreadedEE(self, executor):
        s = 0
        rootpath, dirs, files = next(os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #for other dirs 
        res = executor.map(lambda p : FileUtil(p).getDirSize(dont_print=True), 
            [os.path.join(rootpath,d) for d in dirs])
        s += sum(res)
        return s 
    @aprofile 
    async def getDirSizeAsync(self, executor=None):
        s = 0
        rootpath, dirs, files = next( os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #awaitable loop.run_in_executor(executor, func, *args)
        #awaitable asyncio.gather(*aws, loop=None, return_exceptions=False)
        loop = asyncio.get_running_loop()
        async_jobs = [loop.run_in_executor(executor,
                                     lambda p: FileUtil(p).getDirSize(dont_print=True), 
                                     os.path.join(rootpath,d)) for d in dirs]
        res = await asyncio.gather(*async_jobs)
        s += sum(res)
        return s 
        
    @aprofile 
    async def getDirSizeAsync_v2(self,  executor=None):
        s = 0
        rootpath, dirs, files = next( os.walk(self.path))
        el = self.get_size(rootpath, files)
        s += sum(el.values())
        #awaitable loop.run_in_executor(executor, func, *args)
        #awaitable asyncio.gather(*aws, loop=None, return_exceptions=False)
        loop = asyncio.get_running_loop()
        async_jobs = {loop.run_in_executor(executor,
                                     lambda p: FileUtil(p).getDirSize(dont_print=True), 
                                     os.path.join(rootpath,d)) for d in dirs}                                     
        for coro in asyncio.as_completed(async_jobs):
            size = await coro
            s += size            
        return s 
        
if __name__ == '__main__':
    path = r"C:\windows\system32"
    fiu = FileUtil(path)
    #first time more for cache operations, so do after one time     
    print("sequential")
    r = fiu.getDirSize()    

    print("Now parallel")
    rs = fiu.getDirSizeThreaded()
    
    print("Now parallel")
    rs = fiu.getDirSizeThreaded(8)
    
    print("Now parallel")
    rs = fiu.getDirSizeThreadedSubmit()  

    print("Now parallel")
    rs = fiu.getDirSizeThreadedP()
    
    print("Now parallel with 8")
    rs = fiu.getDirSizeThreadedP(8)
    
    print("Now parallel with submit ")
    rs = fiu.getDirSizeThreadedSubmitP()  
    
    print("Now parallel with Pool ")
    rs = fiu.getDirSizePool()  
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=ws)  as executor:
        r = fiu.getDirSizeThreadedEE(executor) 
        print(r)
        r = asyncio.run(fiu.getDirSizeAsync(executor))
        print(r)
        r = asyncio.run(fiu.getDirSizeAsync_v2(executor))
        print(r)
        import timeit 
        print(timeit.timeit(stmt="asyncio.run(fiu.getDirSizeAsync_v2(executor))", number=10, globals=globals()))

