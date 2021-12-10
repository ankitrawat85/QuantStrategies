import multiprocessing 
import time 

def worker(sleeptime):
    print(multiprocessing.current_process().name, "Entered")
    time.sleep(sleeptime)
    print(multiprocessing.current_process().name, "Exited")
    
    
if __name__ == '__main__':
    print("sequentially")
    worker(5) #MainThread under MainProcess
    print("Parallely")
    st = time.time()
    ths = []
    for _ in range(10):  #creates 10 python process + 1 Manager process for IPC
        th = multiprocessing.Process(target=worker, args=(5,))
        ths.append(th)
    [th.start() for th in ths]
    [th.join() for th in ths] # waiting for end 
    print("Time taken", time.time()-st, "secs") #?