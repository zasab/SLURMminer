import os, sys
from os.path import dirname, abspath

if getattr(sys, 'frozen', False):
    filedir = os.path.dirname(sys.executable)
elif __file__:
    filedir = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(os.path.dirname(sys.executable))
elif __file__:
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(1, basedir)
import config
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

def get_state_time(sub_new_df, state):
    df_time = sub_new_df[sub_new_df['ST']==state].CURRENT_TIMESTAMP.unique()[0]
    if '.' in df_time:
        time_value = df_time.split('.')[0]
    else:
        time_value = df_time

    return datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')

def get_time(df_time):
    if '.' in df_time:
        time_value = df_time.split('.')[0]
    else:
        time_value = df_time

    return datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')

def duration_label(duration):
    if duration < 3600:
        label = 'less_that_1_hour'
    elif duration < 86400:
        label = 'less_that_1_day'
    elif duration < 604800:
        label = 'less_that_1_week'
    elif duration < 2629743:
        label = 'less_that_1_month'
    elif duration < 31556926:
        label = 'less_that_1_year'
    
    return label

def apply_jobid_view(df):
    print()
    print("start jobid_view labeling: ", datetime.now())
    df['JOBID_view'] = ""
    for jobid in df['JOBID'].unique():
        df.loc[df['JOBID']==jobid, 'JOBID_view'] = str(df.loc[df['JOBID'] == jobid].JOBID.to_list()[0])+"_J"

    return df
    print("end jobid_view labeling: ", datetime.now())

def apply_duration(df):
    print()
    print("start duration labeling: ", datetime.now())
    df['DURATION_LABEL'] = ""
    df['START'] = ""
    for jobid in df['JOBID'].unique():
        new_df = df[df['JOBID']==jobid]
        st_list = new_df['ST'].unique()
        if set(['R', 'CG']).issubset(set(st_list)):
            r_time = get_state_time(new_df, 'R')
            c_time = get_state_time(new_df, 'CG')
            duration = c_time - r_time
            duration_timestamp = timedelta.total_seconds(duration)
            label = duration_label(duration_timestamp)
            df.loc[df['JOBID']==jobid, 'DURATION_LABEL'] = label
            df.loc[df['JOBID']==jobid, 'START'] = str(r_time)
        else:
            df.loc[df['JOBID']==jobid, 'START'] = str(get_time(str(df.loc[df['JOBID'] == jobid].CURRENT_TIMESTAMP.to_list()[0])))

    df["DURATION_LABEL"] = df["DURATION_LABEL"].replace("", "no_information")
    print("end duration labeling: ", datetime.now())
    print()

    return df

def apply_default_setting(df):
    print()
    print("start default_setting labeling: ", datetime.now())
    df['CPU_DEFAULT_SETTINGS'] = ""
    df['NICE_DEFAULT_SETTINGS'] = ""
    df['MEMORY_DEFAULT_SETTINGS'] = ""
    for jobid in df['JOBID'].unique():
        new_df = df[df['JOBID']==jobid]
        nice_list = list(new_df['NICE'].unique())
        cpus_list = list(new_df['CPUS'].unique())
        min_cpus_list = list(new_df['MIN_CPUS'].unique())
        min_memory = list(new_df['MIN_MEMORY'].unique())
        if '0' in nice_list or 0 in nice_list:
            df.loc[df['JOBID']==jobid, 'NICE_DEFAULT_SETTINGS'] = 'YES'
        else:
            df.loc[df['JOBID']==jobid, 'NICE_DEFAULT_SETTINGS'] = 'NO'

        if '1' in cpus_list or 1 in cpus_list:
            df.loc[df['JOBID']==jobid, 'CPU_DEFAULT_SETTINGS'] = 'YES'
        else:
            df.loc[df['JOBID']==jobid, 'CPU_DEFAULT_SETTINGS'] = 'NO'


        if '0' in min_memory or 0 in min_memory:
            df.loc[df['JOBID']==jobid, 'MEMORY_DEFAULT_SETTINGS'] = 'YES'
        else:
            df.loc[df['JOBID']==jobid, 'MEMORY_DEFAULT_SETTINGS'] = 'NO'

    print("end default_setting labeling: ", datetime.now())
    print()

    return df