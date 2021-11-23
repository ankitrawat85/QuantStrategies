import timeit
addition = """x = 5 + 7"""
multiplication = """x = 5 * 7"""
division = """x = 5 / 7"""
log = """import math\nx = math.log(7)"""
sqrt = """import math\nx = math.sqrt(7)"""
exp = """import math\nx = math.exp(7)"""
repeat = 10000000
elapsed_time = timeit.timeit(addition, number=repeat)
print("add: \t", elapsed_time / repeat)
elapsed_time = timeit.timeit(multiplication, number=repeat)
print("mul: \t", elapsed_time / repeat)
elapsed_time = timeit.timeit(division, number=repeat)
print("div: \t", elapsed_time / repeat)
elapsed_time = timeit.timeit(log, number=repeat)
print("log: \t", elapsed_time / repeat)
elapsed_time = timeit.timeit(sqrt, number=repeat)
print("sqrt: \t", elapsed_time / repeat)
elapsed_time = timeit.timeit(exp, number=repeat)
print("exp: \t", elapsed_time / repeat)


import timeit
m1 = """import math
S = 100\nK = 105\nvol = 0.1\nt=2\nmu=0.01
d1 = (math.log(S * math.exp(mu*t) / K) + vol * vol * t / 2) / vol / math.sqrt(t)
"""
m2 = """
import math
S = 100\nK = 105\nvol = 0.1\nt=2\nmu=0.01
stdev = vol * math.sqrt(t)
d1 = (math.log(S / K) + mu*t) / stdev + stdev / 2
"""
repeat = 5000000
elapsed_time = timeit.timeit(m1, number=repeat)
print("m1: \t", elapsed_time / repeat)
elapsed_time = timeit.timeit(m2, number=repeat)
print("m2: \t", elapsed_time / repeat)


def toFixedPoint(x : float, w : int, b : int) -> [int]:
    # set a[w-1] to 1 if x < 0, otherwise set a[w-1] to 0
    a = [0 for i in range(w)]
    if x < 0:
        a[0] = 1
        x += 2**(w-1-b)
    for i in range(1, w):
        y = x / (2**(w-1-i-b))
        a[i] = int(y)  # round y down to integer
        x -= a[i] * (2**(w-1-i-b))
    return a

print(toFixedPoint(-10, 8, 1))
print(toFixedPoint(-9.5, 8, 1))
print(toFixedPoint(9.25, 8, 2))


print(toFixedPoint(20, 8, 3))
print(toFixedPoint(20, 9, 3))


def toFixedPoint2(x : float, w : int, b : int) -> [int]:
    # set a[w-1] to 1 if x < 0, otherwise set a[w-1] to 0
    a = [0 for i in range(w)]
    if x < 0:
        a[0] = 1
        x += 2**(w-1-b)
    for i in range(1, w):
        y = x / (2**(w-1-i-b))
        a[i] = int(y)%2  # round y down to integer
        x -= a[i] * (2**(w-1-i-b))
    return a

print(toFixedPoint2(20, 8, 3))
print(toFixedPoint2(20, 9, 3))





import numpy as np
for f in (np.float32, np.float64, float):
    finfo = np.finfo(f)
    print(finfo.dtype, "\t exponent bits = ", finfo.nexp, "\t significand bits = ", finfo.nmant)

x = 10776321
nsteps = 1235
s = x / nsteps
y = 0
for i in range(nsteps):
    y += s
print(x - y)

x = 10.56
print(x == x + 5e-16)



x = 0.1234567891234567890
y = 0.1234567891
scale = 1e16
z1 = (x-y) * scale
print("z1 = ", z1)

z2 = (x*scale - y*scale)
print("z2 = ", z2)