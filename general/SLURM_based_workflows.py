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
import networkx as nx
import re

def add_important_part_of_command_as_a_column(df):
    commands = []
    for command in df['COMMAND'].tolist():
        command_without_argus = command.split(' ')
        command_list = command_without_argus[0].split('/') 
        commands.append(command_list[-1])
    
    df['PROCESSED_COMMAND'] = commands

def connected_components(node, JOBID_dict, finished, pending):
    if node not in finished:
        finished.append(node)
    
    for key, val in JOBID_dict.items():
        if node == key or node in val:
            if key not in finished and key not in pending:
                pending.append(key)
            if node in JOBID_dict and len(JOBID_dict[node]) > 0:
                for c_node in JOBID_dict[node]:
                    if c_node not in finished and c_node not in pending:
                        pending.append(c_node)    

    for connected_node in pending:
        pending.remove(connected_node)
        return connected_components(connected_node, JOBID_dict, finished, pending)

def original_log_as_list(df):
    original_log = list()
    columns = df.columns.tolist()
    vv = df.values.tolist()
    for row in vv:
        row_dict = dict()
        for element_index in range(len(row)):
            row_dict[columns[element_index]] = row[element_index]

        original_log.append(row_dict)
    
    return original_log

def find_connected_job_ids(original_log):
    JOBID_dict = dict()
    for record in original_log:
        if record['ST'] == 'PD':          
            if record['DEPENDENCY'] != '(null)' and 'unfulfilled' in str(record['DEPENDENCY']):
                dependency_list = str(record['DEPENDENCY']).split(",")
                dependency_list2 = list()
                
                for dependency in dependency_list:
                    start_index =  dependency.index(':') + 1
                    end_index = dependency.find("(unfulfilled)")
                    dependency_list2.append(dependency[start_index:end_index])
                JOBID_dict[str(record['JOBID'])] = dependency_list2
            else:
                JOBID_dict[str(record['JOBID'])] = []
    
    jobid_caseid_dict = dict()
    
    for job_id in JOBID_dict:
        finished = []
        connected_components(job_id, JOBID_dict, finished, [])
        job_cluster = sorted(finished)
        case_id = '____'.join(job_cluster)
        jobid_caseid_dict[job_id] = case_id

    
    return jobid_caseid_dict

def SLURM_base_connected_components(df):
    original_log = original_log_as_list(df)
    jobid_connected_caseid_dict = find_connected_job_ids(original_log)
    
    sequences_of_caseids = list()
    for log_row in original_log:
        if str(log_row['JOBID']) in jobid_connected_caseid_dict:
            log_row['DEPENDENCY-BASED-CASE-ID'] = jobid_connected_caseid_dict[str(log_row['JOBID'])]
            sequences_of_caseids.append(log_row['DEPENDENCY-BASED-CASE-ID'])
        else:
            log_row['DEPENDENCY-BASED-CASE-ID'] = str(log_row['JOBID'])
            sequences_of_caseids.append(log_row['DEPENDENCY-BASED-CASE-ID'])

    df['DEPENDENCY-BASED-CASE-ID'] = sequences_of_caseids


def SLURM_base_connected_components2(dataframe):
    dataframe["DEPENDENCY"] = dataframe["DEPENDENCY"].replace("(null)", None)
    dataframe["DEPENDENCY"] = dataframe["DEPENDENCY"].apply(lambda x: f(x))

    job_dep = dataframe.dropna(subset=["DEPENDENCY"])[["JOBID", "DEPENDENCY"]].to_dict("records")

    job_dep = {str(x["JOBID"]): x["DEPENDENCY"] for x in job_dep}
    G = nx.Graph()
    for k, v in job_dep.items():
        v_list = v.split('@@')
        for dep_v in v_list:
            G.add_edge(k, dep_v)

    conn = list(nx.connected_components(G))
    conn_dict = {}
    for i in range(len(conn)):
        for el in conn[i]:
            conn_dict[int(el)] = str(i)
            
    dataframe["DEPENDENCY-BASED-CASE-ID"] = dataframe["JOBID"].map(conn_dict).fillna(dataframe["JOBID"])

def f(x):
    try:
        lst = re.findall(r'\d+', x)
        if lst:
            return '@@'.join(lst)
    except:
        pass
    return None
    