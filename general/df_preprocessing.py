import numpy as np
import json
import pandas as pd
import config

ST_LIST = ["PD", "R", "CG", "BF", "CA", "CD", "CF", "DL", "F", "NF", "OOM", "RR", "RD", "RF", "RH", "RQ", "RS", "RV", "SI", "SE", "SO", "ST", "S", "TO"]
SEP = "\t"

def apply(dataframe):
    dataframe = dataframe[~dataframe['COMMAND'].isin(['(null)'])]
    proccessed_command_list = []
    for x in dataframe['COMMAND']:
        proccessed_command_list.append(str(x).split('/')[-1])
    
    dataframe['PROCESSED_COMMAND'] = proccessed_command_list
    dataframe = dataframe[~dataframe['CURRENT_TIMESTAMP'].isin([np.nan])]
    dataframe = dataframe[dataframe["ST"].isin(ST_LIST)]

    return dataframe

def project_ID_topic_prep(file_path):
    f = open(file_path)
    data = json.load(f)
    whole_df = pd.DataFrame()
    for i in data:
        df = pd.DataFrame()
        project_ids = []
        titles = []
        contents = data[i]
        df['topic'] = [i] * len(contents)
        for j in contents:
            project_ids.append(j['project ID'])
            titles.append(j['title'])

        df['project ID'] = project_ids
        df['title'] = titles
        whole_df = whole_df.append(df, ignore_index=True)
    
    whole_df.to_csv(config.logger.project_ID_topic, sep=SEP, index=False)
    f.close()

    return whole_df

