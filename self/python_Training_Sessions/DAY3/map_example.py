lst = [1,2,3,4]

#Understand datatype of each element of input 
#Understand what collection type is required as output 

#map pattern - Transforming input to output collection 
#Square each element 

#Output data type - List - duplicates, ...
o = [ e*e for e in lst] 
print(o)
#Square even element - condition - guard 
o = [ e*e for e in lst if e%2 == 0] 
print(o)
#Create even, odd pairs 
o = [ (e1,e2) for e1 in lst if e1%2 == 0 for e2 in lst if e2%2 == 1] 
print(o)
#equiv 
o = []
for e1 in lst:
    if e1%2 == 0:
        for e2 in lst:
            if e2%2 == 1:
                o.append( (e1,e2) )
                
#Output data type - set - unique, ...
o = { e*e for e in lst }
print(o)
#Output data type - dict - k,v pairs ...
o = { e: e*e for e in lst }
print(o)