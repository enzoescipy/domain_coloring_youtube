import numpy as np
import sympy as sp
x = sp.symbols("x")
my_sigmoid = (1 / (1 + (np.e)**(-5*(x-0.5))))
print(float(my_sigmoid.subs(x,1.0)))