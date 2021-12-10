#Type of concurrent programming 
#Single host, single process, multi thread 
#Single Host, multiprocess
#Multihost - Cluster compute 

#Python 
#Single host, single process, multi thread - threading 
#Single Host, multiprocess - multiprocessing

#multiprocessing vs threading 
#API similarity 
#Only Python ref implementation because GIL
#https://docs.python.org/3/library/threading.html
#CPU bound - eg numerical computation - mutliprocessing
#IO bound - accessing site, files - threading 


#Thread - light wt , same process constraint, global can be shared
#process - heavy wt , differnt process have diffent limits , sharing requires multiprocessing.Manger
#Commands - windows 
#tasklist /FI "IMAGENAME eq python.exe"
#taskkill /F /IM python.exe 
#Unix - ps -ef | grep python 

#disav - concurrent program 
#No way to sync - even fn can not return 
'''
Thread and Process sync objects 
    Lock Objects
    RLock Objects
        mutex - one thread at a time 
    Condition Objects
        procucer/consumer 
    Semaphore Objects
        - N thread at time 
    Event Objects
        - pub/sub 
    Timer Objects
        - scheduling a future function
    Barrier Objects
    
Multiple sync object - deadlock 

Map/Reduce - fork/join 
    Collection processing (multithreaded)
    - concurrent.futures 
        managed by Executor service 
Producer/Consumer 
    Queue 
'''

import threading 
import time 

def worker(sleeptime):
    print(threading.current_thread().getName(), "Entered")
    time.sleep(sleeptime)
    print(threading.current_thread().getName(), "Exited")
    
    
if __name__ == '__main__':
    print("sequentially")
    worker(5) #MainThread under MainProcess
    print("Parallely")
    st = time.time()
    ths = []
    for _ in range(10):
        th = threading.Thread(target=worker, args=(5,))
        ths.append(th)
    [th.start() for th in ths]
    [th.join() for th in ths] # waiting for end 
    print("Time taken", time.time()-st, "secs") #?
    



