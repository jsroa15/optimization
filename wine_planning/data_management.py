import pandas as pd
import numpy as numpy

# Data read


def read_data(input_file):
    profit = pd.read_excel(input_file, sheet_name="Profit")
    terrains = pd.read_excel(input_file, sheet_name="Terrains")
    terrains.replace({"YES": 1, "NO": 0}, inplace=True)
    general = pd.read_excel(input_file, sheet_name="General Parameters")
    casks = pd.read_excel(input_file, sheet_name="Casks")
    production_limit = pd.read_excel(input_file, sheet_name="Production Limit")

    return profit, terrains, general, casks, production_limit


# Function definitions
##### Extracting sets ######


def get_sets(profit, terrains, casks, production_limit):
    age_set = list(set(profit["Age"]))
    terrains_set = list(set(terrains["Terrain"]))
    years_set = list(set(production_limit["Period"]))
    years_set.sort()
    is_planted_set = list(set(terrains[terrains["Planted"] == 1]["Terrain"]))
    not_planted_set = list(set(terrains[terrains["Planted"] == 0]["Terrain"]))

    return age_set, terrains_set, years_set, is_planted_set, not_planted_set


##### Extracting parameters ######


def get_parameters(profit, terrains, general, casks, production_limit):
    # Profit
    PROFIT = profit.set_index("Age")["Gross Profit"]

    # Terrain Size
    SIZE = terrains.set_index("Terrain")["Acres"]

    # Terrain Productivity
    PRODUCTIVITY = terrains.set_index("Terrain")["Productivity"]

    # Seed Price
    SP = general.iloc[4, 1]

    # Budget
    BUDGET = general.iloc[5, 1]

    # Terrains is Planted?
    terrains.replace({"YES": 1, "NO": 0}, inplace=True)
    IP = terrains.set_index("Terrain")["Planted"]

    # Initial Workers
    IW = general.iloc[0, 1]

    # Annual Salary
    AS = general.iloc[1, 1]

    # Hiring cost
    HC = general.iloc[2, 1]

    # Lay off cost
    FC = general.iloc[3, 1]

    # Maintenance workers needed
    MW = general.iloc[6, 1]

    # Plant workers needed
    PW = general.iloc[7, 1]

    # Botle production
    BP = production_limit.set_index(["Age", "Period"])["Production Limit"]

    # Initial Casks
    CASK1_0 = casks.set_index("Cask Year")["Amount"][1]
    CASK2_0 = casks.set_index("Cask Year")["Amount"][2]
    CASK3_0 = casks.set_index("Cask Year")["Amount"][3]
    return (
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
    )


def get_optimization_data(input_file):
    profit, terrains, general, casks, production_limit = read_data(input_file)

    # Sets
    age_set, terrains_set_set, years_set, is_planted_set, not_planted_set = get_sets(
        profit, terrains, casks, production_limit
    )

    # Parameters
    (
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
    ) = get_parameters(profit, terrains, general, casks, production_limit)

    return (
        age_set,
        terrains_set_set,
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
    )
