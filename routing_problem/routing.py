# %%
import pandas as pd
import numpy as np
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
from data_management import generate_parameters


# Generate parameters and data for optimization model
nodes, edges, distance, v_in, v_out, start_node, final_node = generate_parameters()

# Create model
model = pyo.ConcreteModel()

# Create model variables
model.x = pyo.Var(edges, within=pyo.Binary)

# Create Objective Function
model.obj = pyo.Objective(expr=sum([distance[i,j]*model.x[i,j] for (i,j) in edges]))

# Model Constraints
def _flow_balance(model,i):
    flow_in = sum([model.x[j,i] for j in v_in[i]])
    flow_out = sum([model.x[i,j] for j in v_out[i]])
    
    if i == start_node:
        constraint = (flow_out == 1)
    
    elif i == final_node:
        constraint = (flow_in == 1)

    else:
        constraint = (flow_in == flow_out)
        
    return constraint

model.flow_balance = pyo.Constraint(nodes, rule=_flow_balance)

# Define optimizer
opt = SolverFactory('cbc')
results = opt.solve(model)





