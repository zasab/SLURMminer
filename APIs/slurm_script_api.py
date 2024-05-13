import os, sys
if getattr(sys, 'frozen', False):
    filedir = os.path.dirname(sys.executable)
elif __file__:
    filedir = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(os.path.dirname(sys.executable))
elif __file__:
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from flask import Blueprint
import config
from flask_api import status
from server.response import *
from server.request import *
from server.error_messages import messages
from functions import storageprocessor
from functions import SLURMprocessor
from functions import SRunFactory
import warnings
warnings.filterwarnings("ignore")
import networkx as nx
import pm4py
from pm4py.algo.simulation.playout.petri_net.variants import basic_playout, extensive
import networkx as nx
from pm4py.objects.petri_net.obj import PetriNet, Marking
import re
import hashlib
import ast


slurm_script_manager = Blueprint('slurm_script_manager', __name__)

def hash_to_4_digit_number(input_string):
    # Hash the input string using SHA-256
    hashed = hashlib.sha256(input_string.encode()).hexdigest()
    
    # Take the first 4 characters of the hashed string
    first_4_chars = hashed[:4]
    # Convert hexadecimal string to decimal integer
    decimal_number = int(first_4_chars, 16)
    
    # Take modulo to ensure it's within the range of 4-digit numbers (0000 to 9999)
    four_digit_number = decimal_number % 10000
    
    return four_digit_number

def get_transition(net, node):
    for tran in net.transitions:
        if tran.label == node:
            return tran
        else:
            continue

def find_runs(net, im, fm):
    sequences = basic_playout.apply(net, im, fm)
    runs = []
    for trace in sequences: 
        trace_set = {event['concept:name'] for event in trace}
        if trace_set not in runs:
            runs.append(trace_set)

    new_runs = {}
    for idx, run in enumerate(runs):
        new_run = set()
        for node in run:
            new_run.add(get_transition(net, node))
        
        new_runs[f"run_{idx}"] = new_run
    return new_runs

def return_targets(run, arc, out_arcs, edges,net):
    for arc2 in out_arcs:
        if arc2.target in run:
            new_edge = {'source': arc.source, 'target': arc2.target}
            edges.append(new_edge)
        else:
            for place in net.places:
                for in_arc in place.in_arcs:
                    if in_arc.source == arc2.target:
                        for out_arc in place.out_arcs:
                            return_targets(run, arc, place.out_arcs, edges, net)

def build_edges(net, run):
    edges = []
    arcs =  net.arcs
    for arc in arcs:
        if isinstance(arc.source, PetriNet.Transition) and arc.source in run:
            target_place = arc.target    
            out_arcs = target_place.out_arcs
            return_targets(run, arc, out_arcs, edges, net)

    return edges

def return_inputs(run, arc, in_arcs, inputs_dict ,net):
    for arc2 in in_arcs:
        source_tran = arc2.source
        if source_tran.label == None:
            # print("silent transition .........")
            for place in net.places:
                for out_arc in place.out_arcs:
                    if out_arc.target == source_tran:
                        for in_arc in place.in_arcs:
                            return_inputs(run, arc, place.in_arcs, inputs_dict, net)
        else:
            if source_tran in run:
                if arc.target in inputs_dict:
                    if source_tran not in inputs_dict[arc.target]:
                        inputs_dict[arc.target].append(arc2.source)
                    else:
                        continue
                else:
                    inputs_dict[arc.target] = [source_tran]

def inputs(net, run):
    inputs_dict = {}
    arcs =  net.arcs
    for arc in arcs:
        if isinstance(arc.target, PetriNet.Transition) and arc.target in run:
            source_place = arc.source    
            in_arcs = source_place.in_arcs
            if len(in_arcs) > 0:
                return_inputs(run, arc, in_arcs, inputs_dict, net)

    for task in run:
        if task not in inputs_dict:
            inputs_dict[task] = []

    return inputs_dict

def get_job_id_from_name(task):
    task_name = task.name
    task_name1 = task_name.replace(" ", "_")
    return str(hash_to_4_digit_number(task_name1))

def get_job_application_from_label(task):
    task_label = task.label
    command = task_label.split('.')[0] if '.' in task_label else task_label
    return command.replace(" ", "_")

def get_command_from_label(task):
    return task.label

