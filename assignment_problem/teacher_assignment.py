#%%
from posixpath import sep
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd

# Read Input file
availability = pd.read_excel('input.xlsx', sheet_name='availability')
general = pd.read_excel('input.xlsx', sheet_name='general')


##### Extracting sets ######
# Time spots
availability['From'] = availability['From'].astype(str).str.split(':').apply(lambda x: x[0])
availability['To'] = availability['To'].astype(str).str.split(':').apply(lambda x: x[0])
time_spots = list(set(availability['From']).union(set(availability['To'])))

# Teachers
teachers = list(set(availability['Teacher']))

# Students
students = list(set(general[general['Type']=='Student']['Name']))
#%%
# Calculate Distances between teacher and student
std_dis = general[general['Type']=='Student'][['Name','Street', 'Avenue']]
std_dis['one'] =1
teacher_dis = general[general['Type']=='Teacher'][['Name','Street', 'Avenue']]
teacher_dis['one'] =1
distances = std_dis.merge(teacher_dis,on='one',how='outer')



#%%
# Create global variable to count te number of generator
N = len(data_gen)

# Create model
model = pyo.ConcreteModel()

# Create model variables
model.x = pyo.Var(range(N),bounds=(0,None))
x = model.x

# Create model constraints
# Power balance constraing (satisfy demand)
x_sum = sum([x[i] for i in data_gen.id])
model.balance = pyo.Constraint(expr=x_sum == sum(data_load.load_demand))

# Special condition
model.cond = pyo.Constraint(expr=x[0]+x[3]>=data_load.load_demand[0])

# Upper bounds constraints
model.limits = pyo.ConstraintList()
for i in data_gen.id:
    model.limits.add(expr=x[i]<=data_gen.power_generation[i])

# Define Objective function
model.obj = pyo.Objective(expr=sum([x[i]*data_gen.cost[i] for i in data_gen.id]))

# Define optimizer
opt = SolverFactory('cbc')
results = opt.solve(model)

# Attach solution to input table
data_gen['power_generated'] = [pyo.value(x[i]) for i in data_gen.id]
# %%

print(results)