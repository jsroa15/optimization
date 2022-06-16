# %%
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
from data_management import *

# Read Data
input_file = "data.xlsx"
(
    age,
    terrains,
    years,
    cask,
    PR,
    TS,
    TP,
    IP,
    HRB,
    IW,
    HC,
    FC,
    AS,
    MW,
    PW,
    SP,
    BP,
) = get_optimization_data(input_file)

# Create model
model = pyo.ConcreteModel()

# Create model variables
# Production, inventory, and budget
model.x = pyo.Var(years, within=pyo.Reals, bounds=(0,None))
model.s = pyo.Var(years, within=pyo.Reals, bounds=(0,None))
model.v = pyo.Var(age, years, within=pyo.Reals, bounds=(0,None))
model.p = pyo.Var(years, within=pyo.Reals, bounds=(0,None))
model.y = pyo.Var(terrains, years, within=pyo.Binary)
model.b = pyo.Var(years, within=pyo.Reals, bounds=(0,None))

# HR variables
model.h = pyo.Var(years, within=pyo.Reals, bounds=(0,None))
model.f = pyo.Var(years, within=pyo.Reals, bounds=(0,None))
model.ie = pyo.Var(years, within=pyo.Reals, bounds=(0,None))


# Define Objective function
model.obj = pyo.Objective(
    expr=sum(
        [
            model.v[k, j] * PR[k]
            for k in age
            for j in years
        ]
        - [model.s[j]*SP+model.f[j]*FC+model.h[j]*HC+model.ie[j]*AS for j in years]
        + pyo.value(model.b[2016])
    )
)

# Create model constraints
# Wine Production


def _wine_production(j):
    return model.x[j] == sum([TP[t]*model.y[t,j]*IP[t] for t in terrains])


model.wine_production = pyo.Constraint(years, rule=_wine_production)

# HR constraint


def _employees_inventory(m, j):
    return m.ie[j]==m.ie[j-1]-m.f[j]+m.h[j]


model.employees_inventory = pyo.Constraint(years, rule=_employees_inventory)

# Budget Constraint


def _budget(m, j):
    return m.b[j]==m.b[j-1]-m.f[j]*FC-m.h[j]*HC-m.ie[j]*AS


model._budget = pyo.Constraint(years, rule=_budget)

# Teachers Availability


def _teachers_availability(m, i, j, d, h):
    if availability_teachers[i, d, h] == 0:
        return Constraint.Skip
    return (m.x[i, j, d, h] * availability_teachers[i, d, h]) <= 1


model.teachers_availability = pyo.Constraint(
    teachers, students, days, hours, rule=_teachers_availability
)

# # Teacher must teach at least one class in the week


def _one_class_week(m, i):
    return sum([m.x[i, j, d, h] for j in students for d in days for h in hours]) >= 1


model.one_class_week = pyo.Constraint(teachers, rule=_one_class_week)

# # A student cannot receive more than one class in a day


def _one_class_day(m, j, d):
    return sum([m.x[i, j, d, h] for i in teachers for h in hours]) <= 1


model.one_class_day = pyo.Constraint(students, days, rule=_one_class_day)

# The weekly meeting only occurs when there's no class


def _meeting_no_class(m, d):
    return (
        sum([m.x[i, j, d, h] for i in teachers for j in students for h in hours])
        <= (1 - sum(m.y[d, h] for h in hours)) * 1000
    )


model._meeting_no_class = pyo.Constraint(days, rule=_meeting_no_class)

# Only one teacher´s meeting in the week


def _one_meeting(m):
    return sum([m.y[d, h] for d in days for h in hours]) == 1


model.one_meeting = pyo.Constraint(rule=_one_meeting)

# The teacher's meeting only has 1 hour duration


def _one_hour_meeting(m, d, h):
    if h == 20:
        return Constraint.Skip
    return m.y[d, h] + m.y[d, h + 1] <= 1


model.one_hour_meeting = pyo.Constraint(days, hours, rule=_one_hour_meeting)


# Teacher's meeting only happens when all teacher can attend the meeting


def _all_teachers_can(m, d, h):
    for i in teachers:
        if availability_teachers[i, d, h] == 0:
            return Constraint.Skip
    return sum(m.y[d, h] * availability_teachers[i, d, h] for i in teachers) == m.y[
        d, h
    ] * len(teachers)


model.all_teachers_can = pyo.Constraint(days, hours, rule=_all_teachers_can)

# Classes don't start at 19 hours


def _no_start_at_19_20(m, h):
    if h >= 19:
        return (
            sum([m.x[i, j, d, h] for i in teachers for j in students for d in days])
            == 0
        )
    return Constraint.Skip


model.no_start_at_19_20 = pyo.Constraint(hours, rule=_no_start_at_19_20)

# Each class has a duration of 2 hours


def _two_hours(m, i, j, d, h):
    if h >= 19:
        return pyo.Constraint.Skip
    return m.x[i, j, d, h] + m.x[i, j, d, h + 2] <= 2


model.two_hours = pyo.Constraint(teachers, students, days, hours, rule=_two_hours)

# No overlapped classes


def _no_overlapped(m, i, d, h):
    if h >= 19:
        return Constraint.Skip
    return sum([m.x[i, j, d, h] + m.x[i, j, d, h + 1] for j in students]) <= 1


model.no_overlapped = pyo.Constraint(teachers, days, hours, rule=_no_overlapped)

# 2 classes cannot be taught at the same time


def _no_consecutive(m, i, d, h):
    return sum([m.x[i, j, d, h] for j in students]) <= 1


model.no_consecutive = pyo.Constraint(teachers, days, hours, rule=_no_consecutive)



# Define optimizer
opt = SolverFactory("cbc")
results = opt.solve(model)

print(results)

df = pd.DataFrame(
    index=pd.MultiIndex.from_tuples(
        model.x, names=["teacher", "student", "day", "hour"]
    )
)
df["x"] = [
    pyo.value(model.x[i, j, d, h])
    for i in teachers
    for j in students
    for d in days
    for h in hours
]

df = df[df["x"] == 1]
df = df.reset_index()

df2 = pd.DataFrame(index=pd.MultiIndex.from_tuples(model.y, names=["day", "hour"]))
df2["y"] = [pyo.value(model.y[d, h]) for d in days for h in hours]

df2 = df2[df2["y"] == 1]
df2 = df2.reset_index()

# Create Output
with pd.ExcelWriter("output.xlsx") as writer:
    df.to_excel(writer, sheet_name="schedule", index=False)
    df2.to_excel(writer, sheet_name="meeting", index=False)
# %%
print(pyo.value(model.obj))
