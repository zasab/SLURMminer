import pandas as pd

def num_of_jobs_over_time(df):
    df['CURRENT_TIMESTAMP'] = pd.to_datetime(df['CURRENT_TIMESTAMP'])
    df["CURRENT_TIMESTAMP"] = df["CURRENT_TIMESTAMP"].apply(lambda x: str(x).split(".")[0])
    n_df = df.groupby(df.CURRENT_TIMESTAMP).count()

    dates = list()
    jobids = list()
    for ind in n_df.index:
        dates.append(str(ind))
        jobids.append(n_df['JOBID'][ind])
    dataframe = pd.DataFrame({
            'TIMESTAMP': dates,
            'JOBCOUNT': jobids
        })
    
    return dataframe

def num_of_jobs_requested_cpus(df):
    filtered_df = df[['JOBID', 'CPUS']]
    n_df1 = filtered_df.groupby(filtered_df.CPUS).count()

    cpus = list()
    jobids1 = list()
    for ind1 in n_df1.index:
        cpus.append(str(ind1)+'_CPU')
        jobids1.append(n_df1['JOBID'][ind1])

    dataframe2 = pd.DataFrame({
            'CPUS': cpus,
            'CPUS_JOBCOUNT': jobids1
        })
    
    return dataframe2.sort_values(by=['CPUS_JOBCOUNT'], ascending=False)

def num_of_pending_jobs_over_time(df):
    df = df[['CURRENT_TIMESTAMP', 'ST']]
    df["CURRENT_TIMESTAMP"] = df["CURRENT_TIMESTAMP"].apply(lambda x: str(x).split(".")[0])
    # df['CURRENT_TIMESTAMP'] = pd.to_datetime(df.CURRENT_TIMESTAMP, format='%Y-%m-%d %H:%M:%S')
    states_dict = dict()
    for index, row in df.iterrows():
        time = row['CURRENT_TIMESTAMP']
        if time in states_dict:
            states_a_time = states_dict[time]
            if row['ST'] == 'PD':
                states_a_time["PDnum"] += 1
            elif row['ST'] == 'R':
                states_a_time["Rnum"] += 1
        else:
            if row['ST'] == 'PD':
                states_dict[time] = {
                    "PDnum": 1,
                    "Rnum": 0
                }
            elif row['ST'] == 'R':
                states_dict[time] = {
                    "PDnum": 0,
                    "Rnum": 1
                }

    times = list()
    Rnums = list()
    PDnums = list()
    for a_time in states_dict:
        a_nums = states_dict[a_time]
        times.append(a_time)
        Rnums.append(a_nums['Rnum'])
        PDnums.append(a_nums['PDnum'])

    dataframe = pd.DataFrame({
            'times': times,
            'Rnums': Rnums,
            'PDnums': PDnums
        })
    return dataframe