def generate_dependency_script(runs, inputs_dict):
    processed_tasks = {}
    depend_script = {}
    job_ids = {}
    should_be_uploaded_list = set()
    for index, run in runs.items():
        run_inputs = inputs_dict[index]
        for task in run:
            if task in processed_tasks:
                old_inputs = processed_tasks[task]
                new_inputs = run_inputs[task]
                if set(old_inputs) != set(new_inputs):
                    # we found a task with different inputs
                    the_job_id = job_ids[task] 
                    dep_str = depend_script[the_job_id]
                    dep_str = dep_str.replace('afterok','afterany')
                    for n_input in new_inputs:
                        if n_input not in processed_tasks:
                            add_dependency(n_input, run_inputs, depend_script, job_ids, processed_tasks, [], should_be_uploaded_list)
                        
                    new_input_job_ids = [job_ids[e_in] for e_in in new_inputs]
                    
                    old_job_ids, old_job_ids_str =  extract_text_between_parentheses(dep_str)

                    new_job_ids_str = str(tuple(zip(new_input_job_ids, old_job_ids)))
                    new_dep_str = dep_str.replace(old_job_ids_str, new_job_ids_str)
                    depend_script[the_job_id] = new_dep_str          
            else:
                add_dependency(task, run_inputs, depend_script, job_ids, processed_tasks, [], should_be_uploaded_list)

    return depend_script, should_be_uploaded_list

def extract_text_between_parentheses(text):
    # Use regular expression to find text between parentheses
    matches = re.findall(r'\((.*?)\)', text)
    elements = [elem.strip() for match in matches for elem in match.split(',')]
    return elements, "(" + matches[0] + ")"

def add_dependency(task, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list):
    # based on the name of the application needs to be run on SLURM and the task id we generate a unique a name for our bash file
    # that contains srun and parameter settings
    srun_file_name = get_job_id_from_name(task) + "_" + get_job_application_from_label(task) + '.sh'
    SRunFactory.create(srun_file_name, get_command_from_label(task), should_be_uploaded_list)
    # we also need a job id that refers to srun file in our sbatch file
    job_id = 'job_id_' + str(get_job_id_from_name(task))

    if job_id not in job_ids:
        job_ids[task] = job_id

    if not run_inputs[task]: # no dependency
        depend_script[job_id] = str(srun_file_name)
        processed_tasks[task] = run_inputs[task]
        j_dep_list = []
    elif len(run_inputs[task]) == 1:  # single dependency
        y = run_inputs[task][0]
        if y not in job_ids:
            j_dep_list = []
            add_dependency(y, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list)

        j_y = job_ids[y]
        depend_script[job_id] = f"--dependency:afterok({j_y}) {srun_file_name}"
        processed_tasks[task] = run_inputs[task]

    else:  # multiple dependencies
        for input in run_inputs[task]:
            if input not in job_ids:
                add_dependency(input, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list)

            processed_tasks[task] = run_inputs[task]
            j_dep_list.append(job_ids[input])

        depend_script[job_id] = f"--dependency:afterok({','.join(j_dep_list)}) {srun_file_name}"

@slurm_script_manager.route("/generate_slurm_script_from_files", methods = ["POST", "GET"])
def generate_slurm_script_from_files():
    try:
        if request.files:
            files = request.files
            if 'bpmn_file' in files and 'script_folder_zip' in files:
                bpmn_file = files["bpmn_file"]
                script_folder_zip = files["script_folder_zip"]
                storageprocessor.remove_dir(config.bpmn.uploaded_files_directory)
                bpmn_file_path = storageprocessor.save_file(bpmn_file, config.bpmn.uploaded_files_directory)
                script_folder_zip_path = storageprocessor.save_file(script_folder_zip, config.bpmn.uploaded_files_directory)

                processed_bpmn = SLURMprocessor.preprocessing_bpmn(bpmn_file_path)
                net, im, fm = pm4py.convert_to_petri_net(processed_bpmn)
                # pm4py.view_petri_net(net, im, fm)
                runs = find_runs(net, im, fm)
                all_inputs_dict = {}
                for index, run in runs.items():
                    edges = build_edges(net, run)
                    inputs_dict = inputs(net, run)
                    all_inputs_dict[index] = inputs_dict
                    # dag = storageprocessor.create_dag(edges)
                    # storageprocessor.save_dag(dag)

                depend_script, should_be_uploaded_list = generate_dependency_script(runs, all_inputs_dict)
                # print('----'*20)
                # for job_id_script in depend_script:
                #     print()
                #     print("job id: ", job_id_script)
                #     print("dep script: ", depend_script[job_id_script])
                # print('----'*20)
                # print()
                # for file in should_be_uploaded_list:
                #     print(file + "\n")

                return response_json({
                    "msg":  messages["success"],
                    "slurmDAG": ""
                    },
                status.HTTP_200_OK)
            else:
                return response_json({"error":  messages["required_files_not_found"]},
                status.HTTP_404_NOT_FOUND)
        else:
             return response_json({"error":  messages["required_files_not_found"]},
                status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)