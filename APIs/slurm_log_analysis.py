from flask import Flask, render_template, request, Blueprint, Response, send_file, send_from_directory
from werkzeug.utils import secure_filename
import re
import subprocess
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
from flask_api import status
from server.response import *
from server.request import *
from server.error_messages import messages
from general import ssh_connection
from general import plots
import general.df_labeling as df_lb
import general.log_generator as lg
import pandas as pd
import pm4py
import base64
import time
import json
import plotly
import plotly.express as px
import general.df_preprocessing as dfpre
import general.df_postprocessing as dfpost
import general.slurm_log_analysis as slurm_desc
import general.df_preprocessing as dfpre

sloga = Blueprint('sloga', __name__)
SEP = "\t"

@sloga.route("/get_slurm_log_dotted_chart", methods = ["POST", "GET"])
def get_slurm_log_dotted_chart():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        if 'x_axis' in data and 'y_axis' in data:
            x = data['x_axis']
            y = data['y_axis']
        else:
            return response_json({"error":  "X axis or Y axis fields are empty."}, status.HTTP_406_NOT_ACCEPTABLE)

        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(config.logger.local_log, sep=SEP, error_bad_lines=False)
        df = dfpre.apply(df)
        dotted_chart_path = plots.scatter_plot(df, x, y)
        dotted_chart_image = open(dotted_chart_path, "rb")
        encoded_dotted_chart_image = base64.b64encode(dotted_chart_image.read())
        dec_dotted_chart = encoded_dotted_chart_image.decode()
    
        return response_json({
            "msg":  messages["success"],
            "scatter_model": dec_dotted_chart
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> get_slurm_log_dotted_chart: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@sloga.route("/job_distribution_over_time", methods = ["POST", "GET"])
def job_distribution_over_time():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(config.logger.local_log, sep=SEP, error_bad_lines=False)
        df = dfpre.apply(df)

        dataframe = dfpost.num_of_jobs_over_time(df)
        dataframe1 = dfpost.num_of_jobs_requested_cpus(df)
        dataframe2 = dfpost.num_of_pending_jobs_over_time(df)

        return response_json({
            "msg":  messages["success"],
            "slurm_log_info": json.dumps(dataframe.to_dict(orient='list')),
            "CPUS_JOBCOUNT": json.dumps(dataframe1.to_dict(orient='list')),
            "R_PD_TIME": json.dumps(dataframe2.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> job_distribution_over_time: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@sloga.route("/job_distribution_per_account", methods = ["POST", "GET"])
def job_distribution_per_account():
    try:
        data = create_data(request)

        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)

        df = pd.read_csv(config.logger.local_log, sep=SEP, error_bad_lines=False)
        df = dfpre.apply(df)
        
        filtered_df = df[['JOBID', 'ACCOUNT']]
        aggregation_functions = {'ACCOUNT': 'first'}
        n_df = filtered_df.groupby(filtered_df.JOBID).aggregate(aggregation_functions)
        n_df1 = n_df.reset_index()
        count_df = n_df1.groupby(n_df1.ACCOUNT).count()

        accounts = list()
        jobids = list()
        for ind in count_df.index:
            accounts.append(str(ind))
            jobids.append(count_df['JOBID'][ind])
        
        dataframe = pd.DataFrame({
            'ACCOUNTS': accounts,
            'JOBCOUNT': jobids
        })

        df2 = dataframe.sort_values(by=['JOBCOUNT'], ascending=False)
        # df3 = df2[~(df2['JOBCOUNT'] <= 100)]
        return response_json({
            "msg":  messages["success"],
            "jobs_per_account": json.dumps(df2.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> job_distribution_per_account: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@sloga.route("/dottet_chart_jobid_duration_label", methods = ["POST", "GET"])
def dottet_chart_jobid_duration_label():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(config.logger.local_log, sep=SEP, error_bad_lines=False)

        df = dfpre.apply(df)
        df1 = df_lb.apply_jobid_view(df)
        df2 = df_lb.apply_duration(df1)
        df3 = df_lb.apply_default_setting(df2)
        
        s_labeled_df = df3.sort_values(by=['JOBID_view'])
        filtered_df = s_labeled_df[['JOBID_view', 'START', 'DURATION_LABEL']]
        filtered_df['DURATION_LABEL'] = filtered_df['DURATION_LABEL'].map({
            'less_that_1_hour': 'green',
            'less_that_1_day': 'yellow',
            'less_that_1_week': 'orange',
            'less_that_1_month': 'red',
            'no_information': 'black'
        })
        filtered_df.fillna('black',inplace=True)
        
        return response_json({
            "msg":  messages["success"],
            "time_jobs_state": json.dumps(filtered_df.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> dottet_chart_jobid_duration_label: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@sloga.route("/get_slurm_log_column_values", methods = ["POST", "GET"])
def get_slurm_log_column_values():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
        if not os.path.exists(config.logger.normal_log):
            return response_json({"error":  "The normal event log does not exist. First generate normal log."}, status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(config.logger.normal_log, sep=SEP, error_bad_lines=False)
        unique_accounts = df['ACCOUNT'].unique()
        running_accounts = list()

        for e_account in unique_accounts:
            new_df = df[df['ACCOUNT']==e_account]
            if 'R' in new_df['ST'].unique():
                running_accounts.append(e_account)
            else:
                pass

        slurm_column_values = pd.DataFrame({
            'unique_accounts': running_accounts
        })
        return response_json({
            "msg":  messages["success"],
            "slurm_column_values": json.dumps(slurm_column_values.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> get_slurm_log_column_values: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@sloga.route("/slurm_log_description", methods = ["POST", "GET"])
def slurm_log_description():
    try:
        data = create_data(request)

        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)


        dataframe = pd.read_csv(config.logger.local_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
        res = slurm_desc.apply(dataframe)
        
        log_description = {
            "eventsNumber": res["eventsNumber"],
            "accountNumber": res["accountNumber"],
            "jobNumber": res["jobNumber"],
            "startTime": res["startTime"],
            "endTime": res["endTime"],
            "SLURMaccounts": res["SLURMaccounts"],
            "SLURMaccountsPercentage": res["SLURMaccountsPercentage"],
            "SLURMaccountNumber": res["SLURMaccountNumber"],
            "SLURMjobssPercentage": res["SLURMjobssPercentage"],
            "SLURMjobNumber": res["SLURMjobNumber"],
            "CPUusageAvg": res["CPUusageAvg"],
            "RAMusageAvg": res["RAMusageAvg"],
        }
        
    
        return response_json({
            "msg":  messages["success"],
            "s_log_description": log_description
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> slurm_log_description: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)



@sloga.route("/get_accounts_did_batches", methods = ["POST", "GET"])
def get_accounts_did_batches():
    try:
        data = create_data(request)
        print()
        print("data-----------------: ", data)
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)

        dataframe = pd.read_csv(config.logger.local_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
        duration = data['duration'].strip()
        threshold = str(data['threshold']).strip()
        if threshold.isnumeric():
            threshold = int(threshold)
        else:
            return response_json({"error":  'threshold value has to be a number.'}, status.HTTP_406_NOT_ACCEPTABLE)
        batches = slurm_desc.get_batches(dataframe, duration, threshold)

        dataframe = pd.DataFrame({
            'ACCOUNTS': list(batches.keys()),
            'batches_count': list(batches.values())
        })

        df2 = dataframe.sort_values(by=['batches_count'], ascending=False)
        return response_json({
            "msg":  messages["success"],
            "batches_account": json.dumps(df2.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> get_accounts_did_batches: EXCEPTION " + " \n [" + str(e) + "]")
        if 'does not match format \'%H:%M:%S\'' in str(e):
            return response_json({"error":  str(e)}, status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@sloga.route("/get_account_dotted_chart_info", methods = ["POST", "GET"])
def get_account_dotted_chart_info():
    try:
        data = create_data(request)
        account = data['account'].strip()
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)

        df = pd.read_csv(config.logger.local_log, sep=SEP, error_bad_lines=False)
        df = dfpre.apply(df)

        if account not in df['ACCOUNT'].unique():
            return response_json({"error":  "The user " + account + " not found."}, status.HTTP_404_NOT_FOUND)

        account_df = df[(df['ACCOUNT']==account)&(df['ST']=='PD')]        
        f_account_df = account_df[['ACCOUNT', 'JOBID', 'CURRENT_TIMESTAMP', 'ST']]
        f_account_df2 = f_account_df.sort_values(by=['JOBID'], ascending=True)
        f_account_df2['JOBID']=['J_'+str(i) for i in f_account_df2['JOBID'].values.tolist()]
        
        return response_json({
            "msg":  messages["success"],
            "account_dotted_info": json.dumps(f_account_df2.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> job_distribution_over_time: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@sloga.route("/get_project_id_topics", methods = ["POST", "GET"])
def get_project_id_topics():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        dfpre.project_ID_topic_prep(config.logger.project_ID_topic_json)
        if not os.path.exists(config.logger.project_ID_topic):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(config.logger.project_ID_topic, sep=SEP, error_bad_lines=False)
        project_ID_topic_df = dfpre.project_ID_topic_prep(config.logger.project_ID_topic_json)

        return response_json({
            "msg":  messages["success"],
            "project_ID_topic_df": json.dumps(project_ID_topic_df.to_dict(orient='list'))
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> get_slurm_log_column_values: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)
