# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 23:05:34 2023

@author: Abhijit Biswas
"""
import math as mt
from scipy import optimize

########################################################################################################
# CONSTRAINED OPTIMIZATION OF A MULTI-VARIATE FUNCTION
########################################################################################################
# all the parameters of the objective function are optimisable
################################################################################


########################################################################################################
#
# minimize the function F(x) = 2x1 + x2^2 + sin(x3) + x4^3 + x5
#
# Note : this is an multimodal function and has infinitely many minima and only 1 global minimum
########################################################################################################

def f(x):
    return (2 * x[0] + x[1]**2 + mt.sin(x[2]) + x[3]**3 + x[4] )


# adding some constraints

def constraint1(x):
    # x1 => 0
    return (x[0])

def constraint2(x):
    # x1 <= 20 i.e. 20 - x1 => 0
    return (20 - x[0])

def constraint3(x):
    # x2 >= x1 i.e. x2 - x1 => 0
    return (x[1] - x[0])

def constraint4(x):
    # x2 <= x1 + 10 i.e. x1 + 10 - x2 => 0
    return (x[0] + 10 - x[1])

def constraint5(x):
    # x1 + x2 + x3 <= 100 i.e. 100 - x1 - x2 - x3 => 0
    return (100 - x[0] - x[1] - x[2])

def constraint6(x):
    # x1 * x2 => 30
    return (x[0] * x[1] - 30)


dcons1 = {'type' : 'ineq', 'fun' : constraint1}
dcons2 = {'type' : 'ineq', 'fun' : constraint2}
dcons3 = {'type' : 'ineq', 'fun' : constraint3}
dcons4 = {'type' : 'ineq', 'fun' : constraint4}
dcons5 = {'type' : 'ineq', 'fun' : constraint5}
dcons6 = {'type' : 'ineq', 'fun' : constraint6}

constraints_list = [dcons1, dcons2, dcons3, dcons4, dcons5, dcons6]


###################
# Using various minimization methods and vaious initial values
# Note : if no method is menioned, automatically chhoses the default method based on the type of objective function
#
# Note : All the following methods reach the LOCAL MINIMA, but fail to reach the global minimum unless the initial value is carefully chosen
# hence the result becomes initial value dependent
###################


# default method
x = [1, 1, 1, 1, 1]
res = optimize.minimize(f, x, constraints = constraints_list)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.minimize(f, x, constraints = constraints_list)
print(res.x)


##################
# does not support constraints
#
# Nelder-Mead, Powell, L-BFGS-B, TNC

# does not support constraints or bounds
#
# CG, BFGS
##################



##################
# COBYLA
##################

minimizer_method = "COBYLA"

x = [1, 1, 1, 1, 1]
res = optimize.minimize(f, x, method = minimizer_method, constraints = constraints_list)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.minimize(f, x, method = minimizer_method, constraints = constraints_list)
print(res.x)

##################
# SLSQP
##################

minimizer_method = "SLSQP"

x = [1, 1, 1, 1, 1]
res = optimize.minimize(f, x, method = minimizer_method, constraints = constraints_list)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.minimize(f, x, method = minimizer_method, constraints = constraints_list)
print(res.x)

##################
# trust-constr
# slow
##################

minimizer_method = "trust-constr"

x = [1, 1, 1, 1, 1]
res = optimize.minimize(f, x, method = minimizer_method, constraints = constraints_list)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.minimize(f, x, method = minimizer_method, constraints = constraints_list)
print(res.x)



######################################################################
# Global Minimization
# Note : All the following methods try reach the GLOBAL MINIMA, with varying degree of success, depending on the number of iterations and initial values
######################################################################

# Note: some of the global minimization methods use local minimization methods iteratively
#  

##################
#
# METHOD 1 : basinhopping
#
# basinhopping(func, x0, niter=100, T=1.0, stepsize=0.5, minimizer_kwargs=None, take_step=None, accept_test=None, callback=None, interval=50, disp=False, niter_success=None, seed=None, *, target_accept_rate=0.5, stepwise_factor=0.9)
#
##################

# Note : using various local minimization methods and vaious initial values
# whatever minimizer you use, 200 iterations is too small to reach the global minimum, the result becomes initial value dependent
# 
# Further note: Since basinhopping internally calls the optimize.minimize function hence even for univariate functions we cannot use 
# brent, bounded or golden methods, which are called using optimize.minimize_scalar function


##################
# COBYLA
##################

minimizer_method = {"method": "COBYLA"}

x = [1, 1, 1, 1, 1]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# SLSQP
##################

minimizer_method = {"method": "SLSQP"}

x = [1, 1, 1, 1, 1]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# trust-constr
# slow
##################

minimizer_method = {"method": "trust-constr"}

x = [1, 1, 1, 1, 1]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)



#########################################
#
# Using 2000 iterations
# 
# Note : using enough iterations the global minimum is reached by most local methods, regardless of initial value


##################
# COBYLA
##################

minimizer_method = {"method": "COBYLA"}

x = [1, 1, 1, 1, 1]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# SLSQP
##################

minimizer_method = {"method": "SLSQP"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# trust-constr
# extremely slow, fails sometimes
##################

minimizer_method = {"method": "trust-constr"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = [4, 3, 2, -5, -10]
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)




##################
#
# METHOD 2 : differential_evolution
# VERY IMPORTANT : THIS METHOD CAN HANDLE MIXED INTEGER PROGRAMMING PROBLEMS (MIP)
#
# optimize.differential_evolution(func, bounds, args=(), strategy='best1bin', maxiter=1000, popsize=15, tol=0.01, mutation=(0.5, 1), recombination=0.7, seed=None, callback=None, disp=False, polish=True, init='latinhypercube', atol=0, updating='immediate', workers=1, constraints=(), x0=None, *, integrality=None, vectorized=False)

# bounds (MANDATORY) : Bounds for variables
# There are two ways to specify the bounds: (1) Instance of Bounds class. (2) (min, max) pairs for each element in x, defining the finite lower and upper bounds for the optimizing argument
# you need to have some idea about the possible value range of each variable

# strategy : The differential evolution strategy to use. Should be one of:
# best1bin, best1exp, rand1exp, randtobest1exp, currenttobest1exp, best2exp, rand2exp, randtobest1bin, currenttobest1bin, best2bin, rand2bin, rand1bin
# default is best1bin

# maxiter : The maximum number of generations over which the entire population is evolved.
# default is 1000

# popsize : A multiplier for setting the total population size. The population has popsize * N individuals
# This keyword is overridden if an initial population is supplied via the init keyword. When using init='sobol' the population size is calculated as the next power of 2 after popsize * N

# init : Specify which type of population initialization is performed. Should be one of:
# latinhypercube, sobol, halton, random
# best to use sobol, halton

# updating : immediate / deferred
# If 'immediate', the best solution vector is continuously updated within a single generation. This can lead to faster convergence as trial vectors can take advantage of continuous improvements in the best solution. 
# With 'deferred', the best solution vector is updated once per generation

# workers : population is subdivided into n sections and evaluated in parallel (use -1 to use all available CPU cores)
# if workers != 1 then updating is overridden to 'deferred'

# integrality : 1-D array
# For each decision variable, a boolean value indicating whether the decision variable is constrained to integer values
##################

# Note : using vaious initial values
# whatever minimizer you use, 200 iterations is too small to reach the global minimum, the result becomes initial value dependent
# 
# Further note: Since differential_evolution internally calls the optimize.minimize function hence even for univariate functions we cannot use 
# brent, bounded or golden methods, which are called using optimize.minimize_scalar function


# you need to have some idea about the possible value range of each variable
bounds = [(-2000,2000), (-2000,2000), (-2000,2000), (-2000,2000), (-2000,2000)]

# the default init method does not reach global minimum always, because the sample space is not uniformly scanned
res = optimize.differential_evolution(f, bounds)
print(res.x)

# reach global minimum almost always
res = optimize.differential_evolution(f, bounds, init = 'sobol')
print(res.x)

# reach global minimum almost always
res = optimize.differential_evolution(f, bounds, init = 'halton')
print(res.x)

# you need to have some idea about the possible value range of each variable
bounds = [(-60,60), (-60,60), (-60,60), (-60,60), (-60,60)]
res = optimize.differential_evolution(f, bounds, init = 'halton')
print(res.x)

# increasing workers to parallelize may sometimes may have the opposite effect of slowing it down instead of speeding up
# because the updating is then set to deferred which can have a very bad effect
# don't run this - it will hang
res = optimize.differential_evolution(f, bounds, init = 'halton', workers = 3)
print(res.x)
















