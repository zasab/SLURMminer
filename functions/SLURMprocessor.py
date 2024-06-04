import sys, os
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
from functions import bpmn_parser
from functions.graphObject import JOB
from pm4py.objects.bpmn.obj import BPMN
from functions import common_functions

def preprocessing_bpmn(bpmn_file_path):
    bpmn_graph = bpmn_parser.extract_bpmn_information(bpmn_file_path)
    print("extract_bpmn_information is finished....")
    pre_processed_bpmn = bpmn_parser.pre_processing(bpmn_graph)
    print("pre_processing is finished....")
    bpmn_graph_processed_conditions = bpmn_parser.process_conditions(pre_processed_bpmn)
    print("process_conditions is finished....")
    bpmn_graph_processed_single_value_arguments = bpmn_parser.process_single_value_arguments(bpmn_graph_processed_conditions)
    print("process_single_value_arguments is finished....")
    bpmn_graph_processed_explicit_loops = bpmn_parser.process_explicit_loops(bpmn_graph_processed_single_value_arguments)
    print("process_explicit_loops is finished....")
    bpmn_graph_processed_hidden_loops = bpmn_parser.process_hidden_loops(bpmn_graph_processed_explicit_loops)
    print("process_hidden_loops is finished....")

    return bpmn_graph_processed_hidden_loops

def postprocessing_bpmn(processed_bpmn):
    job_tasks = {job.get_task() for job in JOB.get_all_jobs()}
    _nodes = processed_bpmn.__dict__['_BPMN__nodes']
    for node in _nodes:
        if isinstance(node, BPMN.Task):
            if node not in job_tasks:
                job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(node))
                JOB(task=node, job_id=job_id)
                JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, node)

    return processed_bpmn

def find_connected_jobs():
    connected_jobs = {}

    print("step 1")
    for job in JOB.get_all_jobs():
        job_id = job.get_job_id()
        print("job_id: ", job_id)
        dependecy_script = job.get_dependency_script()
        print("dependecy_script: ", dependecy_script)
        if '--dependency=' not in dependecy_script:
            connected_jobs[job_id] = set()

    print("step 2", connected_jobs)
    for job in JOB.get_all_jobs():
        job_id = job.get_job_id()
        dependecy_script = job.get_dependency_script()
        if '--dependency=' not in dependecy_script:
            connected_jobs[job_id] = set()
        if '--dependency=' in dependecy_script:
            dependecy_parts = dependecy_script.split()
            for part in dependecy_parts:
                if '$job_id_' in part:
                    part_parts = part.split('$')
                    for smaller_part in part_parts:
                        if 'job_id_' in smaller_part:
                            stripped_job_id = smaller_part.replace(',','')
                            if stripped_job_id in connected_jobs:
                                connected_jobs[stripped_job_id].add(job_id)
                            else:
                                for conn_j in connected_jobs:
                                    if stripped_job_id in connected_jobs[conn_j]:
                                        connected_jobs[conn_j].add(job_id)
    
    print("step 3", connected_jobs)
    connected_jobs_list = list()        
    for key, values in connected_jobs.items():
        temp = list()
        temp.append(key)
        for value in values:
            temp.append(value)

        connected_jobs_list.append(temp)

    return connected_jobs_list