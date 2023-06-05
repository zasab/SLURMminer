import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import datetime
import numpy as np
import os
import config
from threading import Thread
import pandas as pd

def generate_ran_values(names):
    d = {ni: indi for indi, ni in enumerate(set(names))}
    numbers = [d[ni]+1 for ni in names]
    return numbers

def scatter_plot(df, x, y):
    # df['CURRENT_TIMESTAMP'] = pd.to_datetime(df['CURRENT_TIMESTAMP'])
    # min_time = df['CURRENT_TIMESTAMP'].min()
    # max_time = df['CURRENT_TIMESTAMP'].max()
    # start_date = datetime.datetime(2022, 11, 22, 15, 54, 19)
    # end_date = datetime.datetime(2022, 11, 22, 15, 54, 30)
    # mask = (df['CURRENT_TIMESTAMP'] > start_date) & (df['CURRENT_TIMESTAMP'] <= end_date)
    # df.loc[mask]
    # df = df.loc[mask]

    # fig = Figure()
    # axis = fig.add_subplot(1, 1, 1)

    plt.style.use('seaborn')
    fig1, ax = plt.subplots()
    colors = generate_ran_values(df[y].tolist())
    sns_plot = ax.scatter(df[x], df[y], s= 20, c=colors, cmap='winter')
    # plt.title('Scatter plot over '+ x + " and "+ y)
    scale_type = 'linear'
    

    fig = sns_plot.get_figure()
    txt = ""
    if len(df[x].unique()) > 10:
        plt.xscale(scale_type)
        txt += 'The x axis values are scaled.'
        
    if len(df[y].unique()) > 10:
        plt.yscale(scale_type)
        txt += 'The Y axis values are scaled.'
    
    if len(txt) > 0:
        fig.text(.5, .05, txt, ha='center')
    dotted_chart_path = os.path.join(config.general.models_dir, x + "_" + y + "_dotted_chart.jpg")
    fig.savefig(dotted_chart_path)
    
    # df.rename(columns={'ST': 'concept:name', 'CURRENT_TIMESTAMP': 'time:timestamp', 'JOBID': 'case:concept:name'}, inplace=True)
    # df = pm4py.format_df(df, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
    # event_log = pm4py.convert_to_event_log(df)
    # dotted_chart_path = os.path.join(config.general.models_dir, 'job_dotted_chart.jpg')
    # pm4py.save_vis_dotted_chart(event_log, dotted_chart_path)

    return dotted_chart_path

def distribution_plot(df):
    df['CURRENT_TIMESTAMP'] = pd.to_datetime(df['CURRENT_TIMESTAMP'])
    df['JUST_DATE'] = df['CURRENT_TIMESTAMP'].dt.date
    n_df = df.groupby(df.JUST_DATE).count()

    dates = list()
    jobids = list()
    for ind in n_df.index:
        dates.append(str(ind))
        jobids.append(n_df['JOBID'][ind])
        
    fig1, ax = plt.subplots()
    ax.bar(dates, jobids)
    dist_plot_path = os.path.join(config.general.models_dir, "dist_plot.jpg")
    plt.savefig(dist_plot_path)

    return dist_plot_path

