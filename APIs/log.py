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
import general.df_labeling as df_lb

log = Blueprint('log', __name__)
SEP = "\t"

@log.route("/start_logging", methods = ["POST", "GET"])
def start_logging():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        serverhost = data['serverhost']
        username = data['username']
        password = data['password']
        

        if 'logging_file_name' in data:
            logging_file_name = str(data['logging_file_name']).strip()
        else:
            logging_file_name = config.logger.local_log

        # check ssh
        try:
            ssh1 = ssh_connection.get_ssh_client(serverhost, username, password)
        except:
            return response_json({"error":  messages["ssh_error"]}, status.HTTP_404_NOT_FOUND)            
        
        logging_res = subprocess.Popen(
            [
                config.general.python_path, 
                os.path.join(basedir , 'general', 'connect.py'),
                serverhost, 
                username, 
                password, 
                logging_file_name
            ] , stdout=subprocess.PIPE)

        while not os.path.exists(config.logger.local_log):
            time.sleep(3)
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)

        dataframe = pd.read_csv(config.logger.local_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
        dataframe = dfpre.apply(dataframe)
        accounts = len(dataframe['ACCOUNT'].unique())
        job_id_numbers = len(dataframe['JOBID'].unique())
        
        min_time = str(dataframe['CURRENT_TIMESTAMP'].min()).split('.')[0] if '.' in str(dataframe['CURRENT_TIMESTAMP'].min()) else str(dataframe['CURRENT_TIMESTAMP'].min())
        max_time = str(dataframe['CURRENT_TIMESTAMP'].max()).split('.')[0] if '.' in str(dataframe['CURRENT_TIMESTAMP'].max()) else str(dataframe['CURRENT_TIMESTAMP'].max())
        return response_json({
            "msg":  messages["success"],
            "accounts": accounts,
            "job_id_numbers": job_id_numbers,
            "min_time": min_time,
            "max_time": max_time
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> start_logging: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@log.route("/get_slurm_log", methods = ["POST", "GET"])
def get_slurm_log():
    try:
        data = create_data(request)
        print()
        print("data: ", data)

        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
            
        return send_file(
            config.logger.local_log,
            mimetype='text/csv',
            as_attachment=True
            )
    except Exception as e:
        print("log-> get_slurm_log: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@log.route("/get_normal_event_log", methods = ["POST", "GET"])
def get_normal_event_log():
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
        lg.normal_log_apply(df3)

        return send_file(
            config.logger.normal_log,
            mimetype='text/csv',
            as_attachment=True
            )
    except Exception as e:
        print("log-> get_normal_event_log: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@log.route("/get_ocel_log", methods= ["POST", "GET"])
def get_ocel_log():
    try:
        data = create_data(request)
        if not os.path.exists(config.logger.normal_log):
            return response_json({"error":  "The normal event log does not exist. First generate normal log."}, status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(config.logger.normal_log, sep=SEP, error_bad_lines=False)
        
        lg.ocel_log_apply(df)
        return send_file(
                config.logger.ocel_log,
                mimetype='application/json',
                as_attachment=True
                )
    except Exception as e:
        print("log-> get_ocel_log: EXCEPTION " + " \n [" + str(e) + "]")
        if 'pm4py.convert' in str(e):
            return response_json({"error":  "Please update to pm4py 2.3.3."}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@log.route("/restart_logging", methods = ["POST", "GET"])
def restart_logging():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        serverhost = data['serverhost']
        username = data['username']
        password = data['password']
        
        logging_file_name = config.logger.local_log
        os.remove(logging_file_name)
        time.sleep(5000)

        try:
            ssh1 = ssh_connection.get_ssh_client(serverhost, username, password)
        except:
            return response_json({"error":  messages["ssh_error"]}, status.HTTP_404_NOT_FOUND)            

        logging_res = subprocess.Popen(
            [
                config.general.python_path, 
                os.path.join(basedir , 'general', 'connect.py'),
                serverhost, 
                username, 
                password, 
                logging_file_name
            ] , stdout=subprocess.PIPE)
            

        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  messages["start_logging"]}, status.HTTP_406_NOT_ACCEPTABLE)
        dataframe = pd.read_csv(config.logger.local_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
        dataframe = dfpre.apply(dataframe)
        accounts = len(dataframe['ACCOUNT'].unique())
        job_id_numbers = len(dataframe['JOBID'].unique())
        min_time = dataframe['CURRENT_TIMESTAMP'].min()
        max_time = dataframe['CURRENT_TIMESTAMP'].max()
        return response_json({
            "msg":  messages["success"],
            "accounts": accounts,
            "job_id_numbers": job_id_numbers,
            "min_time": min_time,
            "max_time": max_time
            },
            status.HTTP_200_OK)
    except Exception as e:
        print("log-> start_logging: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)





