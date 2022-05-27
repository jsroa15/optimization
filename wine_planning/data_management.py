import pandas as pd
import numpy as numpy


# Function definitions
##### Extracting sets ######

profit = pd.read_excel('data.xlsx', sheet_name='Profit')
terrains = pd.read_excel('data.xlsx', sheet_name='Terrains')
budget = pd.read_excel('data.xlsx', sheet_name='Budget')
casks = pd.read_excel('data.xlsx', sheet_name='Casks')
production_limit = pd.read_excel('data.xlsx', sheet_name='Production Limit')
def get_sets(profit,terrains,casks,production_limit):
    
    age = list(set(profit['Age']))
    terrains = list(set(terrains['Terrain']))
    years = list(set(production_limit['Period']))
    cask = list(set(casks['Cask Year']))
    
    return age, terrains, years, cask
    

def get_availability(availability, days_list, hours_list, teachers_list):

    # Build auxiliar availability frames to full teacher's schedule
    df_days = pd.DataFrame(
        {"Day": days_list, "Value": [1 for i in range(len(days_list))]})
    df_teachers = pd.DataFrame({"Teacher": teachers_list, "Value": [
                               1 for i in range(len(teachers_list))]})
    df_hours = pd.DataFrame({"Hour": hours_list, "Value": [
                            1 for i in range(len(hours_list))]})

    aux = df_teachers.merge(df_days, on='Value', how='outer')
    aux = aux.merge(df_hours, on='Value', how='outer')

    availability['Value'] = 1
    sub = availability[['Teacher', 'To', 'Day', 'Value']]
    sub.rename(columns={'To': 'From'}, inplace=True)

    avail = pd.concat([availability, sub])
    avail['From'] = avail['From'].astype(
        'str').str.split(':').apply(lambda x: x[0])
    avail['From'] = avail['From'].astype('int')
    avail = aux.merge(avail, left_on=['Teacher', 'Day', 'Hour'], right_on=[
                      'Teacher', 'Day', 'From'], how='left')
    avail = avail.drop(columns=['From', 'To']).drop_duplicates().fillna(0)
    avail['Value_x'] = avail['Value_x']-avail['Value_y']
    avail.rename(columns={'Value_x': 'Availability'}, inplace=True)

    availability = avail.set_index(['Teacher', 'Day', 'Hour'])['Availability']

    return availability


def get_distance(general):
    # Calculate Distances between teacher and student
    std_dis = general[general['Type'] ==
                      'Student'][['Name', 'Street', 'Avenue']]
    std_dis['one'] = 1
    teacher_dis = general[general['Type'] ==
                          'Teacher'][['Name', 'Street', 'Avenue']]
    teacher_dis['one'] = 1
    distances = std_dis.merge(teacher_dis, on='one', how='outer')

    dis_street = abs(distances['Street_x']-distances['Street_y'])
    dis_avenue = abs(distances['Avenue_x']-distances['Avenue_y'])
    distances['Distance'] = dis_street+dis_avenue
    distances.rename(columns={'Name_x': 'Student',
                              'Name_y': 'Teacher'}, inplace=True)
    distances = distances.set_index(['Teacher', 'Student'])['Distance']

    return distances


def get_parameters(profit,terrains,budget,casks,production_limit):
    # Profit
    PR = profit.set_index('Age')['Gross Profit']
    
    # Terrain Size
    TS = terrains.set_index('Terrain')['Acres']
 
    # Terrain Productivity
    TP = terrains.set_index('Terrain')['Productivity']
    
    # Terrains is Planted?
    terrains.replace({'YES':1,'NO':0},inplace=True)
    IP = terrains.set_index('Terrain')['Planted']
    
    pass
