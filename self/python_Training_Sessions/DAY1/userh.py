# Bank User has name and account. There are two types of Users
# Normal and privileged user . There are two types of privileged
# users, Gold and Silver. Gold has cashback of 5% and Silver has 
# cashback of 3% of expenditure when they spend any cash 

#noun - potential class 
#verbs - methods of those class 
from __future__ import print_function

class NotEnoughBalance(Exception):  #inheritance 
    pass 

class BankAccount:
    def __init__(self, initAmount):
        self.amount = initAmount
    def __str__(self):      #toString
        return "BankAccount("+str(self.amount)+")"
    def transact(self, amount):
        if self.amount + amount < 0:
            raise NotEnoughBalance("not possible")
        self.amount += amount 
        
#has relation - containment
#is relation - inheritance

from abc import ABCMeta, abstractmethod
class BankUser(metaclass=ABCMeta):
    #in py2.7 
    #__metaclass__ = ABCMeta
    #class variable - all have the same value - BankUser.how_many_users 
    how_many_users = {'AllUsers': 0}    
    #class method - first arg is class 
    @classmethod 
    def how_many(cls):
        return cls.how_many_users
    @staticmethod 
    def version():  #there is no first arg #Main usecase= NS kind of usage - rare 
        return "1.0.0"
    #instance method - first arg - instance
    def __init__(self, name, initAmount): #has relation 
        self.name = name   #instance variable 
        self.account = BankAccount(initAmount)
        self.update_bank_users()
    def update_bank_users(self):
        t = self.getUserType()
        if t not in BankUser.how_many_users :
            BankUser.how_many_users[t] = 1
        else:
            BankUser.how_many_users[t] += 1
        BankUser.how_many_users['AllUsers'] += 1
    @abstractmethod  #decorator #enhance original functionality
    def getCashbackPercentage(self):
        return 0 
    @abstractmethod
    def getUserType(self):
        pass 
    def __str__(self):  #template DP
        return  "%s(%s,%s)" % (self.getUserType(), self.name, self.account)
    def transact(self, amount): #template DP 
        try:
            self.account.transact(amount)  #delegation/proxy 
            if amount < 0:
                cashback = self.getCashbackPercentage() * abs(amount)
                self.account.transact(cashback)
        except NotEnoughBalance as ex:
            print(str(ex), "Name:", self.name, "amount:", amount)
    #Property concept - check ref book 
    #property - access a variable, it calls method internally 

#is relation 
# oops - reusability/maintainability - Thick base class and Thin derived class 
class NormalUser(BankUser):
    def getCashbackPercentage(self):
        return super().getCashbackPercentage()
    def getUserType(self):
        return "NormalUser" 
    
class SilverUser(BankUser):
    def getCashbackPercentage(self):
        return 0.03
    def getUserType(self):
        return "SilverUser"  

class GoldUser(BankUser):
    def getCashbackPercentage(self):
        return 0.05
    def getUserType(self):
        return "GoldUser"  

#class PlatUser(BankUser):
#    def getCashbackPercentage(self):
#        return 0.05
 
#file.py - for both module and script 
#module - use with import 
#script - execute from shell 
#__name__ internal variable , in script , == '__main__'
#in module , = module_name, eg here , 'userh'      
if __name__ == '__main__':      # pragma: no cover 
    #ba = BankUser("B", 100)
    #ba = PlatUser("P", 100)
    users = [GoldUser("Gold", 100), SilverUser("Silver", 100), 
             NormalUser("Normal", 100)]
    amounts = [100, -200, 300, -400, 400]
    for u in users:
        for am in amounts:
            u.transact(am)
        print(u)
    users = [GoldUser("Gold", 100), SilverUser("Silver", 100), 
             NormalUser("Normal", 100)]
    print(BankUser.how_many()) #accessing class method 
    print(BankUser.version())  # accessing static method 