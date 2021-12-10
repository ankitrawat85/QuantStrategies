#Basic Iterator 
path = "."

def get_files_recursive(path):
    files = glob.glob(os.path.join(glob.escape(path), "*"))
    #print(os.path.join(glob.escape(path), "*"), files)
    for file in files:
        if os.path.isfile(file):
            yield file 
    for file in files:
        if os.path.isdir(file):
            #print("dir", file)
            yield from get_files_recursive(file)
              
        
#TC version - accumulator 
def get_files_immu(paths): 
    subdirs = []
    for path in paths :
        for file in glob.iglob(os.path.join(glob.escape(path), "*")):
            if os.path.isfile(file):
                yield file 
            elif os.path.isdir(file):
                subdirs.append(file)
    if subdirs:
        yield from  get_files_immu(subdirs)

#Hand 'tco'ed
def get_files_immu_handrolled(paths): 
    while True: 
        subdirs = []
        for path in paths :
            for file in glob.iglob(os.path.join(glob.escape(path), "*")):
                if os.path.isfile(file):
                    yield file 
                elif os.path.isdir(file):
                    subdirs.append(file)
        if not subdirs:
            return 
        paths = subdirs
        
#TCO generator as Decorator 
import sys, glob, os.path
from functools import wraps


class TailRecurseException(Exception):
  def __init__(self, args, kwargs, msg=''):
    super().__init__(msg)
    self.args = args
    self.kwargs = kwargs

def tail_call_optimized(func):
    gens = []
    @wraps(func)
    def _inner(*args, **kwargs):  #this creates first stack frame         
        f = sys._getframe() #current frame
        #f_back is current frame's caller frame 
        #recursion is f.f_back.f_code == f.f_code 
        #but inside _inner, we are calling original fn, func, hence we have to check 2 frames back 
        if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:            
            while True:
                try:
                    gen = func(*args, **kwargs) # this creates 2nd stack frame 
                    for e in gen:
                        yield e 
                    else:
                        return
                except TailRecurseException as ex: # flattens , since in TC, only args changes, so make args immutable
                    args, kwargs = ex.args, ex.kwargs 
    return _inner


@tail_call_optimized
def get_files_immu(paths): 
    subdirs = []
    for path in paths :
        for file in glob.iglob(os.path.join(glob.escape(path), "*")):
            if os.path.isfile(file):
                yield file 
            elif os.path.isdir(file):
                subdirs.append(file)
    if subdirs:
        yield from  get_files_immu(subdirs)


#Experimenting with another flattened version      
def get_files_non_recursive(path):
    subdirs = [path]
    def subdirs_it(path):
        it = glob.iglob(os.path.join(glob.escape(path), "*"))    
        for file in it:
            if os.path.isfile(file):
                yield file 
            elif os.path.isdir(file):
                subdirs.append(file)
    while subdirs:
        p, *subdirs = subdirs
        yield from subdirs_it(p)
        
#class version - recursive
class BFiles: #Bad version 
    def __init__(self, path):
        self.path = path 
    def __iter__(self):
        files = glob.glob(os.path.join(glob.escape(self.path), "*"))
        for file in files:
            if os.path.isfile(file):
                yield file 
        for file in files:
            if os.path.isdir(file):
                yield from BFiles(file)
                
#Another way of flattening call stack        
class Trampoline:
    def __init__(self, gen):
        self.gens = []
        self(gen)
    def __iter__(self):
        while self.gens:
            gen, *self.gens = self.gens 
            yield from gen
    def __call__(self, gen):
        gen.yieldfrom = self
        self.gens.append(gen)
        
class Files:
    def __init__(self, path):
        self.path = path 
    def __iter__(self):
        files = glob.glob(os.path.join(glob.escape(self.path), "*"))
        for file in files:
            if os.path.isfile(file):
                yield file 
        for file in files:
            if os.path.isdir(file):
                self.yieldfrom(Files(file))
#Usage 
for e in Trampoline(Files(path)):
    print(e)


