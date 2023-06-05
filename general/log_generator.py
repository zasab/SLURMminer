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
import general.SLURM_based_workflows as slurm_w
import pm4py.convert as pmc
import pm4py
SEP = "\t"

def add_account_group_column(df):
    account_groups = list()
    for index, row in df.iterrows():
        # account_groups.append(str(row['ACCOUNT']) + "_" + str('nan'))
        account_groups.append(str(row['ACCOUNT']) + "_" + str(row['GROUP']))
    
    df['ACCOUNT-GROUP-BASED-CASE-ID'] = account_groups

def normal_log_apply(df):
    print()
    print("start find connected_components: ", datetime.now())
    slurm_w.SLURM_base_connected_components2(df)
    print("end find connected_components: ", datetime.now())
    print()
    print("start find account_groups: ", datetime.now())
    add_account_group_column(df)
    print("end find account_groups: ", datetime.now())
    df.to_csv(config.logger.normal_log, sep=SEP, index=False)
    return df

def ocel_log_apply(df):
    dataframe = df[df['ST'].isin(['R'])]
    ocel = pmc.convert_log_to_ocel(dataframe, activity_column='COMMAND', timestamp_column='CURRENT_TIMESTAMP', object_types=["ACCOUNT ", "GROUP", "DEPENDENCY-BASED-CASE-ID", "ACCOUNT-GROUP-BASED-CASE-ID"])
    pm4py.write_ocel(ocel, config.logger.ocel_log)