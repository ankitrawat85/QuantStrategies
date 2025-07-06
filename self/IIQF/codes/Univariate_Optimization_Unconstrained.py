# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 23:05:34 2023

@author: Abhijit Biswas
"""
import math as mt
from scipy import optimize

########################################################################################################
# UNCONSTRAINED OPTIMIZATION OF A UNIVARIATE FUNCTION
########################################################################################################

########################################################################################################
# EXAMPLE 1 : UNIMODAL FUNCTION
########################################################################################################


########################################################################################################
#
# minimize the function F(x) = x^2
#
# Note : this is an unimodal function and has only 1 minimum, hence all methods are able to find it, regardless of initial value
########################################################################################################

def f(x):
    return x**2

# using various minimization methods and vaious initial values
# Note : if no method is menioned, automatically chhoses the default method based on the type of objective function

# default method
x = 1
res = optimize.minimize(f, x)  
print(res.x)

x = 10
res = optimize.minimize(f, x)
print(res.x)

x = -100
res = optimize.minimize(f, x)
print(res.x)


##################
# brent
##################
##################
# NOTE: 1) ONLY APPLICABLE FOR UNIVARIATE functions
#       2) Supports bounds (OPTIONAL) but not constraints
#       3) does not take any inotial value
##################

minimizer_method = "brent"

res = optimize.minimize_scalar(f, method = minimizer_method)
print(res.x)


##################
# bounded
##################
##################
# NOTE: 1) ONLY APPLICABLE FOR UNIVARIATE functions WITH BOUNDS (MANDATORY)
#       2) Supports bounds but not constraints
#       3) does not take any inotial value
##################

minimizer_method = "bounded"

res = optimize.minimize_scalar(f, method = minimizer_method)
print(res.x)


##################
# golden
##################
##################
# NOTE: 1) ONLY APPLICABLE FOR UNIVARIATE functions
#       2) Supports bounds (OPTIONAL) but not constraints
#       3) does not take any inotial value
##################

minimizer_method = "golden"

res = optimize.minimize_scalar(f, method = minimizer_method)
print(res.x)



##################
# Nelder-Mead
# does not support constraints
##################

minimizer_method = "Nelder-Mead"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)


##################
# Powell
##################

minimizer_method = "Powell"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# CG
##################

minimizer_method = "CG"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# BFGS
##################

minimizer_method = "BFGS"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# Newton-CG
# requires the JACOBIAN
##################

minimizer_method = "Newton-CG"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# L-BFGS-B
##################

minimizer_method = "L-BFGS-B"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# TNC
# NOTE : Gives most accurate solution for most initial values
##################

minimizer_method = "TNC"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# COBYLA
##################

minimizer_method = "COBYLA"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# SLSQP
# NOTE : Gives the MOST ACCURATE solution, irrespective of the initial value, (in a unimodal case)
##################

minimizer_method = "SLSQP"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-constr
##################

minimizer_method = "trust-constr"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# dogleg
# requires the JACOBIAN
##################

minimizer_method = "dogleg"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-ncg
# requires the JACOBIAN
##################

minimizer_method = "trust-ncg"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-krylov
# requires the JACOBIAN
##################

minimizer_method = "trust-krylov"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-exact
# requires the JACOBIAN
##################

minimizer_method = "trust-exact"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)





########################################################################################################
# EXAMPLE 2 : MULTI-MODAL FUNCTION
########################################################################################################


########################################################################################################
#
# minimize the function F(x) = sin(x) / x
#
# Note : this is an multimodal function and has infinitely many minima and only 1 global minimum
########################################################################################################


def f(x):
    return (mt.sin(x) / x)



###################
# Using various minimization methods and vaious initial values
# Note : if no method is menioned, automatically chhoses the default method based on the type of objective function
#
# Note : All the following methods reach the LOCAL MINIMA, but fail to reach the global minimum unless the initial value is carefully chosen
# hence the result becomes initial value dependent
###################


# default method
x = 1
res = optimize.minimize(f, x)  
print(res.x)

x = 10
res = optimize.minimize(f, x)
print(res.x)

x = -100
res = optimize.minimize(f, x)
print(res.x)

##################
# Nelder-Mead
##################

minimizer_method = "Nelder-Mead"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)


##################
# Powell
##################

minimizer_method = "Powell"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# CG
##################

minimizer_method = "CG"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# BFGS
##################

minimizer_method = "BFGS"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# Newton-CG
# requires the JACOBIAN
##################

minimizer_method = "Newton-CG"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# L-BFGS-B
##################

minimizer_method = "L-BFGS-B"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# TNC
##################

minimizer_method = "TNC"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# COBYLA
##################

minimizer_method = "COBYLA"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# SLSQP
# NOTE : This method worked so well for the unimodal case but fails miserably in a multi-modal situation
##################

minimizer_method = "SLSQP"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-constr
##################

minimizer_method = "trust-constr"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# dogleg
# requires the JACOBIAN
##################

minimizer_method = "dogleg"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-ncg
# requires the JACOBIAN
##################

minimizer_method = "trust-ncg"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-krylov
# requires the JACOBIAN
##################

minimizer_method = "trust-krylov"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

##################
# trust-exact
# requires the JACOBIAN
##################

minimizer_method = "trust-exact"

x = 1
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = 10
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)

x = -100
res = optimize.minimize(f, x, method = minimizer_method)
print(res.x)







######################################################################
# Global Minimization
# Note : All the following methods try reach the GLOBAL MINIMA, with varying degree of success, depending on the number of iterations and initial values
######################################################################

# Note: some of the global minimization methods use local minimization methods iteratively
#  

##################
# METHOD 1 : basinhopping
##################

# Note : using various local minimization methods and vaious initial values
# whatever minimizer you use, 200 iterations is too small to reach the global minimum, the result becomes initial value dependent
# 
# Further note: Since basinhopping internally calls the optimize.minimize function hence even for univariate functions we cannot use 
# brent, bounded or golden methods, which are called using optimize.minimize_scalar function

##################
# Nelder-Mead
##################

minimizer_method = {"method": "Nelder-Mead"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# Powell
##################

minimizer_method = {"method": "Powell"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)


##################
# CG
##################

minimizer_method = {"method": "CG"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# BFGS
##################

minimizer_method = {"method": "BFGS"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# L-BFGS-B
##################

minimizer_method = {"method": "L-BFGS-B"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# TNC
##################

minimizer_method = {"method": "TNC"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# COBYLA
##################

minimizer_method = {"method": "COBYLA"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# SLSQP
##################

minimizer_method = {"method": "SLSQP"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

##################
# trust-constr
##################

minimizer_method = {"method": "trust-constr"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=200)
print(res.x)



#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#
# Using 2000 iterations
# 
# Note : using enough iterations the global minimum is reached by most local methods, regardless of initial value

##################
# Nelder-Mead
# fails sometimes
##################

minimizer_method = {"method": "Nelder-Mead"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# Powell
# fails sometimes
##################

minimizer_method = {"method": "Powell"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)


##################
# CG
# fails sometimes
##################

minimizer_method = {"method": "CG"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# BFGS
# fails sometimes
##################

minimizer_method = {"method": "BFGS"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# L-BFGS-B
# fails sometimes
##################

minimizer_method = {"method": "L-BFGS-B"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# TNC
# fails sometimes
##################

minimizer_method = {"method": "TNC"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# COBYLA
# FAILS MOSTLY
##################

minimizer_method = {"method": "COBYLA"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

##################
# SLSQP
# fails sometimes
##################

minimizer_method = {"method": "SLSQP"}

x = 1
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
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

x = 10
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)

x = -100
res = optimize.basinhopping(f, x, minimizer_kwargs = minimizer_method, niter=2000)
print(res.x)




