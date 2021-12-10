path = r"D:\handson\DAY3\data\example.xml"
#SQL DATA - 2D flattened DATA
#NO SQL DATA - xml/json - nested data
##XML
import xml.etree.ElementTree as ET
tr = ET.parse(path)
root = tr.getroot()
print(type(root))
# <class 'xml.etree.ElementTree.Element'>
print(root.tag, root.attrib, root.text)
# ('data', {}, '\n    ')
#Extract all ranks
nn = root.findall("./country/rank")
print(nn)
# [<Element 'rank' at 0x00000005D77FD778>, <Element 'rank' at 0x00000005D77FD958
# >, <Element 'rank' at 0x00000005D77FDAE8>]
print([ n.text for n in nn])
# ['1', '4', '68']
#XML disadv - it has String Datatype
print([ int(n.text) for n in nn])
# [1, 4, 68]
##XPATH
#https://www.w3schools.com/xml/xpath_syntax.asp
print(root.findall(".//rank"))
# [<Element 'rank' at 0x00000005D77FD778>, <Element 'rank' at 0x00000005D77FD958
# >, <Element 'rank' at 0x00000005D77FDAE8>]
print(root.findall(".//year/.."))
# [<Element 'country' at 0x00000005D77FD728>, <Element 'country' at 0x00000005D7
# 7FD908>, <Element 'country' at 0x00000005D77FDA98>]
print(root.findall(".//country"))
# [<Element 'country' at 0x00000005D77FD728>, <Element 'country' at 0x00000005D7
# 7FD908>, <Element 'country' at 0x00000005D77FDA98>]
print(root.findall(".//year/../.."))
# [<Element 'data' at 0x00000005D77FD6D8>]
print(root.findall(".//year/..[@name='Singapore']"))
# [<Element 'country' at 0x00000005D77FD908>]
print(root.findall(".//neighbor[2]"))
# [<Element 'neighbor' at 0x00000005D77FD8B8>, <Element 'neighbor' at 0x00000005
# D77FDC78>]
print(root.findall(".//year/..[@name='Singapore']"))
# [<Element 'country' at 0x00000005D77FD908>]
print([ n for n in root.findall(".//year/..") if n.attrib['name'] == 'Singapore'])
# [<Element 'country' at 0x00000005D77FD908>]
##Extraction
#Create XPATH, use findall and use comprehension to get data
#Extract all country names
#output data type required - List of str(cnames)
#[ e*e for e in lst]
# >>>
# 
# D:\handson>python
# Python 3.7.6 (tags/v3.7.6:43364a7ae0, Dec 19 2019, 00:42:30) [MSC v.1916 64 bi
# t (AMD64)] on win32
# Type "help", "copyright", "credits" or "license" for more information.
path = r"D:\handson\DAY3\data\example.xml"
import xml.etree.ElementTree as ET
tr = ET.parse(path)
root = tr.getroot()
print([ n.attrib['name'] for n in root.findall("./country") ])
# ['Liechtenstein', 'Singapore', 'Panama']
print([ n.attrib['name'] for n in tr.getroot().findall("./country")])
# ['Liechtenstein', 'Singapore', 'Panama']
print(root.tag, root.attrib, root.text)
# ('data', {}, '\n    ')
##Extract country names and it's neighbors
#Output data type required - ? dict - key-cnams
#value - list of nnames
print({ c.attrib['name'] : [    n.attrib['name'] for n in c.findall(".//neighbor")]  for c in root.findall(".//country")})
# {'Liechtenstein': ['Austria', 'Switzerland'], 'Singapore': ['Malaysia'], 'Pana
# ma': ['Costa Rica', 'Colombia']}
#equiv
o = {}
for c in root.findall(".//country"):
    lst = []
    for n in c.findall(".//neighbor"):
            lst.append( n.attrib['name'] )
    o[c.attrib['name']] = lst
# ...
print(o)
# {'Liechtenstein': ['Austria', 'Switzerland'], 'Singapore': ['Malaysia'], 'Pana
# ma': ['Costa Rica', 'Colombia']}
# >>>
# >>>
#Transformation
print(dir(root))
# ['__class__', '__copy__', '__deepcopy__', '__delattr__', '__delitem__', '__dir
# __', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getit
# em__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__',
# '__le__', '__len__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex
# __', '__repr__', '__setattr__', '__setitem__', '__setstate__', '__sizeof__', '
# __str__', '__subclasshook__', 'append', 'attrib', 'clear', 'extend', 'find', '
# findall', 'findtext', 'get', 'getchildren', 'getiterator', 'insert', 'items',
# 'iter', 'iterfind', 'itertext', 'keys', 'makeelement', 'remove', 'set', 'tag',
#  'tail', 'text']
for rank in root.iter('rank'):
    new_r = int(rank.text) + 1
    rank.text = str(new_r)
    rank.set('updated', 'yes')
# ...
tr.write('output.xml')
with open('output.xml') as f:
    print(f.read())
# ...
# <data>
#     <country name="Liechtenstein">
#         <rank updated="yes">2</rank>
#         <year>2008</year>
#         <gdppc>141100</gdppc>
#         <neighbor direction="E" name="Austria" />
#         <neighbor direction="W" name="Switzerland" />
#     </country>
#     <country name="Singapore">
#         <rank updated="yes">5</rank>
#         <year>2011</year>
#         <gdppc>59900</gdppc>
#         <neighbor direction="N" name="Malaysia" />
#     </country>
#     <country name="Panama">
#         <rank updated="yes">69</rank>
#         <year>2011</year>
#         <gdppc>13600</gdppc>
#         <neighbor direction="W" name="Costa Rica" />
#         <neighbor direction="E" name="Colombia" />
#     </country>
# </data>
##Creation
print(dir(ET))
# ['Comment', 'Element', 'ElementPath', 'ElementTree', 'HTML_EMPTY', 'PI', 'Pars
# eError', 'ProcessingInstruction', 'QName', 'SubElement', 'TreeBuilder', 'VERSI
# ON', 'XML', 'XMLID', 'XMLParser', 'XMLPullParser', '_Element_Py', '_ListDataSt
# ream', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__load
# er__', '__name__', '__package__', '__spec__', '_escape_attrib', '_escape_attri
# b_html', '_escape_cdata', '_get_writer', '_namespace_map', '_namespaces', '_ra
# ise_serialization_error', '_sentinel', '_serialize', '_serialize_html', '_seri
# alize_text', '_serialize_xml', 'collections', 'contextlib', 'dump', 'fromstrin
# g', 'fromstringlist', 'io', 'iselement', 'iterparse', 'parse', 're', 'register
# _namespace', 'sys', 'tostring', 'tostringlist', 'warnings']
a = ET.Element('a')
# b = ET.subElement(a, 'b', attrib=dict(count='1'))
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # AttributeError: module 'xml.etree.ElementTree' has no attribute 'subElement'
b = ET.SubElement(a, 'b', attrib=dict(count='1'))
b.text = "Hello"
print(ET.dump(a))
# <a><b count="1">Hello</b></a>
print(type(root))
# <class 'xml.etree.ElementTree.Element'>
# >>>
#XML - String datatype only
#XML - has NS
##NS
path = r"D:\handson\DAY3\data\example1.xml"
tr1 = ET.parse(path)
r1 = tr1.getroot()
print(r1.tag)
# '{http://people.example.com}actors'
ns = dict(fictional="http://characters.example.com",          default="http://people.example.com")
print(r1.findall(".//fictional:character", ns))
# [<Element '{http://characters.example.com}character' at 0x000000A96E1D0DB8>, <
# Element '{http://characters.example.com}character' at 0x000000A96E1D0E08>, <El
# ement '{http://characters.example.com}character' at 0x000000A96E1D0EF8>, <Elem
# ent '{http://characters.example.com}character' at 0x000000A96E1D0F48>, <Elemen
# t '{http://characters.example.com}character' at 0x000000A96E1D0F98>]
print([n.text for n in r1.findall(".//fictional:character", ns)])
# ['Lancelot', 'Archie Leach', 'Sir Robin', 'Gunther', 'Commander Clement']
# >>> quit()
##JSON
path = r"D:\handson\DAY3\data\example.json"
import json
with open(path) as f:
    obj = json.load(f)
