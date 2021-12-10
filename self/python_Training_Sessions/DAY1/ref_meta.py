def some_dummy_method(self, *args, **kwargs):
    print(args, kwargs)
    return "some_return"

class M(type):
    def __new__(meta, c, s, cd):  #meta, classname, supers, classdict #at class definition
        print("meta.__new__")
        print(meta, c, s, cd)
        #metaprograming - modify classdict to inject some functionality 
        cd['meta_injected_method'] = some_dummy_method
        return type.__new__(meta,c,s,cd)  #calls meta.__init__
    def __call__(*args, **kargs):    #calls at instance creation
        print("meta.__call__")
        return type.__call__(*args, **kargs)
    def __init__ (c, cn, s, cd):   #class, classname, supers, classdict #class definition
        print("meta.__init__")
        print(c,cn,s,cd)
        return type.__init__(c,cn,s,cd)
	
	
class A(metaclass=M):   #object py2.x
    #__metaclass__ = M  #py2.x
    def __new__(cls):           #called at instance creation, Note this is classmethod!!!
        print("A's new")
        return object.__new__(cls)  #calls self.__init__
    def __init__(self):
        print("A's init")
    def __call__(self, *args, **kargs):
        print("A's call")


#above instantly prints below
#meta.__new__
#<class '__main__.m'> A () {'__module__': '__main__', '__qualname__': 'A'}  #meta, classname, supers, classdict
#meta.__init__
#<class '__main__.A'> A () {'__module__': '__main__', '__qualname__': 'A'}  #class, classname, supers, classdict 

if __name__ == '__main__':
    a = A()
    #meta.__call__
    #A's new
    #A's init
    print(a.meta_injected_method("arg1", "arg2"))
    #('arg1', 'arg2') {}
    #some_return
    a()
    #A's call
