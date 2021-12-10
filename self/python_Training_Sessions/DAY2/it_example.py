#Given a directory, get all the files recursively 
import glob  # dir in python 
import os.path 

def get_files(path, lst): 
    files = glob.glob(os.path.join(path, "*"))
    for file in files:
        if os.path.isfile(file):
            lst.append(file)
    for file in files:
        if not os.path.isfile(file):
            get_files(file, lst)   
    return lst 
    
#gen-fn 
def get_files_it(path): 
    files = glob.glob(os.path.join(path, "*"))
    for file in files:
        if os.path.isfile(file):
            yield file 
    for file in files:
        if not os.path.isfile(file):
            for e in  get_files_it(file):
                yield e

#OOPs 
class Files:
    def __init__(self, path):
        self.path = path 
    def __iter__(self): 
        files = glob.glob(os.path.join(self.path, "*"))
        for file in files:
            if os.path.isfile(file):
                yield file 
        for file in files:
            if not os.path.isfile(file):
                yield from Files(file)         
    
if __name__ == '__main__':
    path = r"C:\Windows"  
    #for file in get_files_it(path):
    for file in Files(path):
        print(file)