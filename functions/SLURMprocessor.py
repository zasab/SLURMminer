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
    _flows = processed_bpmn.__dict__['_BPMN__flows']
    
    for node in _nodes:
        if isinstance(node, BPMN.Task):
            if node not in job_tasks:
                job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(node))
                JOB(task=node, job_id=job_id)
                JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, node)

    # TODO
    for __flow in _flows.copy():
        if __flow.source in _nodes and __flow.target in _nodes:
            pass
        else:
            processed_bpmn.remove_flow(__flow)
            

    return processed_bpmn