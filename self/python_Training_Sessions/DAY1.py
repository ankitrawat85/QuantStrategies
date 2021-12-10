lst = [1,2,3]
print(2 in lst)
# True
print(len(lst))
# 3
print(lst[0])
# 1
lst[0] = 20
for e in lst:
    print(e)
# ...
# 20
# 2
# 3
print(lst + [1,2])
# [20, 2, 3, 1, 2]
###Ops overload
print(list.__add__(lst, [1,2]))
# [20, 2, 3, 1, 2]
print(list.__contains__(lst, 2))
# True
print(list.__getitem__(lst, 0))
# 20
list.__setitem__(lst, 0, 200)
print(lst)
# [200, 2, 3]
print(dir(list))
# ['__add__', '__class__', '__contains__', '__delattr__', '__delitem__', '__dir_
# _', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getite
# m__', '__gt__', '__hash__', '__iadd__', '__imul__', '__init__', '__init_subcla
# ss__', '__iter__', '__le__', '__len__', '__lt__', '__mul__', '__ne__', '__new_
# _', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__rmul__', '__
# setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 'appen
# d', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'r
# everse', 'sort']
print([1,2] * 4)
# [1, 2, 1, 2, 1, 2, 1, 2]
print([1,2] == [1,2])
# True
# >>> quit()
# >>> quit()
class A:
    pass
# ...
class B(A):
    pass
# ...
class C(B,A):
    pass
# ...
c = C()
C.__init__(c)
print(C.__mro__  ) # Method resolution order
# (<class '__main__.C'>, <class '__main__.B'>, <class '__main__.A'>, <class 'obj
# ect'>)
print(C.__init__)
# <slot wrapper '__init__' of 'object' objects>
#class object which is root of any class parents
print(dir(object))
# ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__
# ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass_
# _', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '_
# _repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']
# c.a
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # AttributeError: 'C' object has no attribute 'a'
# # >>>
# # >>>
#Class creates instance - __new__ and __init__
#Metaclass creates class - by overriding __new__
#Metaprogramming - deriving from metaclass, hooking into creation process
print(c.__class__  ) # it's a class
# <class '__main__.C'>
print(C.__class__ ) # now it is metaclass
# <class 'type'>
#type is the default metaclass
#Deriving from 'type' and using metaclas='THAT_CLASS' is way of metaprogra
# mming
print(object.__class__)
# <class 'type'>
# >>> quit()
import abc
print(dir(abc))
# ['ABC', 'ABCMeta', '__builtins__', '__cached__', '__doc__', '__file__', '__loa
# der__', '__name__', '__package__', '__spec__', '_abc_init', '_abc_instancechec
# k', '_abc_register', '_abc_subclasscheck', '_get_dump', '_reset_caches', '_res
# et_registry', 'abstractclassmethod', 'abstractmethod', 'abstractproperty', 'ab
# stractstaticmethod', 'get_cache_token']
# >>> quit()
# >>> quit()
def add(x,y):
    y = 20
    return x+y
# ...
print(add(2,200))
# 22
# >>> quit()
#  x = 20
# #   File "<stdin>", line 1
# #     x = 20
# #     ^
# # IndentationError: unexpected indent
# raise IndentationError("NOT")
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # IndentationError: NOT
# # >>> quit()
