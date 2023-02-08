# %%
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
from data_management import *
import os

os.chdir("C:/repositories/optimization/wine_planning")

# Read Data
input_file = "data.xlsx"
(
    age_set,
    terrains_set,
    years_set,
    is_planted_set,
    not_planted_set,
    PROFIT,
    SIZE,
    PRODUCTIVITY,
    IP,
    BUDGET,
    IW,
    HC,
    FC,
    AS,
    MW,
    PW,
    SP,
    BP,
    CASK1_0,
    CASK2_0,
    CASK3_0,
) = get_optimization_data(input_file)

# Create model
model = pyo.ConcreteModel()

# Create model variables
# Production, inventory, and budget
# model.y = pyo.Var(terrains, years, within=pyo.Binary)
# model.x = pyo.Var(age, years, within=pyo.Reals, bounds=(0, None))
# model.s = pyo.Var(years, within=pyo.Reals, bounds=(0, None))
# model.b = pyo.Var(years, within=pyo.Reals, bounds=(0, None))
# model.v = pyo.Var(age, years, within=pyo.Reals, bounds=(0, None))
# model.p = pyo.Var(years, within=pyo.Reals, bounds=(0, None))
# model.c = pyo.Var(age_period_cask, years, within=pyo.Reals, bounds=(0, None))
# model.cum = pyo.Var(terrains, within=pyo.Reals, bounds=(0, None))
# model.q = pyo.Var(years, within=pyo.Reals, bounds=(0, None))

# # HR variables
# model.h = pyo.Var(years, within=pyo.Reals, bounds=(0, None))
# model.f = pyo.Var(years, within=pyo.Reals, bounds=(0, None))
# model.ie = pyo.Var(years, within=pyo.Reals, bounds=(0, None))


# # Define Objective function
# model.obj = pyo.Objective(
#     expr=sum([model.v[k, j] * PR[k] for k in age for j in years])
#     - sum(
#         [
#             model.s[j] * SP + model.f[j] * FC + model.h[j] * HC + model.ie[j] * AS
#             for j in years
#         ]
#     )
#     + model.b[years[-1]]
# )

# # Create model constraints
# # Wine Production


# def _production_harvest_1(m, j):
#     if j == years[-1]:
#         return pyo.Constraint.Skip
#     else:
#         return m.q[j] == sum([m.x[k, j + 1] for k in age])


# model.production_harvest_1 = pyo.Constraint(years, rule=_production_harvest_1)


# def _production_harvest_2(m, j):
#     return m.q[j] == sum([m.y[t, j] * TP[t] + TP[t] * IP[t] for t in terrains])


# model.production_harvest_2 = pyo.Constraint(years, rule=_production_harvest_2)


# # HR constraint


# def _employees_inventory(m, j):
#     if j == years[0]:
#         return m.ie[j] == IW - m.f[j] + m.h[j]
#     else:
#         return m.ie[j] == m.ie[j - 1] - m.f[j] + m.h[j]


# model.employees_inventory = pyo.Constraint(years, rule=_employees_inventory)


# # Cumulative planted terrains
# def _cumulative(m, t):
#     return m.cum[t] == sum(m.y[t, j - 1] for j in years if j > 2012)


# model.cumulative = pyo.Constraint(terrains, rule=_cumulative)


# # Requested Employees


# def _requested_employees(m, j):
#     if j == years[0]:
#         return (
#             sum([TS[t] * MW * IP[t] + m.y[t, j] * TS[t] * PW * IP[t] for t in terrains])
#             == m.ie[j]
#         )
#     else:
#         return (
#             sum(
#                 [
#                     TS[t] * MW * IP[t]
#                     + m.cum[t] * TS[t] * MW
#                     + m.y[t, j] * TS[t] * PW * IP[t]
#                     for t in terrains
#                 ]
#             )
#             == m.ie[j]
#         )


# model.requested_employees = pyo.Constraint(years, rule=_requested_employees)

# # Budget Constraint


# def _budget(m, j):
#     if j == years[0]:
#         m.b[j] == HRB - m.f[j] * FC - m.h[j] * HC - m.ie[j] * AS
#     else:
#         return m.b[j] == m.b[j - 1] - m.f[j] * FC - m.h[j] * HC - m.ie[j] * AS


# model._budget = pyo.Constraint(years, rule=_budget)

# # Seed Constraint


# def _seeds(m, j):
#     return m.s[j] == sum([m.y[t, j] * SP * TS[t] * IP[t] for t in terrains])


# model.seeds = pyo.Constraint(years, rule=_seeds)

# # Productive Terrains


# def _productive_terrains(m, j):
#     if j == years[0]:
#         return m.p[j] == sum(IP) + sum([m.y[t, j - 1] * IP[t] for t in terrains])
#     else:
#         return m.p[j] == m.p[j - 1] + sum([m.y[t, j - 1] * IP[t] for t in terrains])


# model.productive_terrains = pyo.Constraint(years, rule=_productive_terrains)

# # A terrain can be planted once


# def _once_planted(m, t):
#     return sum([m.y[t, j] for j in years]) == (1 - IP[t])


# model.once_planted = pyo.Constraint(terrains, rule=_once_planted)

# # Botles production limit


# def _production_limit(m, k, j):
#     return m.x[k, j] == BP[k, j]


# model.production_limit = pyo.Constraint(age, years, rule=_production_limit)

# # Cask constraint, production and sales relationship


# def _cask_constraint_1(m, j):
#     if j == years[0]:
#         return m.c[1, j] == IC[1] + sum(m.x[k, j] for k in age)
#     else:
#         return m.c[1, j] == sum(m.x[k, j] for k in age)


# model.cask_constraint_1 = pyo.Constraint(years, rule=_cask_constraint_1)


# def _cask_constraint_2(m, j):
#     if j == years[0]:
#         return m.c[2, j] == IC[2] + m.x[3, j - 1] - m.v[1, j]
#     else:
#         return m.c[2, j] == m.x[3, j - 1] - m.v[1, j]


# model.cask_constraint_2 = pyo.Constraint(years, rule=_cask_constraint_2)


# def _cask_constraint_3(m, j):
#     if j == years[0]:
#         return m.c[3, j] == IC[3] + m.x[3, j - 2]
#     else:
#         return m.c[3, j] == m.x[3, j - 2]


# model.cask_constraint_3 = pyo.Constraint(years, rule=_cask_constraint_3)


# def _cask_constraint_4(m, j):
#     if j == years[0]:
#         return m.c[3, j] == IC[3] + m.x[3, j - 2]
#     else:
#         return m.c[3, j] == m.v[3, j + 1]


# model.cask_constraint_4 = pyo.Constraint(years, rule=_cask_constraint_4)

# # Define optimizer
# opt = SolverFactory("cbc")
# results = opt.solve(model)

# print(results)

# df = pd.DataFrame(index=pd.MultiIndex.from_tuples(model.x, names=["age", "year"]))
# df["x"] = [pyo.value(model.x[k, j]) for k in age for j in years]
# df = df.reset_index()

# df2 = pd.DataFrame(index=pd.MultiIndex.from_tuples(model.y, names=["terrain", "year"]))
# df2["y"] = [pyo.value(model.y[t, j]) for t in terrains for j in years]

# df2 = df2[df2["y"] == 1]
# df2 = df2.reset_index()

# # Create Output
# with pd.ExcelWriter("output.xlsx") as writer:
#     df.to_excel(writer, sheet_name="production", index=False)
#     df2.to_excel(writer, sheet_name="planted terrains", index=False)
# # %%
# print(pyo.value(model.obj))
