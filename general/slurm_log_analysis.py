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
import general.df_preprocessing as dfpre
import humanfriendly
from datetime import datetime, timedelta
from hurry.filesize import size
SEP = "\t"

def apply(dataframe):
    dataframe = dfpre.apply(dataframe)

     
    event_num = dataframe.shape[0]
    account_num = len(dataframe['ACCOUNT'].unique())
    jobs_num = len(dataframe['JOBID'].unique())
    
    min_time = str(dataframe['CURRENT_TIMESTAMP'].min()).split('.')[0] if '.' in str(dataframe['CURRENT_TIMESTAMP'].min()) else str(dataframe['CURRENT_TIMESTAMP'].min())
    max_time = str(dataframe['CURRENT_TIMESTAMP'].max()).split('.')[0] if '.' in str(dataframe['CURRENT_TIMESTAMP'].max()) else str(dataframe['CURRENT_TIMESTAMP'].max())
    

    slurmy_accounts = list()
    slurmy_jobs = list()
    print("start finding slurmys", datetime.now())
    for index, row in dataframe.iterrows():
        if '(unfulfilled)' in str(row['DEPENDENCY']) and row['DEPENDENCY'] != '(null)':
            if row['ACCOUNT'] not in slurmy_accounts:
                slurmy_accounts.append(row['ACCOUNT'])

            if row['JOBID'] not in slurmy_jobs:
                slurmy_jobs.append(row['JOBID'])
        else:
            pass

    slurmy_accounts_num = len(slurmy_accounts)
    slurmy_jobs_num = len(slurmy_jobs)
    print("start finding cpus", datetime.now())
    cpu_sum = 0
    for cpu_val in dataframe['CPUS'].tolist():
        s_cpu_val = str(cpu_val)
        if len(s_cpu_val)>0 and s_cpu_val.isnumeric():
            cpu_sum = cpu_sum + int(s_cpu_val)
        else:
            pass
            
    average_cpu_usage = cpu_sum / len(dataframe['CPUS'].tolist())
    print("start finding RAMs", datetime.now())
    RAM_list = list()
    for RAM in dataframe['MIN_MEMORY'].to_list():
        if RAM != 'None' and any(char.isdigit() for char in RAM) and RAM not in dataframe['PARTITION'].unique():
            num_bytes = humanfriendly.parse_size(RAM)
            RAM_list.append(num_bytes)
            
            
    average_RAM_usage = sum(RAM_list) / len(RAM_list)

    res = {
        "startTime": str(min_time),
        "endTime": str(max_time),
        "eventsNumber": str(event_num),
        "jobNumber": str(jobs_num),
        "accountNumber": str(account_num),
        "SLURMaccountsPercentage": str(round(slurmy_accounts_num/account_num, 2)),
        "SLURMaccounts": str(slurmy_accounts),
        "SLURMaccountNumber": str(slurmy_accounts_num) + " out of " + str(account_num),
        "SLURMjobssPercentage": str(round(slurmy_jobs_num/jobs_num, 2)),
        "SLURMjobNumber": str(slurmy_jobs_num) + " out of " + str(jobs_num),
        "CPUusageAvg": str(round(average_cpu_usage, 2)),
        "RAMusageAvg": str(size(round(average_RAM_usage, 2)))     
    }

    return res

def account_batches(df, start_time_obj, duration, batches_list):
    batches_dict = {}
    duration_obj = datetime.strptime(duration, '%H:%M:%S')
    next_time = start_time_obj + timedelta(hours=duration_obj.hour, minutes=duration_obj.minute, seconds=duration_obj.second)

    df['CURRENT_TIMESTAMP'] = pd.to_datetime(df.CURRENT_TIMESTAMP, format='%Y-%m-%d %H:%M:%S')
    new_df = df[(start_time_obj<df['CURRENT_TIMESTAMP']) & (df['CURRENT_TIMESTAMP']<next_time)]
    for account in new_df.ACCOUNT.unique():
        account_df = new_df[new_df['ACCOUNT']==account]
        batches_dict[account] = len(account_df.JOBID.unique())

    if len(batches_dict) > 0:
        batches_list.append(batches_dict)
    return next_time, batches_list

def num_of_intervals_an_account_did_batching(batches_list, threshold, num_of_intervals_account_did_batches):
    for batches in batches_list:
        for account in batches:
            if batches[account] >= threshold:
                if account in num_of_intervals_account_did_batches:
                    num_of_intervals_account_did_batches[account] += 1
                else:
                    num_of_intervals_account_did_batches[account] = 1


    return num_of_intervals_account_did_batches

def get_batches(df, duration, threshold):
    df = dfpre.apply(df)
    start_time = df['CURRENT_TIMESTAMP'].min()
    start_time_obj = datetime.strptime(start_time.split('.')[0], '%Y-%m-%d %H:%M:%S')
    end_time = df['CURRENT_TIMESTAMP'].max()
    end_time_obj = datetime.strptime(end_time.split('.')[0], '%Y-%m-%d %H:%M:%S')

    batches_list = []
    while start_time_obj < end_time_obj:
        next_time, new_batches_list = account_batches(df, start_time_obj, duration, batches_list)
        batches_list = new_batches_list
        start_time_obj = next_time

    num_of_intervals_account_did_batches = num_of_intervals_an_account_did_batching(batches_list, threshold, {})

    return num_of_intervals_account_did_batches


if __name__ == "__main__":
    dataframe = pd.read_csv(config.logger.local_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
    print(apply(dataframe))