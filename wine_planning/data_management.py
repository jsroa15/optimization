import pandas as pd
import numpy as numpy

# Data read


def read_data(input_file):
    profit = pd.read_excel(input_file, sheet_name="Profit")
    terrains = pd.read_excel(input_file, sheet_name="Terrains")
    general = pd.read_excel(input_file, sheet_name="General Parameters")
    casks = pd.read_excel(input_file, sheet_name="Casks")
    production_limit = pd.read_excel(input_file, sheet_name="Production Limit")

    return profit, terrains, general, casks, production_limit


# Function definitions
##### Extracting sets ######


def get_sets(profit, terrains, casks, production_limit):

    age = list(set(profit["Age"]))
    terrains = list(set(terrains["Terrain"]))
    years = list(set(production_limit["Period"]))
    cask = list(set(casks["Cask Year"]))

    return age, terrains, years, cask


##### Extracting parameters ######


def get_parameters(profit, terrains, general, casks, production_limit):
    # Profit
    PR = profit.set_index("Age")["Gross Profit"]

    # Terrain Size
    TS = terrains.set_index("Terrain")["Acres"]

    # Terrain Productivity
    TP = terrains.set_index("Terrain")["Productivity"]

    # Terrains is Planted?
    terrains.replace({"YES": 1, "NO": 0}, inplace=True)
    IP = terrains.set_index("Terrain")["Planted"]

    # HR Budget
    HRB = general.iloc[5, 1]

    # Initial Workers
    IW = general.iloc[0, 1]

    # Hiring cost
    HC = general.iloc[2, 1]

    # Lay off cost
    FC = general.iloc[3, 1]

    # Annual Salary
    AS = general.iloc[1, 1]

    # Maintenance workers needed
    MW = general.iloc[6, 1]

    # Plant workers needed
    PW = general.iloc[7, 1]

    # Seed Price
    SP = general.iloc[4, 1]

    # Botle production
    BP = production_limit.set_index(["Age", "Period"])["Production Limit"]
    
    # Initial Casks
    IC = casks.set_index("Cask Year")["Amount"]

    return PR, TS, TP, IP, HRB, IW, HC, FC, AS, MW, PW, SP, BP, IC


def get_optimization_data(input_file):
    profit, terrains, general, casks, production_limit = read_data(input_file)

    # Sets
    age, terrains_set, years, cask = get_sets(profit, terrains, casks, production_limit)

    # Parameters
    PR, TS, TP, IP, HRB, IW, HC, FC, AS, MW, PW, SP, BP, IC = get_parameters(
        profit, terrains, general, casks, production_limit
    )

    return (
        age,
        terrains_set,
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
        IC,
    )
