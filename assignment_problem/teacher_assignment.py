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

# Satisfy teachers supply
def _teachers_supply(m,i):
    return sum([m.x[i,j,d,h] for j in students for d in days for h in hours])<= O[i]

model.teachers_supply = pyo.Constraint(teachers, rule=_teachers_supply) 

# Levels student and teacher
def _levels(m,i,j,d,h):
    return m.x[i,j,d,h]*TL[i]<=SL[j]

model.teachers_supply = pyo.Constraint(teachers,students,days,hours, rule=_levels)

# Teachers Availability
def _teachers_availability(m,i,j,d,h):
    return m.x[i,j,d,h]*D[i,d,h]<=1

model.teachers_availability = pyo.Constraint(teachers,students,days,hours, rule=_teachers_availability)

# Teacher must teach at least one class in the week
def _one_class_week(m,i):
    return sum([m.x[i,j,d,h] for j in students for d in days for h in hours])>=1

model.one_class_week = pyo.Constraint(teachers, rule=_one_class_week)

# A student cannot receive more than one class in a day
def _one_class_day(m,j,d):
    return sum([m.x[i,j,d,h] for i in teachers for h in hours])<=1

model.one_class_day = pyo.Constraint(students, days, rule=_one_class_day)

# The weekly meeting only occurs when there's no class
def _meeting_no_class(m,d):
    sum([m.x[i,j,d,h] for i in teachers for j in students for h in hours])<=(1-sum(m.y[d,h] for h in hours))*1000

model._meeting_no_class = pyo.Constraint(days, rule=_meeting_no_class)

# Only one teacher´s meeting in the week
def _one_meeting(m):
    return sum([m.y[d,h] for d in days for h in hours])==1

model._one_meeting = pyo.Constraint(rule=_one_meeting)

# The teacher's meeting only has 1 hour duration
def one_hour_meeting(m,d,h):
    if h!=20:
        return m.y[d,h]+m.y[d,h+1]==1

model.one_hour_meeting = pyo.Constraint(days, hours, rule=one_hour_meeting)

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
