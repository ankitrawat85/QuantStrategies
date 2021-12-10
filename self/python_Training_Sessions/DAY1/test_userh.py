#Execute by 
#pytest -v test_userh.py 
#for cov 
#pytest --cov=userh --cov-report term-missing test_userh.py 
from userh import * 

'''
$ pytest --help 
-k EXPRESSION         only run tests which match the given substring
                      expression. An expression is a python evaluatable
                      expression where all names are substring-matched
                      against test names and their parent classes. Example:
                      -k 'test_method or test_other' matches all test
                      functions and classes whose name contains
                      'test_method' or 'test_other', while -k 'not
                      test_method' matches those that don't contain
                      'test_method' in their names. Additionally keywords
                      are matched to classes and functions containing extra
                      names in their 'extra_keyword_matches' set, as well as

In our case, name of ts are 
test_userh.py::TestUser::test_silver PASSED
test_userh.py::TestUser::test_gold PASSED
test_userh.py::TestUser::test_normal PASSED
test_userh.py::test_ba_str PASSED

#filtering - only TestUser suite
$ pytest -k "TestUser" -v test_userh.py 
#No TestUser suite
$ pytest -k "not TestUser" -v test_userh.py 
'''

#Test suite - is collection of similar testcases inside a Class 
#Testcase - method with prefix 'test' and having assert
class TestUser: 
    def test_silver(self, amounts):  #amounts is test fixture from conftest.py
        u = SilverUser("Silver", 100)
        #amounts = [100, -200, 300, -400, 400] #Test data or fixture 
        for am in amounts:
            u.transact(am)
        assert u.account.amount == 706
    def test_gold(self, amounts):
        u = GoldUser("Gold", 100)
        #amounts = [100, -200, 300, -400, 400] #Test data or fixture 
        for am in amounts:
            u.transact(am)
        assert u.account.amount == 710
    def test_normal(self, amounts):
        u = NormalUser("Gold", 100)
        #amounts = [100, -200, 300, -400, 400] #Test data or fixture 
        for am in amounts:
            u.transact(am)
        assert u.account.amount == 700    
    
#Can you include line no 17 in our coverage?
def test_ba_str():
    ba = BankAccount(100)
    assert str(ba) == 'BankAccount(100)'

#HOMEWORK - include all these 35, 38, 49, 56, 58

