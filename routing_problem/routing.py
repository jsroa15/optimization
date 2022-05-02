# %%
import pandas as pd
import numpy as np
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
from data_management import generate_parameters


# Generate parameters and data for optimization model
nodes, edges, distance, v_in, v_out = generate_parameters()

# Create model
model = pyo.ConcreteModel()

# Create model variables
model.x = pyo.Var(edges, within=pyo.Binary)

# Create Objective Function
model.obj = pyo.Objective(expr=sum([distance[i,j]*model.x[i,j] for (i,j) in edges]))



