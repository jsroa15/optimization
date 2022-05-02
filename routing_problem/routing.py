# %%
import pandas as pd
import numpy as np
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
from data_management import generate_parameters

nodes, edges, distance, v_in, v_out = generate_parameters()
