import pytest

'''
function: the default scope, the fixture is destroyed at the end of the test.
class: the fixture is destroyed during teardown of the last test in the class.
module: the fixture is destroyed during teardown of the last test in the module.
package: the fixture is destroyed during teardown of the last test in the package.
session: the fixture is destroyed at the end of the test session.
'''

@pytest.fixture(scope='module')
def amounts():   #Test fixture name = method name 
    am = [100, -200, 300, -400, 400] 
    return am 
