import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory


# Create model instance
model = pyo.ConcreteModel()

# Create model variables
model.x = pyo.Var(bounds = (0,3))
model.y = pyo.Var()

x = model.x
y = model.y

# Create Model Constraints
model.C1 = pyo.Constraint(expr=x+y<=8)
model.C2 = pyo.Constraint(expr=8*x+3*y>=-24)
model.C3 = pyo.Constraint(expr=-6*x+8*y<=48)
model.C4 = pyo.Constraint(expr=3*x+5*y<=15)

# Create Objective Function
model.obj = pyo.Objective(expr=-4*x-2*y, sense=minimize)

# Define Optimizer
opt = SolverFactory('cbc')

# Execute Optimization
opt.solve(model)

# Print Solution
model.pprint()
print(pyo.value(x))
print(pyo.value(y))
