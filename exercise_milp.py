#%%
import pandas as pd
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from pyomo.environ import *

# Define model
model = pyo.ConcreteModel()
range_i = 5

# Create model variables
model.x = pyo.Var(range(1,range_i+1), within=Integers, bounds=(0,None))
model.y = pyo.Var(bounds=(0,None))

x = model.x
y = model.y

model.pprint()

# Model constraints
model.C1 = pyo.Constraint(expr=sum([x[i] for i in range(1,range_i+1)]) + y <= 20)

model.C2 = pyo.Constraint(expr=sum([i*x[i] for i in range(1,range_i+1)]) >= 10)

model.C3 = pyo.Constraint(expr=x[5] + 2*y >=30)

# Constraint list
model.C4 = pyo.ConstraintList()

for i in range(1,range_i+1):
    model.C4.add(expr = x[i]+y >= 15)

# Define Objective function
model.obj = pyo.Objective(expr=sum([x[i] for i in range(1,range_i+1)])+y,sense=minimize)

# Define optimizer
opt = SolverFactory('cbc')
results = opt.solve(model)


print(results)
print(pyo.value(y))

x_result = [pyo.value(x[i]) for i in range(1,range_i+1)]
print(x_result)
print(pyo.value(model.obj))

# %%
