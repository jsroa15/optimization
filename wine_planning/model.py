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
model.y = pyo.Var(terrains_set, years_set, within=pyo.Binary)
model.x = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.b = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.v = pyo.Var(age_set, years_set, within=pyo.Reals, bounds=(0, None))
model.p = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.pl = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.h = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.f = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.ie = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.mant = pyo.Var(terrains_set, within=pyo.Reals, bounds=(0, None))
model.cask1 = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.cask2 = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))
model.cask3 = pyo.Var(years_set, within=pyo.Reals, bounds=(0, None))


# # Define Objective function
model.PROFIT = sum(model.v[i, t] * PROFIT[i] for i in age_set for t in years_set)
model.PEOPLE_COST = sum(
    model.f[t] * FC + model.h[t] * HC + model.ie[t] * AS for t in years_set
)
model.SEED_COST = sum(
    model.y[j, t] * SP * SIZE[j] for j in terrains_set for t in years_set
)

model.obj = pyo.Objective(expr=model.PROFIT - model.PEOPLE_COST - model.SEED_COST)


# Create model constraints
# ***Available employees***
def _available_employees(m, t):
    if t == years_set[0]:
        return m.ie[t] == IW - m.f[t] + m.h[t]
    else:
        return m.ie[t] == m.ie[t - 1] + m.f[t] + m.h[t]


model.available_employees = pyo.Constraint(years_set, rule=_available_employees)


# ***Hired Employees***
def _hired_employees(m, t):
    return m.h[t] == sum(m.y[j, t] * SIZE[j] * PW for j in not_planted_set)


model.hired_employees = pyo.Constraint(years_set, rule=_hired_employees)


# ***Each planted terrain has maintenance workers***
def _planted_terrain_employees_1(m, j):
    return m.mant[j] == sum(m.y[j, t] * MW * SIZE[j] for t in years_set)


model.planted_terrain_employees_1 = pyo.Constraint(
    not_planted_set, rule=_planted_terrain_employees_1
)


def _planted_terrain_employees_2(m, j):
    return m.mant[j] >= 0


model.planted_terrain_employees_2 = pyo.Constraint(
    not_planted_set, rule=_planted_terrain_employees_2
)


# ***Fired Employees***
def _fired_employees(m, t):
    if t == years_set[0]:
        return pyo.Constraint.Skip
    else:
        return m.f[t] == sum(
            m.y[j, t - 1] * SIZE[j] * PW - m.mant[j] for j in not_planted_set
        )


model.fired_employees = pyo.Constraint(years_set, rule=_fired_employees)


# Budget Constraints


# ***Operational cost cannot exceed the budget
def _operational_cost(m):
    return (
        sum(m.y[j, t] * SP * SIZE[j] for j in not_planted_set for t in years_set)
        + sum(m.ie[t] * AS + m.h[t] * HC + m.f[t] * FC for t in years_set)
        <= BUDGET
    )


model.operational_cost = pyo.Constraint(rule=_operational_cost)


# ***Available Budget***
def _available_budget(m, t):
    if t == years_set[0]:
        return m.b[t] == BUDGET - (
            sum(m.y[j, t] * SP * SIZE[j] for j in not_planted_set for t in years_set)
            + sum(m.ie[t] * AS + m.h[t] * HC + m.f[t] * FC for t in years_set)
        )

    else:
        return m.b[t] == m.b[t - 1] - (
            sum(m.y[j, t] * SP * SIZE[j] for j in not_planted_set for t in years_set)
            + sum(m.ie[t] * AS + m.h[t] * HC + m.f[t] * FC for t in years_set)
        )


model.available_budget = pyo.Constraint(years_set, rule=_available_budget)


# Production Constraints


# ***Production for each period***
def _production(m, t):
    return m.x[t] == sum(PRODUCTIVITY[j] for j in is_planted_set) + sum(
        m.y[j, t] * PRODUCTIVITY[j] for j in not_planted_set
    )


model.production = pyo.Constraint(years_set, rule=_production)


# ***A terrain can be planted only once***
def _terrain_planted_once(m, j):
    return sum(m.y[j, t] for t in years_set) <= 1


model.terrain_planted_once = pyo.Constraint(not_planted_set, rule=_terrain_planted_once)




stop = 1

# # Wine Production


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