# ...
print(obj)
# [{'empId': 1, 'details': {'firstName': 'John', 'lastName': 'Smith', 'isAlive':
#  True, 'age': 25, 'salary': 123.5, 'address': {'streetAddress': '21 2nd Street
# ', 'city': 'New York', 'state': 'NY', 'postalCode': '10021-3100'}, 'phoneNumbe
# rs': [{'type': 'home', 'number': '212 555-1234'}, {'type': 'office', 'number':
#  '646 555-4567'}, {'type': 'mobile', 'number': '123 456-7890'}], 'children': [
# ], 'spouse': None}}, {'empId': 20, 'details': {'firstName': 'Johns', 'lastName
# ': 'Smith', 'isAlive': True, 'age': 25, 'salary': 123.5, 'address': {'streetAd
# dress': '21 2nd Street', 'city': 'New York', 'state': 'CL', 'postalCode': '100
# 21-3100'}, 'phoneNumbers': [{'type': 'home', 'number': '212 555-1234'}, {'type
# ': 'office', 'number': '646 555-4567'}, {'type': 'mobile', 'number': '123 456-
# 7890'}], 'children': [], 'spouse': None}}]
print(type(obj))
# <class 'list'>
print(type(obj[0]))
# <class 'dict'>
#List of dict
#Extract all empid
print([emp["empId"] for emp in obj])
# [1, 20]
##Extract full names of all emps
#firstName + lastName
#Output - list
# with open(path) as f:
# obj = json.load(f)
# #   File "<stdin>", line 2
# #     obj = json.load(f)
# #       ^
# # IndentationError: expected an indented block
with open(path) as f:
    obj = json.load(f)
# ...
print([emp["details"]["firstName"]+" "+emp["details"]["lastName"] for emp in obj])
# ['John Smith', 'Johns Smith']
n= [emp["details"] for emp in obj]
print(n[0]["firstName"] + " " + n[0]["lastName"])
# John Smith
# >>>
# >>>
with open(path) as f:
    obj = json.load(f)
