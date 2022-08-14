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
    age_period_cask,
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
    IC,
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
model.c = pyo.Var(age_period_cask,years, within=pyo.Reals, bounds=(0,None))

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

# Seed Constraint


def _seeds(m, j):
    return m.s[j] == sum([m.y[t,j]*SP*TS[t]*IP[t] for t in terrains])


model.seeds = pyo.Constraint(years, rule = _seeds)

# Productive Terrains


def _productive_terrains(m, j):
    return m.p[j] == m.p[j-1] + sum([m.y[t, j-1]*IP[t] for t in terrains])
    

model.productive_terrains = pyo.Constraint(years, rule=_productive_terrains)

# Requested Employees


def _requested_employees(m, j):
    return sum([m.p[j]*TS[t]*MW + m.y[t,j]*TS[t]*PW*IP[t] for t in terrains]) == m.ie[j]


model.requested_employees = pyo.Constraint(years, rule=_requested_employees)

# A terrain can be planted once


def _once_planted(m, t):
    return sum([m.y[t,j] for j in years]) == (1-IP[t])


model.once_planted = pyo.Constraint(terrains, rule=_once_planted)

# Botles production limit


def _production_limit(m,k,j):
    return m.v[k,j] == BP[k,j]


model.production_limit = pyo.Constraint(age, years,rule=_production_limit)

# Cask constraints


def _cask_constraint(m, f, j):
    if j == 2012:
        return m.c[f,j] == IC[f] - sum(m.v[k,j] for k in age)
    return m.y[d, h] + m.y[d, h + 1] <= 1



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
