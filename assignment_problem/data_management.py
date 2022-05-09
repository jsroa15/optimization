import pandas as pd
import numpy as numpy


# Function definitions
##### Extracting sets ######
def get_sets(availability, general):
    # Time spots
    hours = [int(i) for i in range(15, 21)]

    # Teachers
    teachers = list(set(availability['Teacher']))

    # Students
    students = list(set(general[general['Type'] == 'Student']['Name']))

    # Levels
    levels = list(set(general['Level']))

    # Days
    days = ['Friday', 'Monday', 'Thursday', 'Tuesday', 'Wednesday']

    return hours, teachers, students, levels, days


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


def get_parameters(general):

    # Distance
    D = get_distance(general)

    # Student Demand
    student_demand = general[general['Type'] == 'Student']
    C = student_demand.set_index('Name')['Classes']

    # Teacher Supply
    teacher_supply = general[general['Type'] == 'Teacher']
    O = teacher_supply.set_index('Name')['Classes']

    # Student Level
    student_level = general[general['Type'] == 'Student']
    SL = student_level.set_index('Name')['Level']

    # Teacher Level
    teacher_level = general[general['Type'] == 'Teacher']
    TL = teacher_level.set_index('Name')['Level']

    return D, C, O, SL, TL
