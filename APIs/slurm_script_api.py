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
import warnings
warnings.filterwarnings("ignore")
import networkx as nx
import pm4py
from pm4py.algo.simulation.playout.petri_net.variants import basic_playout, extensive
import networkx as nx
from pm4py.objects.petri_net.obj import PetriNet, Marking


slurm_script_manager = Blueprint('slurm_script_manager', __name__)

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

    new_runs = []
    for run in runs:
        new_run = set()
        for node in run:
            new_run.add(get_transition(net, node))
        
        new_runs.append(new_run)
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

    for edge in edges:
        print(edge)

    return edges


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
                pm4py.view_petri_net(net, im, fm)
                runs = find_runs(net, im, fm)

                for run in runs:
                    edges = build_edges(net, run)
                    dag = storageprocessor.create_dag(edges)
                    storageprocessor.save_dag(dag)

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