#Decorator version of Above 
class TrampolineD:
    def __init__(self, Gen):
        self.gens = []
        self.Gen = Gen 
    def __iter__(self):
        while self.gens:
            gen, *self.gens = self.gens 
            yield from gen
    def __call__(self, *args, **kwargs):    
        gen = self.Gen(*args, **kwargs)
        gen.yieldfrom = self.noop
        self.gens.append( gen )
        return self
    def noop(self, *args, **kwargs):
        pass

  
@TrampolineD
#earlier code  - chaning name for experimenting  
class Files1:            #Files1 = TrampolineD(Files1)
    def __init__(self, path):
        self.path = path 
    def __iter__(self):
        files = glob.glob(os.path.join(glob.escape(self.path), "*"))
        for file in files:
            if os.path.isfile(file):
                yield file 
        for file in files:
            if os.path.isdir(file):
                self.yieldfrom(Files1(file))

for e in Files(path):
    print(e)



#######################
#Asyncio version 
import asyncio 
    
async def aget_files_recursive(paths, *args, post_process_fn=lambda file, *args: print(file)):
    subdirs = []
    #print('aget_files_recursive', paths)
    for p in paths:
        await asyncio.sleep(0)  # allow others 
        for file in glob.iglob(os.path.join(glob.escape(p), "*")):
            if os.path.isfile(file):
                post_process_fn(file, *args)
            elif os.path.isdir(file):
                subdirs.append(file)
    if subdirs:
        #moves to Heap - Trampoline
        await asyncio.create_task(aget_files_recursive(tuple(subdirs), *args, post_process_fn=post_process_fn))

#Queue version - producer/consumer 
def get_files_dirs(path):
    files, subdirs = [], []
    it = glob.glob(os.path.join(glob.escape(path), "*"))    
    for file in it:
        if os.path.isfile(file):
            files.append(file)
        elif os.path.isdir(file):
            subdirs.append(file)
    return tuple(files), tuple(subdirs)
    
async def put_files(files_q, files):
    #print("put_files", files_q, files)
    for file in files:
        await files_q.put(file)
        
async def producer(name, files_q, paths):
    print("Starting ", name, paths)
    subdirs = [*paths]    
    while subdirs:
        await asyncio.sleep(0)  #asking others 
        p, *subdirs = subdirs
        files, dirs = get_files_dirs(p)
        [subdirs.append(d) for d in dirs]
        await put_files(files_q, files)
    print("Ending ", name)
        
async def consumer(name, files_q, lock, post_process_coro = None):
    print("Starting ", name)
    while True:
        await asyncio.sleep(0)
        file = await files_q.get()        
        if post_process_coro:
            await post_process_coro(file, lock, name)
        files_q.task_done()
    print("Ending ", name)
    
async def post_process_coro(file, lock, name):
    async with lock:
        print(f"{name}>", file)
        
async def aget_files_queue(path, cons_c=3, per_prod=3):
    files_q = asyncio.Queue()
    lock = asyncio.Lock()

    workers, producers = [], []
    for i in range(cons_c):
        task = asyncio.create_task(consumer(f'worker-{i}', files_q, lock, post_process_coro))
        #print(task)
        workers.append(task)
        
    files, subdirs = get_files_dirs(path)
    await put_files(files_q, files)
    how_many_producers = len(subdirs) // per_prod + 1
    #print(subdirs, how_many_producers)
    for i in range(how_many_producers):
        paths = subdirs[i*per_prod: (i+1)*per_prod]
        #print("paths", paths)
        task = asyncio.create_task(producer(f'producer-{i}', files_q, paths))
        #print(task)
        producers.append(task)
    #wait for all done 
    await asyncio.sleep(1)
    #print(files_q)
    #print("Pending tasks at exit: %s" % asyncio.Task.all_tasks())
    await files_q.join()
    # Cancel our worker tasks.
    [t.cancel() for t in workers + producers]
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*(workers + producers), return_exceptions=True)

#print("==========")
asyncio.run(aget_files_queue(path))
print("==========")
asyncio.run(aget_files_recursive([path]))
