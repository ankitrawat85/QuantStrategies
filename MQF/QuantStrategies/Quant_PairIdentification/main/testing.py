import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from statsmodels.nonparametric.kernel_regression import KernelReg as kr
import plotly.graph_objs as go
import pandas as pd

np.random.seed(1)
# xwidth controls the range of x values.
xwidth = 20
x = np.arange(0,xwidth,1)
# we want to add some noise to the x values so that dont sit at regular intervals
#print(x)
x_residuals = np.random.normal(scale=0.2, size=[x.shape[0]])
# new_x is the range of x values we will be using all the way through
#print(x_residuals)
new_x = x + x_residuals
# We generate residuals for y values since we want to show some variation in the data
num_points = x.shape[0]
residuals = np.random.normal(scale=2.0, size=[num_points])
#print(residuals)
# We will be using fun_y to generate y values all the way through
fun_y = lambda x: -(x*x) + residuals
#print (fun_y(new_x))
# Plot the x and y values
plt.scatter(x=new_x,y=fun_y(new_x))
plt.scatter(x=new_x,y=fun_y(new_x))
#fig.add_trace(go.Scatter(x=new_x, y=pred_y, name='Statsmodels fit',  mode='lines'))


kernel_x = np.arange(-xwidth,xwidth, 0.1)
bw_manual = 1
def gauss_const(h):
    """
    Returns the normalization constant for a gaussian
    """
    return 1/(h*np.sqrt(np.pi*2))
def gauss_exp(ker_x, xi, h):
    """
    Returns the gaussian function exponent term
    """
    print ("kernal constant ")
    #print (ker_x)
    num =  - 0.5*np.square((xi- ker_x))
    den = h*h
    return num/den
def kernel_function(h, ker_x, xi):
    """
    Returns the gaussian function value. Combines the gauss_const and
    gauss_exp to get this result
    """
    const = gauss_const(h)
    gauss_val = const*np.exp(gauss_exp(ker_x,xi,h))
    return gauss_val
# We are selecting a single point and calculating the Kernel value
input_x = new_x[0]
col1 = gauss_const(bw_manual)
col2= gauss_exp(kernel_x, input_x, bw_manual)
col3 = kernel_function(bw_manual, kernel_x, input_x)
#print(kernel_x)
# Dataframe for a single observation point x_i. In the code x_i comes from new_x

data = {'Input_x': [input_x for x in range(col2.shape[0])],
        'kernel_x': kernel_x,
        'gaussian_const': [col1 for x in range(col2.shape[0])],
        'gaussian_exp': col2,
        'full_gaussian_value': col3,
        'bw':[bw_manual for x in range(col2.shape[0])],
        }
single_pt_KE = pd.DataFrame(data=data)
single_pt_KE.plot()
print(single_pt_KE)
