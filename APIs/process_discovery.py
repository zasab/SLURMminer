from flask import Flask, render_template, request, Blueprint, Response
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
import general.model_generator as mg
import pandas as pd
import base64

from PIL import Image
import PIL
import glob

discovery = Blueprint('discovery', __name__)
SEP = "\t"
ST_LIST = ["PD", "R", "CG", "BF", "CA", "CD", "CF", "DL", "F", "NF", "OOM", "RR", "RD", "RF", "RH", "RQ", "RS", "RV", "SI", "SE", "SO", "ST", "S", "TO"]

def validate_noise(noise_threshold):
    if noise_threshold.isnumeric():
        return True
    elif '.' in noise_threshold:
        noise_threshold_array = noise_threshold.split('.')
        return noise_threshold_array[0].isnumeric() and noise_threshold_array[1].isnumeric()
    else:
        return False

@discovery.route("/discover_model", methods = ["POST", "GET"])
def discover_model():
    try:
        data = create_data(request)
        print()
        print("data: ", data)

        if not os.path.exists(config.logger.normal_log):
            return response_json({"error":  "The normal event log does not exist. First generate normal log."}, status.HTTP_406_NOT_ACCEPTABLE)

        dataframe = pd.read_csv(config.logger.normal_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)

        if 'selected_topic' in data:
            selected_topic = data['selected_topic'].strip()
            if selected_topic == 'no topic is selected.':
                return response_json({"error":  "Please select a topic from list of projects."}, status.HTTP_406_NOT_ACCEPTABLE)
        
            noise_threshold = data['noise_threshold'].strip()
            if not validate_noise(noise_threshold):
                return response_json({"error":  "Invalid value for noise threshold."}, status.HTTP_406_NOT_ACCEPTABLE)
            else:
                noise_threshold = float(noise_threshold)

            
            projects = pd.read_csv(config.logger.project_ID_topic, sep=SEP, error_bad_lines=False)
            new_projects_df = projects[projects['topic'] == selected_topic]
            account_names_array = list(new_projects_df['project ID'].unique())
        
            accounts_list = []
            for account_name in account_names_array:
                if len(account_name)>0 and account_name not in dataframe['ACCOUNT'].unique():
                    pass
                else:
                    accounts_list.append(account_name)

            all_users = ', '.join(account_names_array)

            if len(accounts_list) == 0:
                return response_json({"error":  "Among the list of {0} users, of \"{1}\" project, no one is appeared in the extracted event log.".format(all_users, selected_topic)}, status.HTTP_406_NOT_ACCEPTABLE)
        else:
            selected_topic = ""
            noise_threshold = 0.2
            account_names_str = data['account'].strip()
            account_names_array = account_names_str.split(',')
            accounts_list = []
            for account_name in account_names_array:
                striped_name = account_name.strip()
                if len(striped_name)>0 and striped_name not in dataframe['ACCOUNT'].unique():
                    return response_json({"error":  "{0} user, not found.".format(striped_name)}, status.HTTP_404_NOT_FOUND)
                else:
                    accounts_list.append(striped_name)

        account_df = dataframe[dataframe['ACCOUNT'].isin(accounts_list)]
        account_df2 = account_df[account_df['ST'].isin(['R'])]
        if account_df2.shape[0] == 0:
            return response_json({"error":  "There is no RUNNING job for this user in the log. The model does not make sense."}, status.HTTP_406_NOT_ACCEPTABLE)

        models_info = mg.apply(account_df, accounts_list, noise_threshold)

        cc_model_image = open(models_info['cc_model'], "rb")
        enc_cc_model = base64.b64encode(cc_model_image.read())
        dec_cc_model = enc_cc_model.decode()

        ag_model_image = open(models_info['ag_model'], "rb")
        enc_ag_model = base64.b64encode(ag_model_image.read())
        dec_ag_model = enc_ag_model.decode()

        return response_json({
            "msg":  messages["success"],
            "recorded_users": 'Among the list of '+', '.join(account_names_array)+' user/users' + ', for \"{0}\" project, '.format(selected_topic)+ ' the discovered model belongs to '+', '.join(accounts_list) +' user/users' if len(selected_topic) > 0 else "",
            "cc_model": dec_cc_model,
            "cc_fitness": models_info['cc_fitness'],
            "ag_model": dec_ag_model,
            "ag_fitness": models_info['ag_fitness'],
            },
        status.HTTP_200_OK)              
    except Exception as e:
        print("log-> discover_model: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)


@discovery.route("/discover_jobid_ST_model", methods = ["POST", "GET"])
def discover_jobid_ST_model():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        if not os.path.exists(config.logger.local_log):
            return response_json({"error":  "The normal event log does not exist. First generate normal log."}, status.HTTP_406_NOT_ACCEPTABLE)
            
        dataframe = pd.read_csv(config.logger.local_log, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
        smaller_df = dataframe[dataframe["ST"].isin(ST_LIST)]
        models_info = mg.apply(smaller_df, '__all__', 0.2)

        freq_model_image = open(models_info['freq_model'], "rb")
        enc_freq_model = base64.b64encode(freq_model_image.read())
        dec_freq_model = enc_freq_model.decode()

        perf_model_image = open(models_info['perf_model'], "rb")
        enc_perf_model = base64.b64encode(perf_model_image.read())
        dec_perf_model = enc_perf_model.decode()

        return response_json({
            "msg":  messages["success"],
            "freq_model": dec_freq_model,
            "pref_model": dec_perf_model,
            },
        status.HTTP_200_OK)              
    except Exception as e:
        print("log-> discover_jobid_ST_model: EXCEPTION " + " \n [" + str(e) + "]")
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)