# ...
print(obj)
# [{'empId': 1, 'details': {'firstName': 'John', 'lastName': 'Smith', 'isAlive':
#  True, 'age': 25, 'salary': 123.5, 'address': {'streetAddress': '21 2nd Street
# ', 'city': 'New York', 'state': 'NY', 'postalCode': '10021-3100'}, 'phoneNumbe
# rs': [{'type': 'home', 'number': '212 555-1234'}, {'type': 'office', 'number':
#  '646 555-4567'}, {'type': 'mobile', 'number': '123 456-7890'}], 'children': [
# ], 'spouse': None}}, {'empId': 20, 'details': {'firstName': 'Johns', 'lastName
# ': 'Smith', 'isAlive': True, 'age': 25, 'salary': 123.5, 'address': {'streetAd
# dress': '21 2nd Street', 'city': 'New York', 'state': 'CL', 'postalCode': '100
# 21-3100'}, 'phoneNumbers': [{'type': 'home', 'number': '212 555-1234'}, {'type
# ': 'office', 'number': '646 555-4567'}, {'type': 'mobile', 'number': '123 456-
# 7890'}], 'children': [], 'spouse': None}}]
# >>>
# >>>
##Extract full names
print([emp["details"]["firstName"]+" "+emp["details"]["lastName"] for emp in obj])
# ['John Smith', 'Johns Smith']
# >>>
##Extract all office phones of state 'NY' if employee is alive
print([ ph['number']   for emp in obj for ph in emp['details']['phoneNumbers']   if ph['type'] == 'office'])
# ['646 555-4567', '646 555-4567']
print([ ph['number']   for emp in obj for ph in emp['details']['phoneNumbers']   if ph['type'] == 'office' and emp['details']['address']['state'] == 'NY'])
# ['646 555-4567']
print([emp["details"]["phoneNumbers"] for emp in obj if emp["details"]["isAlive"] and  emp["details"]["address"]["state"] == "NY"])
# [[{'type': 'home', 'number': '212 555-1234'}, {'type': 'office', 'number': '64
# 6 555-4567'}, {'type': 'mobile', 'number': '123 456-7890'}]]
# >>>
print(dir(json))
# ['JSONDecodeError', 'JSONDecoder', 'JSONEncoder', '__all__', '__author__', '__
# builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '_
# _package__', '__path__', '__spec__', '__version__', '_default_decoder', '_defa
# ult_encoder', 'codecs', 'decoder', 'detect_encoding', 'dump', 'dumps', 'encode
# r', 'load', 'loads', 'scanner']
#dump and load - works file
#dumps and loads - works with string
print(json.dumps(obj))
# '[{"empId": 1, "details": {"firstName": "John", "lastName": "Smith", "isAlive"
# : true, "age": 25, "salary": 123.5, "address": {"streetAddress": "21 2nd Stree
# t", "city": "New York", "state": "NY", "postalCode": "10021-3100"}, "phoneNumb
# ers": [{"type": "home", "number": "212 555-1234"}, {"type": "office", "number"
# : "646 555-4567"}, {"type": "mobile", "number": "123 456-7890"}], "children":
# [], "spouse": null}}, {"empId": 20, "details": {"firstName": "Johns", "lastNam
# e": "Smith", "isAlive": true, "age": 25, "salary": 123.5, "address": {"streetA
# ddress": "21 2nd Street", "city": "New York", "state": "CL", "postalCode": "10
# 021-3100"}, "phoneNumbers": [{"type": "home", "number": "212 555-1234"}, {"typ
# e": "office", "number": "646 555-4567"}, {"type": "mobile", "number": "123 456
# -7890"}], "children": [], "spouse": null}}]'
obj1 = json.loads(json.dumps(obj))
print(obj is obj1)
# False
obj == obj1
# True
##SQL DATA - 2D flatened data
# >>> quit()
import pandas as pd
print(len(dir(pd.DataFrame)))
# 427
#DF - list of columns- list of Series
print(len(dir(pd.Series)))
# 425
print(len(dir(pd)))
# 140
#Trick-1
print(len(set(dir(pd.DataFrame)) & set(dir(pd.Series))))
# 372
#Trick-2
#Pandas_Cheat_Sheet.pdf
import pandas as pd
#read data
iris = pd.read_csv(r"D:\handson\DAY3\data\iris.csv")
#metadata
print(iris.head()  ) # default 5 rows
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name
# 0          5.1         3.5          1.4         0.2  Iris-setosa
# 1          4.9         3.0          1.4         0.2  Iris-setosa
# 2          4.7         3.2          1.3         0.2  Iris-setosa
# 3          4.6         3.1          1.5         0.2  Iris-setosa
# 4          5.0         3.6          1.4         0.2  Iris-setosa
print(iris.columns)
# Index(['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Name'], dtyp
# e='object')
print(iris.dtypes)
# SepalLength    float64
# SepalWidth     float64
# PetalLength    float64
# PetalWidth     float64
# Name            object
# dtype: object
print(len(iris))
# 150
#Access
print(iris['SepalLength'])
# 0      5.1
# 1      4.9
# 2      4.7
# 3      4.6
# 4      5.0
#       ...
# 145    6.7
# 146    6.3
# 147    6.5
# 148    6.2
# 149    5.9
# Name: SepalLength, Length: 150, dtype: float64
print(type(iris['SepalLength']))
# <class 'pandas.core.series.Series'>
print(type(iris))
# <class 'pandas.core.frame.DataFrame'>
print(iris.SepalLength)
# 0      5.1
# 1      4.9
# 2      4.7
# 3      4.6
# 4      5.0
#       ...
# 145    6.7
# 146    6.3
# 147    6.5
# 148    6.2
# 149    5.9
# Name: SepalLength, Length: 150, dtype: float64
print(iris[['SepalLength', 'SepalWidth']])
#      SepalLength  SepalWidth
# 0            5.1         3.5
# 1            4.9         3.0
# 2            4.7         3.2
# 3            4.6         3.1
# 4            5.0         3.6
# ..           ...         ...
# 145          6.7         3.0
# 146          6.3         2.5
# 147          6.5         3.0
# 148          6.2         3.4
# 149          5.9         3.0
# 
# [150 rows x 2 columns]
print(type(iris[['SepalLength', 'SepalWidth']]))
# <class 'pandas.core.frame.DataFrame'>
##Slicing
#.iloc[row_index, column_index]
#.loc[row_id, column_names]
print(iris.head())
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name
# 0          5.1         3.5          1.4         0.2  Iris-setosa
# 1          4.9         3.0          1.4         0.2  Iris-setosa
# 2          4.7         3.2          1.3         0.2  Iris-setosa
# 3          4.6         3.1          1.5         0.2  Iris-setosa
# 4          5.0         3.6          1.4         0.2  Iris-setosa
#row_id = index
print(iris.index)
# RangeIndex(start=0, stop=150, step=1)
print(iris.loc[0:2, ['SepalLength',  'SepalWidth']] ) #end id is inclusive
#    SepalLength  SepalWidth
# 0          5.1         3.5
# 1          4.9         3.0
# 2          4.7         3.2
print(iris.iloc[0:3, [0,1]])
#    SepalLength  SepalWidth
# 0          5.1         3.5
# 1          4.9         3.0
# 2          4.7         3.2
#iloc - end is exclusive
#Loc  - can have boolean condition
print(iris.head())
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name
# 0          5.1         3.5          1.4         0.2  Iris-setosa
# 1          4.9         3.0          1.4         0.2  Iris-setosa
# 2          4.7         3.2          1.3         0.2  Iris-setosa
# 3          4.6         3.1          1.5         0.2  Iris-setosa
# 4          5.0         3.6          1.4         0.2  Iris-setosa
print(iris.loc[iris.SepalLength > 5.1, :])
#      SepalLength  SepalWidth  PetalLength  PetalWidth            Name
# 5            5.4         3.9          1.7         0.4     Iris-setosa
# 10           5.4         3.7          1.5         0.2     Iris-setosa
# 14           5.8         4.0          1.2         0.2     Iris-setosa
# 15           5.7         4.4          1.5         0.4     Iris-setosa
# 16           5.4         3.9          1.3         0.4     Iris-setosa
# ..           ...         ...          ...         ...             ...
# 145          6.7         3.0          5.2         2.3  Iris-virginica
# 146          6.3         2.5          5.0         1.9  Iris-virginica
# 147          6.5         3.0          5.2         2.0  Iris-virginica
# 148          6.2         3.4          5.4         2.3  Iris-virginica
# 149          5.9         3.0          5.1         1.8  Iris-virginica
# 
# [109 rows x 5 columns]
#boolean - and &, or |, not ~
print(iris.loc[(iris.SepalLength > 5.1) & (iris.SepalLength <= 5.5), :])
#     SepalLength  SepalWidth  PetalLength  PetalWidth             Name
# 5           5.4         3.9          1.7         0.4      Iris-setosa
# 10          5.4         3.7          1.5         0.2      Iris-setosa
# 16          5.4         3.9          1.3         0.4      Iris-setosa
# 20          5.4         3.4          1.7         0.2      Iris-setosa
# 27          5.2         3.5          1.5         0.2      Iris-setosa
# 28          5.2         3.4          1.4         0.2      Iris-setosa
# 31          5.4         3.4          1.5         0.4      Iris-setosa
# 32          5.2         4.1          1.5         0.1      Iris-setosa
# 33          5.5         4.2          1.4         0.2      Iris-setosa
# 36          5.5         3.5          1.3         0.2      Iris-setosa
# 48          5.3         3.7          1.5         0.2      Iris-setosa
# 53          5.5         2.3          4.0         1.3  Iris-versicolor
# 59          5.2         2.7          3.9         1.4  Iris-versicolor
# 80          5.5         2.4          3.8         1.1  Iris-versicolor
# 81          5.5         2.4          3.7         1.0  Iris-versicolor
# 84          5.4         3.0          4.5         1.5  Iris-versicolor
# 89          5.5         2.5          4.0         1.3  Iris-versicolor
# 90          5.5         2.6          4.4         1.2  Iris-versicolor
print(iris.loc[(iris.SepalLength > 5.1) & (iris.SepalLength <= 5.5), :].  reset_index())
#     index  SepalLength  SepalWidth  PetalLength  PetalWidth             Name
# 0       5          5.4         3.9          1.7         0.4      Iris-setosa
# 1      10          5.4         3.7          1.5         0.2      Iris-setosa
# 2      16          5.4         3.9          1.3         0.4      Iris-setosa
# 3      20          5.4         3.4          1.7         0.2      Iris-setosa
# 4      27          5.2         3.5          1.5         0.2      Iris-setosa
# 5      28          5.2         3.4          1.4         0.2      Iris-setosa
# 6      31          5.4         3.4          1.5         0.4      Iris-setosa
# 7      32          5.2         4.1          1.5         0.1      Iris-setosa
# 8      33          5.5         4.2          1.4         0.2      Iris-setosa
# 9      36          5.5         3.5          1.3         0.2      Iris-setosa
# 10     48          5.3         3.7          1.5         0.2      Iris-setosa
# 11     53          5.5         2.3          4.0         1.3  Iris-versicolor
# 12     59          5.2         2.7          3.9         1.4  Iris-versicolor
# 13     80          5.5         2.4          3.8         1.1  Iris-versicolor
# 14     81          5.5         2.4          3.7         1.0  Iris-versicolor
# 15     84          5.4         3.0          4.5         1.5  Iris-versicolor
# 16     89          5.5         2.5          4.0         1.3  Iris-versicolor
# 17     90          5.5         2.6          4.4         1.2  Iris-versicolor
##Creation of new Columns
#works elementwise
iris['dummy'] = iris.SepalLength - 2* iris.SepalWidth + 1
print(iris.dummy)
# 0     -0.9
# 1     -0.1
# 2     -0.7
# 3     -0.6
# 4     -1.2
#       ...
# 145    1.7
# 146    2.3
# 147    1.5
# 148    0.4
# 149    0.9
# Name: dummy, Length: 150, dtype: float64
#Function - use numpy
import numpy as np
print(abs(-1))
# 1
#np takes Series/vector
iris['dummy'] = np.abs(iris.dummy)
print(iris.dummy)
# 0      0.9
# 1      0.1
# 2      0.7
# 3      0.6
# 4      1.2
#       ...
# 145    1.7
# 146    2.3
# 147    1.5
# 148    0.4
# 149    0.9
# Name: dummy, Length: 150, dtype: float64
print(len(dir(np)))
# 620
#deleteion
print(iris.columns)
# Index(['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Name',
#        'dummy'],
#       dtype='object')
print(iris.drop(columns=['dummy']))
#      SepalLength  SepalWidth  PetalLength  PetalWidth            Name
# 0            5.1         3.5          1.4         0.2     Iris-setosa
# 1            4.9         3.0          1.4         0.2     Iris-setosa
# 2            4.7         3.2          1.3         0.2     Iris-setosa
# 3            4.6         3.1          1.5         0.2     Iris-setosa
# 4            5.0         3.6          1.4         0.2     Iris-setosa
# ..           ...         ...          ...         ...             ...
# 145          6.7         3.0          5.2         2.3  Iris-virginica
# 146          6.3         2.5          5.0         1.9  Iris-virginica
# 147          6.5         3.0          5.2         2.0  Iris-virginica
# 148          6.2         3.4          5.4         2.3  Iris-virginica
# 149          5.9         3.0          5.1         1.8  Iris-virginica
# 
# [150 rows x 5 columns]
print(iris.columns)
# Index(['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Name',
#        'dummy'],
#       dtype='object')
#to make it mutable
iris.drop(columns=['dummy'], inplace=True) # original gets changed
print(iris.columns)
# Index(['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Name'], dtyp
# e='object')
#Functions
print(iris.SepalLength.mean())
# 5.843333333333334
print(iris.mean())
# SepalLength    5.843333
# SepalWidth     3.054000
# PetalLength    3.758667
# PetalWidth     1.198667
# dtype: float64
#DF - by default works with column
#by default axis=0
print(iris.mean(axis=0))
# SepalLength    5.843333
# SepalWidth     3.054000
# PetalLength    3.758667
# PetalWidth     1.198667
# dtype: float64
#axis=1 for rowwise
print(iris.mean(axis=1))
# 0      2.550
# 1      2.375
# 2      2.350
# 3      2.350
# 4      2.550
#        ...
# 145    4.300
# 146    3.925
# 147    4.175
# 148    4.325
# 149    3.950
# Length: 150, dtype: float64
#Axis has another meaning
df = iris.iloc[:, [0,1]]
print(df.columns)
# Index(['SepalLength', 'SepalWidth'], dtype='object')
df.columns = ['SL', 'SW']
print(df.head())
#     SL   SW
# 0  5.1  3.5
# 1  4.9  3.0
# 2  4.7  3.2
# 3  4.6  3.1
# 4  5.0  3.6
#concat - axis=1, columnwise stack
df3 = pd.concat([iris, df], axis=1)
print(df3.head())
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name   SL   SW
# 0          5.1         3.5          1.4         0.2  Iris-setosa  5.1  3.5
# 1          4.9         3.0          1.4         0.2  Iris-setosa  4.9  3.0
# 2          4.7         3.2          1.3         0.2  Iris-setosa  4.7  3.2
# 3          4.6         3.1          1.5         0.2  Iris-setosa  4.6  3.1
# 4          5.0         3.6          1.4         0.2  Iris-setosa  5.0  3.6
df4 = pd.concat([iris, df], axis=0)
print(len(df4))
# 300
print(df4.index)
# Int64Index([  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,
#             ...
#             140, 141, 142, 143, 144, 145, 146, 147, 148, 149],
#            dtype='int64', length=300)
df5 = df4.reset_index()
print(df5.index)
# RangeIndex(start=0, stop=300, step=1)
#Best way to understand axis meaning from doc
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sum.html
#COnvert - tolist()
# iris.tolist()
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# #   File "c:\python37\lib\site-packages\pandas\core\generic.py", line 5139, in _
# # _getattr__
# #     return object.__getattribute__(self, name)
# # AttributeError: 'DataFrame' object has no attribute 'tolist'
print(iris.values)
# array([[5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
#        [4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
#        [4.7, 3.2, 1.3, 0.2, 'Iris-setosa'],
#        [4.6, 3.1, 1.5, 0.2, 'Iris-setosa'],
#        [5.0, 3.6, 1.4, 0.2, 'Iris-setosa'],
#        [5.4, 3.9, 1.7, 0.4, 'Iris-setosa'],
#        [4.6, 3.4, 1.4, 0.3, 'Iris-setosa'],
#        [5.0, 3.4, 1.5, 0.2, 'Iris-setosa'],
#        [4.4, 2.9, 1.4, 0.2, 'Iris-setosa'],
#        [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
#        [5.4, 3.7, 1.5, 0.2, 'Iris-setosa'],
#        [4.8, 3.4, 1.6, 0.2, 'Iris-setosa'],
#        [4.8, 3.0, 1.4, 0.1, 'Iris-setosa'],
#        [4.3, 3.0, 1.1, 0.1, 'Iris-setosa'],
#        [5.8, 4.0, 1.2, 0.2, 'Iris-setosa'],
#        [5.7, 4.4, 1.5, 0.4, 'Iris-setosa'],
#        [5.4, 3.9, 1.3, 0.4, 'Iris-setosa'],
#        [5.1, 3.5, 1.4, 0.3, 'Iris-setosa'],
#        [5.7, 3.8, 1.7, 0.3, 'Iris-setosa'],
#        [5.1, 3.8, 1.5, 0.3, 'Iris-setosa'],
#        [5.4, 3.4, 1.7, 0.2, 'Iris-setosa'],
#        [5.1, 3.7, 1.5, 0.4, 'Iris-setosa'],
#        [4.6, 3.6, 1.0, 0.2, 'Iris-setosa'],
#        [5.1, 3.3, 1.7, 0.5, 'Iris-setosa'],
#        [4.8, 3.4, 1.9, 0.2, 'Iris-setosa'],
#        [5.0, 3.0, 1.6, 0.2, 'Iris-setosa'],
#        [5.0, 3.4, 1.6, 0.4, 'Iris-setosa'],
#        [5.2, 3.5, 1.5, 0.2, 'Iris-setosa'],
#        [5.2, 3.4, 1.4, 0.2, 'Iris-setosa'],
#        [4.7, 3.2, 1.6, 0.2, 'Iris-setosa'],
#        [4.8, 3.1, 1.6, 0.2, 'Iris-setosa'],
#        [5.4, 3.4, 1.5, 0.4, 'Iris-setosa'],
#        [5.2, 4.1, 1.5, 0.1, 'Iris-setosa'],
#        [5.5, 4.2, 1.4, 0.2, 'Iris-setosa'],
#        [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
#        [5.0, 3.2, 1.2, 0.2, 'Iris-setosa'],
#        [5.5, 3.5, 1.3, 0.2, 'Iris-setosa'],
#        [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'],
#        [4.4, 3.0, 1.3, 0.2, 'Iris-setosa'],
#        [5.1, 3.4, 1.5, 0.2, 'Iris-setosa'],
#        [5.0, 3.5, 1.3, 0.3, 'Iris-setosa'],
#        [4.5, 2.3, 1.3, 0.3, 'Iris-setosa'],
#        [4.4, 3.2, 1.3, 0.2, 'Iris-setosa'],
#        [5.0, 3.5, 1.6, 0.6, 'Iris-setosa'],
#        [5.1, 3.8, 1.9, 0.4, 'Iris-setosa'],
#        [4.8, 3.0, 1.4, 0.3, 'Iris-setosa'],
#        [5.1, 3.8, 1.6, 0.2, 'Iris-setosa'],
#        [4.6, 3.2, 1.4, 0.2, 'Iris-setosa'],
#        [5.3, 3.7, 1.5, 0.2, 'Iris-setosa'],
#        [5.0, 3.3, 1.4, 0.2, 'Iris-setosa'],
#        [7.0, 3.2, 4.7, 1.4, 'Iris-versicolor'],
#        [6.4, 3.2, 4.5, 1.5, 'Iris-versicolor'],
#        [6.9, 3.1, 4.9, 1.5, 'Iris-versicolor'],
#        [5.5, 2.3, 4.0, 1.3, 'Iris-versicolor'],
#        [6.5, 2.8, 4.6, 1.5, 'Iris-versicolor'],
#        [5.7, 2.8, 4.5, 1.3, 'Iris-versicolor'],
#        [6.3, 3.3, 4.7, 1.6, 'Iris-versicolor'],
#        [4.9, 2.4, 3.3, 1.0, 'Iris-versicolor'],
#        [6.6, 2.9, 4.6, 1.3, 'Iris-versicolor'],
#        [5.2, 2.7, 3.9, 1.4, 'Iris-versicolor'],
#        [5.0, 2.0, 3.5, 1.0, 'Iris-versicolor'],
#        [5.9, 3.0, 4.2, 1.5, 'Iris-versicolor'],
#        [6.0, 2.2, 4.0, 1.0, 'Iris-versicolor'],
#        [6.1, 2.9, 4.7, 1.4, 'Iris-versicolor'],
#        [5.6, 2.9, 3.6, 1.3, 'Iris-versicolor'],
#        [6.7, 3.1, 4.4, 1.4, 'Iris-versicolor'],
#        [5.6, 3.0, 4.5, 1.5, 'Iris-versicolor'],
#        [5.8, 2.7, 4.1, 1.0, 'Iris-versicolor'],
#        [6.2, 2.2, 4.5, 1.5, 'Iris-versicolor'],
#        [5.6, 2.5, 3.9, 1.1, 'Iris-versicolor'],
#        [5.9, 3.2, 4.8, 1.8, 'Iris-versicolor'],
#        [6.1, 2.8, 4.0, 1.3, 'Iris-versicolor'],
#        [6.3, 2.5, 4.9, 1.5, 'Iris-versicolor'],
#        [6.1, 2.8, 4.7, 1.2, 'Iris-versicolor'],
#        [6.4, 2.9, 4.3, 1.3, 'Iris-versicolor'],
#        [6.6, 3.0, 4.4, 1.4, 'Iris-versicolor'],
#        [6.8, 2.8, 4.8, 1.4, 'Iris-versicolor'],
#        [6.7, 3.0, 5.0, 1.7, 'Iris-versicolor'],
#        [6.0, 2.9, 4.5, 1.5, 'Iris-versicolor'],
#        [5.7, 2.6, 3.5, 1.0, 'Iris-versicolor'],
#        [5.5, 2.4, 3.8, 1.1, 'Iris-versicolor'],
#        [5.5, 2.4, 3.7, 1.0, 'Iris-versicolor'],
#        [5.8, 2.7, 3.9, 1.2, 'Iris-versicolor'],
#        [6.0, 2.7, 5.1, 1.6, 'Iris-versicolor'],
#        [5.4, 3.0, 4.5, 1.5, 'Iris-versicolor'],
#        [6.0, 3.4, 4.5, 1.6, 'Iris-versicolor'],
#        [6.7, 3.1, 4.7, 1.5, 'Iris-versicolor'],
#        [6.3, 2.3, 4.4, 1.3, 'Iris-versicolor'],
#        [5.6, 3.0, 4.1, 1.3, 'Iris-versicolor'],
#        [5.5, 2.5, 4.0, 1.3, 'Iris-versicolor'],
#        [5.5, 2.6, 4.4, 1.2, 'Iris-versicolor'],
#        [6.1, 3.0, 4.6, 1.4, 'Iris-versicolor'],
#        [5.8, 2.6, 4.0, 1.2, 'Iris-versicolor'],
#        [5.0, 2.3, 3.3, 1.0, 'Iris-versicolor'],
#        [5.6, 2.7, 4.2, 1.3, 'Iris-versicolor'],
#        [5.7, 3.0, 4.2, 1.2, 'Iris-versicolor'],
#        [5.7, 2.9, 4.2, 1.3, 'Iris-versicolor'],
#        [6.2, 2.9, 4.3, 1.3, 'Iris-versicolor'],
#        [5.1, 2.5, 3.0, 1.1, 'Iris-versicolor'],
#        [5.7, 2.8, 4.1, 1.3, 'Iris-versicolor'],
#        [6.3, 3.3, 6.0, 2.5, 'Iris-virginica'],
#        [5.8, 2.7, 5.1, 1.9, 'Iris-virginica'],
#        [7.1, 3.0, 5.9, 2.1, 'Iris-virginica'],
#        [6.3, 2.9, 5.6, 1.8, 'Iris-virginica'],
#        [6.5, 3.0, 5.8, 2.2, 'Iris-virginica'],
#        [7.6, 3.0, 6.6, 2.1, 'Iris-virginica'],
#        [4.9, 2.5, 4.5, 1.7, 'Iris-virginica'],
#        [7.3, 2.9, 6.3, 1.8, 'Iris-virginica'],
#        [6.7, 2.5, 5.8, 1.8, 'Iris-virginica'],
#        [7.2, 3.6, 6.1, 2.5, 'Iris-virginica'],
#        [6.5, 3.2, 5.1, 2.0, 'Iris-virginica'],
#        [6.4, 2.7, 5.3, 1.9, 'Iris-virginica'],
#        [6.8, 3.0, 5.5, 2.1, 'Iris-virginica'],
#        [5.7, 2.5, 5.0, 2.0, 'Iris-virginica'],
#        [5.8, 2.8, 5.1, 2.4, 'Iris-virginica'],
#        [6.4, 3.2, 5.3, 2.3, 'Iris-virginica'],
#        [6.5, 3.0, 5.5, 1.8, 'Iris-virginica'],
#        [7.7, 3.8, 6.7, 2.2, 'Iris-virginica'],
#        [7.7, 2.6, 6.9, 2.3, 'Iris-virginica'],
#        [6.0, 2.2, 5.0, 1.5, 'Iris-virginica'],
#        [6.9, 3.2, 5.7, 2.3, 'Iris-virginica'],
#        [5.6, 2.8, 4.9, 2.0, 'Iris-virginica'],
#        [7.7, 2.8, 6.7, 2.0, 'Iris-virginica'],
#        [6.3, 2.7, 4.9, 1.8, 'Iris-virginica'],
#        [6.7, 3.3, 5.7, 2.1, 'Iris-virginica'],
#        [7.2, 3.2, 6.0, 1.8, 'Iris-virginica'],
#        [6.2, 2.8, 4.8, 1.8, 'Iris-virginica'],
#        [6.1, 3.0, 4.9, 1.8, 'Iris-virginica'],
#        [6.4, 2.8, 5.6, 2.1, 'Iris-virginica'],
#        [7.2, 3.0, 5.8, 1.6, 'Iris-virginica'],
#        [7.4, 2.8, 6.1, 1.9, 'Iris-virginica'],
#        [7.9, 3.8, 6.4, 2.0, 'Iris-virginica'],
#        [6.4, 2.8, 5.6, 2.2, 'Iris-virginica'],
#        [6.3, 2.8, 5.1, 1.5, 'Iris-virginica'],
#        [6.1, 2.6, 5.6, 1.4, 'Iris-virginica'],
#        [7.7, 3.0, 6.1, 2.3, 'Iris-virginica'],
#        [6.3, 3.4, 5.6, 2.4, 'Iris-virginica'],
#        [6.4, 3.1, 5.5, 1.8, 'Iris-virginica'],
#        [6.0, 3.0, 4.8, 1.8, 'Iris-virginica'],
#        [6.9, 3.1, 5.4, 2.1, 'Iris-virginica'],
#        [6.7, 3.1, 5.6, 2.4, 'Iris-virginica'],
#        [6.9, 3.1, 5.1, 2.3, 'Iris-virginica'],
#        [5.8, 2.7, 5.1, 1.9, 'Iris-virginica'],
#        [6.8, 3.2, 5.9, 2.3, 'Iris-virginica'],
#        [6.7, 3.3, 5.7, 2.5, 'Iris-virginica'],
#        [6.7, 3.0, 5.2, 2.3, 'Iris-virginica'],
#        [6.3, 2.5, 5.0, 1.9, 'Iris-virginica'],
#        [6.5, 3.0, 5.2, 2.0, 'Iris-virginica'],
#        [6.2, 3.4, 5.4, 2.3, 'Iris-virginica'],
#        [5.9, 3.0, 5.1, 1.8, 'Iris-virginica']], dtype=object)
print(iris.values.tolist())
# [[5.1, 3.5, 1.4, 0.2, 'Iris-setosa'], [4.9, 3.0, 1.4, 0.2, 'Iris-setosa'], [4.
# 7, 3.2, 1.3, 0.2, 'Iris-setosa'], [4.6, 3.1, 1.5, 0.2, 'Iris-setosa'], [5.0, 3
# .6, 1.4, 0.2, 'Iris-setosa'], [5.4, 3.9, 1.7, 0.4, 'Iris-setosa'], [4.6, 3.4,
# 1.4, 0.3, 'Iris-setosa'], [5.0, 3.4, 1.5, 0.2, 'Iris-setosa'], [4.4, 2.9, 1.4,
#  0.2, 'Iris-setosa'], [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'], [5.4, 3.7, 1.5, 0.2
# , 'Iris-setosa'], [4.8, 3.4, 1.6, 0.2, 'Iris-setosa'], [4.8, 3.0, 1.4, 0.1, 'I
# ris-setosa'], [4.3, 3.0, 1.1, 0.1, 'Iris-setosa'], [5.8, 4.0, 1.2, 0.2, 'Iris-
# setosa'], [5.7, 4.4, 1.5, 0.4, 'Iris-setosa'], [5.4, 3.9, 1.3, 0.4, 'Iris-seto
# sa'], [5.1, 3.5, 1.4, 0.3, 'Iris-setosa'], [5.7, 3.8, 1.7, 0.3, 'Iris-setosa']
# , [5.1, 3.8, 1.5, 0.3, 'Iris-setosa'], [5.4, 3.4, 1.7, 0.2, 'Iris-setosa'], [5
# .1, 3.7, 1.5, 0.4, 'Iris-setosa'], [4.6, 3.6, 1.0, 0.2, 'Iris-setosa'], [5.1,
# 3.3, 1.7, 0.5, 'Iris-setosa'], [4.8, 3.4, 1.9, 0.2, 'Iris-setosa'], [5.0, 3.0,
#  1.6, 0.2, 'Iris-setosa'], [5.0, 3.4, 1.6, 0.4, 'Iris-setosa'], [5.2, 3.5, 1.5
# , 0.2, 'Iris-setosa'], [5.2, 3.4, 1.4, 0.2, 'Iris-setosa'], [4.7, 3.2, 1.6, 0.
# 2, 'Iris-setosa'], [4.8, 3.1, 1.6, 0.2, 'Iris-setosa'], [5.4, 3.4, 1.5, 0.4, '
# Iris-setosa'], [5.2, 4.1, 1.5, 0.1, 'Iris-setosa'], [5.5, 4.2, 1.4, 0.2, 'Iris
# -setosa'], [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'], [5.0, 3.2, 1.2, 0.2, 'Iris-set
# osa'], [5.5, 3.5, 1.3, 0.2, 'Iris-setosa'], [4.9, 3.1, 1.5, 0.1, 'Iris-setosa'
# ], [4.4, 3.0, 1.3, 0.2, 'Iris-setosa'], [5.1, 3.4, 1.5, 0.2, 'Iris-setosa'], [
# 5.0, 3.5, 1.3, 0.3, 'Iris-setosa'], [4.5, 2.3, 1.3, 0.3, 'Iris-setosa'], [4.4,
#  3.2, 1.3, 0.2, 'Iris-setosa'], [5.0, 3.5, 1.6, 0.6, 'Iris-setosa'], [5.1, 3.8
# , 1.9, 0.4, 'Iris-setosa'], [4.8, 3.0, 1.4, 0.3, 'Iris-setosa'], [5.1, 3.8, 1.
# 6, 0.2, 'Iris-setosa'], [4.6, 3.2, 1.4, 0.2, 'Iris-setosa'], [5.3, 3.7, 1.5, 0
# .2, 'Iris-setosa'], [5.0, 3.3, 1.4, 0.2, 'Iris-setosa'], [7.0, 3.2, 4.7, 1.4,
# 'Iris-versicolor'], [6.4, 3.2, 4.5, 1.5, 'Iris-versicolor'], [6.9, 3.1, 4.9, 1
# .5, 'Iris-versicolor'], [5.5, 2.3, 4.0, 1.3, 'Iris-versicolor'], [6.5, 2.8, 4.
# 6, 1.5, 'Iris-versicolor'], [5.7, 2.8, 4.5, 1.3, 'Iris-versicolor'], [6.3, 3.3
# , 4.7, 1.6, 'Iris-versicolor'], [4.9, 2.4, 3.3, 1.0, 'Iris-versicolor'], [6.6,
#  2.9, 4.6, 1.3, 'Iris-versicolor'], [5.2, 2.7, 3.9, 1.4, 'Iris-versicolor'], [
# 5.0, 2.0, 3.5, 1.0, 'Iris-versicolor'], [5.9, 3.0, 4.2, 1.5, 'Iris-versicolor'
# ], [6.0, 2.2, 4.0, 1.0, 'Iris-versicolor'], [6.1, 2.9, 4.7, 1.4, 'Iris-versico
# lor'], [5.6, 2.9, 3.6, 1.3, 'Iris-versicolor'], [6.7, 3.1, 4.4, 1.4, 'Iris-ver
# sicolor'], [5.6, 3.0, 4.5, 1.5, 'Iris-versicolor'], [5.8, 2.7, 4.1, 1.0, 'Iris
# -versicolor'], [6.2, 2.2, 4.5, 1.5, 'Iris-versicolor'], [5.6, 2.5, 3.9, 1.1, '
# Iris-versicolor'], [5.9, 3.2, 4.8, 1.8, 'Iris-versicolor'], [6.1, 2.8, 4.0, 1.
# 3, 'Iris-versicolor'], [6.3, 2.5, 4.9, 1.5, 'Iris-versicolor'], [6.1, 2.8, 4.7
# , 1.2, 'Iris-versicolor'], [6.4, 2.9, 4.3, 1.3, 'Iris-versicolor'], [6.6, 3.0,
#  4.4, 1.4, 'Iris-versicolor'], [6.8, 2.8, 4.8, 1.4, 'Iris-versicolor'], [6.7,
# 3.0, 5.0, 1.7, 'Iris-versicolor'], [6.0, 2.9, 4.5, 1.5, 'Iris-versicolor'], [5
# .7, 2.6, 3.5, 1.0, 'Iris-versicolor'], [5.5, 2.4, 3.8, 1.1, 'Iris-versicolor']
# , [5.5, 2.4, 3.7, 1.0, 'Iris-versicolor'], [5.8, 2.7, 3.9, 1.2, 'Iris-versicol
# or'], [6.0, 2.7, 5.1, 1.6, 'Iris-versicolor'], [5.4, 3.0, 4.5, 1.5, 'Iris-vers
# icolor'], [6.0, 3.4, 4.5, 1.6, 'Iris-versicolor'], [6.7, 3.1, 4.7, 1.5, 'Iris-
# versicolor'], [6.3, 2.3, 4.4, 1.3, 'Iris-versicolor'], [5.6, 3.0, 4.1, 1.3, 'I
# ris-versicolor'], [5.5, 2.5, 4.0, 1.3, 'Iris-versicolor'], [5.5, 2.6, 4.4, 1.2
# , 'Iris-versicolor'], [6.1, 3.0, 4.6, 1.4, 'Iris-versicolor'], [5.8, 2.6, 4.0,
#  1.2, 'Iris-versicolor'], [5.0, 2.3, 3.3, 1.0, 'Iris-versicolor'], [5.6, 2.7,
# 4.2, 1.3, 'Iris-versicolor'], [5.7, 3.0, 4.2, 1.2, 'Iris-versicolor'], [5.7, 2
# .9, 4.2, 1.3, 'Iris-versicolor'], [6.2, 2.9, 4.3, 1.3, 'Iris-versicolor'], [5.
# 1, 2.5, 3.0, 1.1, 'Iris-versicolor'], [5.7, 2.8, 4.1, 1.3, 'Iris-versicolor'],
#  [6.3, 3.3, 6.0, 2.5, 'Iris-virginica'], [5.8, 2.7, 5.1, 1.9, 'Iris-virginica'
# ], [7.1, 3.0, 5.9, 2.1, 'Iris-virginica'], [6.3, 2.9, 5.6, 1.8, 'Iris-virginic
# a'], [6.5, 3.0, 5.8, 2.2, 'Iris-virginica'], [7.6, 3.0, 6.6, 2.1, 'Iris-virgin
# ica'], [4.9, 2.5, 4.5, 1.7, 'Iris-virginica'], [7.3, 2.9, 6.3, 1.8, 'Iris-virg
# inica'], [6.7, 2.5, 5.8, 1.8, 'Iris-virginica'], [7.2, 3.6, 6.1, 2.5, 'Iris-vi
# rginica'], [6.5, 3.2, 5.1, 2.0, 'Iris-virginica'], [6.4, 2.7, 5.3, 1.9, 'Iris-
# virginica'], [6.8, 3.0, 5.5, 2.1, 'Iris-virginica'], [5.7, 2.5, 5.0, 2.0, 'Iri
# s-virginica'], [5.8, 2.8, 5.1, 2.4, 'Iris-virginica'], [6.4, 3.2, 5.3, 2.3, 'I
# ris-virginica'], [6.5, 3.0, 5.5, 1.8, 'Iris-virginica'], [7.7, 3.8, 6.7, 2.2,
# 'Iris-virginica'], [7.7, 2.6, 6.9, 2.3, 'Iris-virginica'], [6.0, 2.2, 5.0, 1.5
# , 'Iris-virginica'], [6.9, 3.2, 5.7, 2.3, 'Iris-virginica'], [5.6, 2.8, 4.9, 2
# .0, 'Iris-virginica'], [7.7, 2.8, 6.7, 2.0, 'Iris-virginica'], [6.3, 2.7, 4.9,
#  1.8, 'Iris-virginica'], [6.7, 3.3, 5.7, 2.1, 'Iris-virginica'], [7.2, 3.2, 6.
# 0, 1.8, 'Iris-virginica'], [6.2, 2.8, 4.8, 1.8, 'Iris-virginica'], [6.1, 3.0,
# 4.9, 1.8, 'Iris-virginica'], [6.4, 2.8, 5.6, 2.1, 'Iris-virginica'], [7.2, 3.0
# , 5.8, 1.6, 'Iris-virginica'], [7.4, 2.8, 6.1, 1.9, 'Iris-virginica'], [7.9, 3
# .8, 6.4, 2.0, 'Iris-virginica'], [6.4, 2.8, 5.6, 2.2, 'Iris-virginica'], [6.3,
#  2.8, 5.1, 1.5, 'Iris-virginica'], [6.1, 2.6, 5.6, 1.4, 'Iris-virginica'], [7.
# 7, 3.0, 6.1, 2.3, 'Iris-virginica'], [6.3, 3.4, 5.6, 2.4, 'Iris-virginica'], [
# 6.4, 3.1, 5.5, 1.8, 'Iris-virginica'], [6.0, 3.0, 4.8, 1.8, 'Iris-virginica'],
#  [6.9, 3.1, 5.4, 2.1, 'Iris-virginica'], [6.7, 3.1, 5.6, 2.4, 'Iris-virginica'
# ], [6.9, 3.1, 5.1, 2.3, 'Iris-virginica'], [5.8, 2.7, 5.1, 1.9, 'Iris-virginic
# a'], [6.8, 3.2, 5.9, 2.3, 'Iris-virginica'], [6.7, 3.3, 5.7, 2.5, 'Iris-virgin
# ica'], [6.7, 3.0, 5.2, 2.3, 'Iris-virginica'], [6.3, 2.5, 5.0, 1.9, 'Iris-virg
# inica'], [6.5, 3.0, 5.2, 2.0, 'Iris-virginica'], [6.2, 3.4, 5.4, 2.3, 'Iris-vi
# rginica'], [5.9, 3.0, 5.1, 1.8, 'Iris-virginica']]
#at to get cell value
#check material - https://pandas.pydata.org/docs/reference/api/pandas.Data
# Frame.at.html
# >>>
# >>>
print(iris.head())
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name
# 0          5.1         3.5          1.4         0.2  Iris-setosa
# 1          4.9         3.0          1.4         0.2  Iris-setosa
# 2          4.7         3.2          1.3         0.2  Iris-setosa
# 3          4.6         3.1          1.5         0.2  Iris-setosa
# 4          5.0         3.6          1.4         0.2  Iris-setosa
print(iris.iloc[1, :])
# SepalLength            4.9
# SepalWidth               3
# PetalLength            1.4
# PetalWidth             0.2
# Name           Iris-setosa
# Name: 1, dtype: object
print(iris.iloc[[0,1], :])
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name
# 0          5.1         3.5          1.4         0.2  Iris-setosa
# 1          4.9         3.0          1.4         0.2  Iris-setosa
print(iris.iloc[0:10, :])
#    SepalLength  SepalWidth  PetalLength  PetalWidth         Name
# 0          5.1         3.5          1.4         0.2  Iris-setosa
# 1          4.9         3.0          1.4         0.2  Iris-setosa
# 2          4.7         3.2          1.3         0.2  Iris-setosa
# 3          4.6         3.1          1.5         0.2  Iris-setosa
# 4          5.0         3.6          1.4         0.2  Iris-setosa
# 5          5.4         3.9          1.7         0.4  Iris-setosa
# 6          4.6         3.4          1.4         0.3  Iris-setosa
# 7          5.0         3.4          1.5         0.2  Iris-setosa
# 8          4.4         2.9          1.4         0.2  Iris-setosa
# 9          4.9         3.1          1.5         0.1  Iris-setosa
#Special attribute and methods in Series
print(iris.Name)
# 0         Iris-setosa
# 1         Iris-setosa
# 2         Iris-setosa
# 3         Iris-setosa
# 4         Iris-setosa
#             ...
# 145    Iris-virginica
# 146    Iris-virginica
# 147    Iris-virginica
# 148    Iris-virginica
# 149    Iris-virginica
# Name: Name, Length: 150, dtype: object
print(dir(iris.Name.str) ) # .str only for str column
# ['__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc_
# _', '__eq__', '__format__', '__frozen', '__ge__', '__getattribute__', '__getit
# em__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__l
# e__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex_
# _', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '_
# _weakref__', '_doc_args', '_freeze', '_get_series_list', '_inferred_dtype', '_
# is_categorical', '_is_string', '_make_accessor', '_orig', '_parent', '_validat
# e', '_wrap_result', 'capitalize', 'casefold', 'cat', 'center', 'contains', 'co
# unt', 'decode', 'encode', 'endswith', 'extract', 'extractall', 'find', 'findal
# l', 'fullmatch', 'get', 'get_dummies', 'index', 'isalnum', 'isalpha', 'isdecim
# al', 'isdigit', 'islower', 'isnumeric', 'isspace', 'istitle', 'isupper', 'join
# ', 'len', 'ljust', 'lower', 'lstrip', 'match', 'normalize', 'pad', 'partition'
# , 'repeat', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rs
# trip', 'slice', 'slice_replace', 'split', 'startswith', 'strip', 'swapcase', '
# title', 'translate', 'upper', 'wrap', 'zfill']
print(iris.Name.str)
# <pandas.core.strings.StringMethods object at 0x000000806D008E48>
print(iris.Name.str.lower())
# 0         iris-setosa
# 1         iris-setosa
# 2         iris-setosa
# 3         iris-setosa
# 4         iris-setosa
#             ...
# 145    iris-virginica
# 146    iris-virginica
# 147    iris-virginica
# 148    iris-virginica
# 149    iris-virginica
# Name: Name, Length: 150, dtype: object
print(iris.Name.str.upper())
# 0         IRIS-SETOSA
# 1         IRIS-SETOSA
# 2         IRIS-SETOSA
# 3         IRIS-SETOSA
# 4         IRIS-SETOSA
#             ...
# 145    IRIS-VIRGINICA
# 146    IRIS-VIRGINICA
# 147    IRIS-VIRGINICA
# 148    IRIS-VIRGINICA
# 149    IRIS-VIRGINICA
# Name: Name, Length: 150, dtype: object
print(iris.Name.str.split("-"))
# 0         [Iris, setosa]
# 1         [Iris, setosa]
# 2         [Iris, setosa]
# 3         [Iris, setosa]
# 4         [Iris, setosa]
#              ...
# 145    [Iris, virginica]
# 146    [Iris, virginica]
# 147    [Iris, virginica]
# 148    [Iris, virginica]
# 149    [Iris, virginica]
# Name: Name, Length: 150, dtype: object
print(iris.Name.str.split("-", expand=True))
#         0          1
# 0    Iris     setosa
# 1    Iris     setosa
# 2    Iris     setosa
# 3    Iris     setosa
# 4    Iris     setosa
# ..    ...        ...
# 145  Iris  virginica
# 146  Iris  virginica
# 147  Iris  virginica
# 148  Iris  virginica
# 149  Iris  virginica
# 
# [150 rows x 2 columns]
df6 = iris.Name.str.split("-", expand=True)
df6.columns = ['part1', 'part2']
print(df6)
#     part1      part2
# 0    Iris     setosa
# 1    Iris     setosa
# 2    Iris     setosa
# 3    Iris     setosa
# 4    Iris     setosa
# ..    ...        ...
# 145  Iris  virginica
# 146  Iris  virginica
# 147  Iris  virginica
# 148  Iris  virginica
# 149  Iris  virginica
# 
# [150 rows x 2 columns]
#Special attribute - datetime series, .dt, eg .dt.year,...
#check offline
#Series has also additionla methods
print(iris.Name.unique())
# array(['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'], dtype=object)
print(iris.Name.value_counts())
# Iris-setosa        50
# Iris-versicolor    50
# Iris-virginica     50
# Name: Name, dtype: int64
#DF has few addl methods
print(iris.describe())
#        SepalLength  SepalWidth  PetalLength  PetalWidth
# count   150.000000  150.000000   150.000000  150.000000
# mean      5.843333    3.054000     3.758667    1.198667
# std       0.828066    0.433594     1.764420    0.763161
# min       4.300000    2.000000     1.000000    0.100000
# 25%       5.100000    2.800000     1.600000    0.300000
# 50%       5.800000    3.000000     4.350000    1.300000
# 75%       6.400000    3.300000     5.100000    1.800000
# max       7.900000    4.400000     6.900000    2.500000
#Aggregation
gr = iris.groupby('Name')
print(gr.mean())
#                  SepalLength  SepalWidth  PetalLength  PetalWidth
# Name
# Iris-setosa            5.006       3.418        1.464       0.244
# Iris-versicolor        5.936       2.770        4.260       1.326
# Iris-virginica         6.588       2.974        5.552       2.026
print(gr.agg({'SepalLength' : ['min', 'count', 'max']}))
#                 SepalLength
#                         min count  max
# Name
# Iris-setosa             4.3    50  5.8
# Iris-versicolor         4.9    50  7.0
# Iris-virginica          4.9    50  7.9
gr.agg({'SepalLength' : ['min', 'count', 'max']}).to_excel('processed.xlsx')
import glob
print(glob.glob('*.xl*'))
# ['processed.xlsx']
#Plotting
# import matplotlob.pyplot as plt
# # Traceback (most recent call last):
# #   File "<stdin>", line 1, in <module>
# # ModuleNotFoundError: No module named 'matplotlob'
import matplotlib.pyplot as plt
print(iris.iloc[:, 0:4].plot(kind='line'))
# <AxesSubplot:>
plt.savefig('plot.png')
#https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.htm
# l
print(glob.glob('*.png'))
# ['plot.png']
##DB
#Many kind of DBs - mysql, oracle,...
#Each DB - many modules , each module might have it's own complexity
#DBAPI - DB API2 and ORM
#ORM - creates class from table- hibernet
#DBAPI2 - sql query
from sqlalchemy import create_engine
eng = create_engine('sqlite:///foo.db', echo=False)
#insert
iris.to_sql('iris', con=eng, if_exists='replace')
#DB API - .execute(sql_query)
# >>> eng.execute("select max(SepalLength) from iris group by Name)....
#   File "<stdin>", line 2
# 
#     ^
# SyntaxError: EOL while scanning string literal
print(eng.execute("select max(SepalLength) from iris group by Name").   fetchall())
# [(5.8,), (7.0,), (7.9,)]
# >>>
#DF from DB table
df = pd.read_sql('iris', con=eng)
print(df.columns)
# Index(['index', 'SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth',
#        'Name'],
#       dtype='object')
# >>> quit()
