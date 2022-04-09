# %%
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
from data_management import *

# Read Data
general = pd.read_excel('input.xlsx', sheet_name='general')
availability = pd.read_excel('input.xlsx', sheet_name='availability')

# Get data for LP model
# Sets
hours, teachers, students, levels, days = get_sets(availability, general)

# Parameters
D, C, O, SL, TL = get_parameters(general)


# #%%

# Create model
model = pyo.ConcreteModel()

# Create model variables
model.x = pyo.Var(teachers, students, days, hours,
                  within=pyo.Binary)

model.y = pyo.Var(days, hours, within=pyo.Binary)

# Create model constraints
# Satisfy students demand
def _students_demand(m,j):
    return sum([m.x[i,j,d,h] for i in teachers for d in days for h in hours])>= C[j]

model.students_demand = pyo.Constraint(students, rule=_students_demand)


# # Define Objective function
# model.obj = pyo.Objective(
#     expr=sum([x[i]*data_gen.cost[i] for i in data_gen.id]))

# # Define optimizer
# opt = SolverFactory('cbc')
# results = opt.solve(model)

# # Attach solution to input table
# data_gen['power_generated'] = [pyo.value(x[i]) for i in data_gen.id]
# # %%

# print(results)
