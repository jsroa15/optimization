#%%
import pandas as pd
import numpy as numpy
from teacher_assignment import *


days_list
hours_list = [i for i in range(15,21)]
def get_availability(days_list,hours_list, teachers_list):
    
    # Build auxiliar data frames to full teacher's schedule
    df_days = pd.DataFrame({"Day":days_list,"Value":[1 for i in range(len(days_list))]})
    df_teachers = pd.DataFrame({"Teacher":teachers_list,"Value":[1 for i in range(len(teachers_list))]})
    df_hours = pd.DataFrame({"Hour":hours_list,"Value":[1 for i in range(len(hours_list))]})
    
    aux = df_teachers.merge(df_days,on='Value',how='outer')
    aux = aux.merge(df_hours, on ='Value', how='outer')
    print(aux)
    
    
get_availability(days_list=days_list,
                 hours_list=hours_list,
                 teachers_list=list(teachers))
