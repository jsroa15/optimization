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
# BUDGET=10000000000000
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
    model.y[j, t] * SP * SIZE[j] for j in not_planted_set for t in years_set
)

model.obj = pyo.Objective(expr=model.PROFIT ,sense = pyo.maximize)


# Create model constraints
# ***Available employees***
def _available_employees(m, t):
    if t == years_set[0]:
        return m.ie[t] == IW - m.f[t] + m.h[t]
    else:
        return m.ie[t] ==m.ie[t - 1] - m.f[t] + m.h[t]


model.available_employees = pyo.Constraint(years_set, rule=_available_employees)


# ***Hired Employees***
def _hired_employees(m, t):
    return m.h[t] == sum(m.y[j, t] * SIZE[j] * PW for j in not_planted_set)


model.hired_employees = pyo.Constraint(years_set, rule=_hired_employees)


# ***Each planted terrain has maintenance workers***
def _planted_terrain_employees_1(m, j):
    return m.mant[j] == MW * SIZE[j]*IP[j]+sum(m.y[j, t] * MW * SIZE[j] for t in years_set)


model.planted_terrain_employees_1 = pyo.Constraint(
    terrains_set, rule=_planted_terrain_employees_1
)


def _planted_terrain_employees_2(m, j):
    return m.mant[j] >= 0


model.planted_terrain_employees_2 = pyo.Constraint(
    not_planted_set, rule=_planted_terrain_employees_2
)


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
def _terrain_planted(m, j):
    return sum(m.y[j, t] for t in years_set) <= 1


model.terrain_planted = pyo.Constraint(not_planted_set, rule=_terrain_planted)



# Casks and sales constraints


# ***One year cask***
def _cask_1(m, t):
    if t == years_set[0]:
        return m.cask1[t] == CASK1_0
    else:
        return m.cask1[t] == m.x[t-1] - sum(m.v[i,t] for i in age_set)
    

model.cask_1 = pyo.Constraint(years_set, rule=_cask_1)


# ***Two year cask***
def _cask_2(m, t):
    if t == years_set[0]:
        return m.cask2[t] == CASK2_0
    else:
        return m.cask2[t] == m.cask1[t-1]

model.cask_2 = pyo.Constraint(years_set, rule=_cask_2)

# ***Three year cask***
def _cask_3(m, t):    
    if t == years_set[0]:
        return m.cask3[t] == CASK3_0
    else:
        return m.cask3[t] == m.cask2[t-1] - sum(m.v[i,t] for i in age_set)
model.cask_3 = pyo.Constraint(years_set, rule=_cask_3)


# ***Relation between cask and sales***
def _cask_sales(m, i,t):
    if i == age_set[0]:
        return m.v[i, t] <= m.cask1[t] 
    elif i == age_set[1]:
        return m.v[i, t] == m.cask3[t]
    else:
        pyo.Constraint.Skip


model.cask_sales = pyo.Constraint(age_set,years_set, rule=_cask_sales)


# Sales and bottle production


# ***Sales cannot exceed bottles production***
def _bottles_limit(m, i, t):
   return m.v[i,t] <= BP[i,t]
    
    
model.bottles_limit = pyo.Constraint(age_set,years_set, rule=_bottles_limit)


# # Define optimizer
opt = SolverFactory("cbc")
results = opt.solve(model)

print(results)
try:
    df = pd.DataFrame(index=pd.Index([t for t in years_set]))
    df["x"] = [pyo.value(model.x[t]) for t in years_set]
    
    df2 = pd.DataFrame(index=pd.MultiIndex.from_tuples(model.y, names=["terrain", "year"]))
    df2["y"] = [pyo.value(model.y[j, t]) for j in terrains_set for t in years_set]
  
    df3 = pd.DataFrame(index=pd.MultiIndex.from_tuples(model.v, names=["age", "year"]))
    df3["v"] = [pyo.value(model.v[i, t]) for i in age_set for t in years_set]
    

    df4 = pd.DataFrame(index=pd.Index([j for j in terrains_set]))
    df4["mant"] = [pyo.value(model.mant[j]) for j in terrains_set]
    
    df5 = pd.DataFrame(index=pd.Index([t for t in years_set]))
    df5["h"] = [pyo.value(model.h[t]) for t in years_set]
    
    df6 = pd.DataFrame(index=pd.Index([t for t in years_set]))
    df6["f"] = [pyo.value(model.f[t]) for t in years_set]
    
    df7 = pd.DataFrame(index=pd.Index([t for t in years_set]))
    df7["ie"] = [pyo.value(model.ie[t]) for t in years_set]
    
    df = df.reset_index()
    df2 = df2.reset_index()
    df3 = df3.reset_index()
    df4 = df4.reset_index()
    df5 = df5.reset_index()
    df6 = df6.reset_index()
    df7 = df7.reset_index()
    
    dfs = [df,df2,df3,df4,df5, df6,df7]
    
    for df in dfs:
        print(df)
        print("++++++++++++++++++++++++++++++++")
    
    # Create Output
    with pd.ExcelWriter("output.xlsx") as writer:
        df.to_excel(writer, sheet_name="production", index=False)
        df2.to_excel(writer, sheet_name="planted terrains", index=False)
        df3.to_excel(writer, sheet_name="sales", index=False)
        df4.to_excel(writer, sheet_name="mant_workers", index=False)
        df5.to_excel(writer, sheet_name="hired_workers", index=False)
        df6.to_excel(writer, sheet_name="fired_workers", index=False)
        df7.to_excel(writer, sheet_name="avail_workers", index=False)
    # %%
    print(pyo.value(model.obj))
except ValueError:
    print('model infeseable')
