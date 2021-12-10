
def dummy():
    print("dummy")

class T:
    def __init__(self, fun):
            self.fun = fun
    def __call__(self, *args, **kwargs):
            print("1")
            res = self.fun(*args, **kwargs)
            print("2")
            return res

@T
def dumm1():
    print("dumm1")

dumm1()
#1
#dumm1
#2

@T
@T
def dumm1():
    print("dumm1")

dumm1()
#1
#1
#dumm1
#2
#2
def f(fun):
    def inn(*args,**kwargs):
        print(11)
        res = fun(*args, **kwargs)
        print(22)
        return res
    return inn

@f
@T
@T
@f
def fumm():
    print("fumm")

fumm()
#11
#1
#1
#11
#fumm
#22
#2
#2
#22

#With arg 
class TT:
    def __init__(self, arg):
        self.arg = arg
    def __call__(self, fun):
        self.fun = fun
        return self.handle
    def handle(self, *args, **kwargs):
        print(13)
        res = self.fun(*args, **kwargs)
        print(14)
        return res 
        
        
@TT(2)
@TT(2)
@T
@f
@T 
def funn2():
    print("fun2")
    
funn2()
#13
#13
#1
#11
#1
#fun2
#2
#22
#2
#14
#14