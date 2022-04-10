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
availability_teachers = get_availability(availability, days, hours, teachers)
availability_teachers.replace(0, -1, inplace=True)


# Create model
model = pyo.ConcreteModel()

# Create model variables
model.x = pyo.Var(teachers, students, days, hours,
                  within=pyo.Binary)

model.y = pyo.Var(days, hours, within=pyo.Binary)

# Create model constraints
# Satisfy students demand


def _students_demand(m, j):
    return sum([m.x[i, j, d, h] for i in teachers for d in days for h in hours]) >= C[j]


model.students_demand = pyo.Constraint(students, rule=_students_demand)

# Satisfy teachers supply


def _teachers_supply(m, i):
    return sum([m.x[i, j, d, h] for j in students for d in days for h in hours]) <= O[i]


model.teachers_supply = pyo.Constraint(teachers, rule=_teachers_supply)

# Levels student and teacher


def _levels(m, i, j, d, h):
    return m.x[i, j, d, h]*TL[i] <= SL[j]


model._levels = pyo.Constraint(teachers, students, days, hours, rule=_levels)

# Teachers Availability


def _teachers_availability(m, i, j, d, h):

    return (m.x[i, j, d, h]*availability_teachers[i, d, h]) <= 1


model.teachers_availability = pyo.Constraint(
    teachers, students, days, hours, rule=_teachers_availability)

# Teacher must teach at least one class in the week


def _one_class_week(m, i):
    return sum([m.x[i, j, d, h] for j in students for d in days for h in hours]) >= 1


model.one_class_week = pyo.Constraint(teachers, rule=_one_class_week)

# A student cannot receive more than one class in a day


def _one_class_day(m, j, d):
    return sum([m.x[i, j, d, h] for i in teachers for h in hours]) <= 1


model.one_class_day = pyo.Constraint(students, days, rule=_one_class_day)

# The weekly meeting only occurs when there's no class


def _meeting_no_class(m, d):
    return sum([m.x[i, j, d, h] for i in teachers for j in students for h in hours]) <= (1-sum(m.y[d, h] for h in hours))*1000


model._meeting_no_class = pyo.Constraint(days, rule=_meeting_no_class)

# Only one teacher´s meeting in the week


def _one_meeting(m):
    return sum([m.y[d, h] for d in days for h in hours]) == 1


model.one_meeting = pyo.Constraint(rule=_one_meeting)

# The teacher's meeting only has 1 hour duration


def _one_hour_meeting(m, d, h):
    if h == 20:
        return Constraint.Skip
    return m.y[d, h]+m.y[d, h+1] == 1


model.one_hour_meeting = pyo.Constraint(days, hours, rule=_one_hour_meeting)

# Teacher's meeting only happens when all teacher can attend the meeting


def _all_teachers_can(m, d, h):
    return sum([m.x[i, j, d, h] for i in teachers for j in students]) <= (1-sum([m.y[d, h] for d in days for h in hours]))*1000


model.all_teachers_can = pyo.Constraint(days, hours, rule=_all_teachers_can)

# Classes don't start at 19 hours


def _no_start_at_19(m):
    return sum([m.x[i, j, d, 19] for i in teachers for j in students for d in days]) == 0


model.no_start_at_19 = pyo.Constraint(rule=_no_start_at_19)

# Each class has a duration of 2 hours


def _two_hours(m, i, j, d, h):
    if h >= 19:
        return pyo.Constraint.Skip
    return m.x[i, j, d, h]+m.x[i, j, d, h+2] == 2


model.two_hours = pyo.Constraint(
    teachers, students, days, hours, rule=_two_hours)

# Classes cannot have duration of 1 hours


def _no_one_hour(m, i, j, d, h):
    if h == 20:
        return Constraint.Skip
    return m.x[i, j, d, h]+m.x[i, j, d, h+1] <= 1


model.no_one_hour = pyo.Constraint(
    teachers, students, days, hours, rule=_no_one_hour)

# 2 classes cannot be taught at the same time


def _no_consecutive(m, i, d, h):
    return sum([m.x[i, j, d, h] for j in students]) <= 1


model.no_consecutive = pyo.Constraint(
    teachers, days, hours, rule=_no_consecutive)

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
