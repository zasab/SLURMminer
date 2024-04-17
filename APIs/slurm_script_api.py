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


slurm_script_manager = Blueprint('slurm_script_manager', __name__)

import networkx as nx

def create_dag(nodes, arcs):
    G = nx.DiGraph()

    # Create a set to store all nodes that are targets in arcs
    nodes_with_arcs = set()
    for arc in arcs:
        nodes_with_arcs.add(arc.target)
        nodes_with_arcs.add(arc.source)

    # Add nodes and arcs that are connected to each other
    for arc in arcs:
        # If both source and target of an arc are in the nodes_with_arcs set, add them to the graph
        if arc.source in nodes_with_arcs and arc.target in nodes_with_arcs:
            G.add_edge(arc.source, arc.target)

    # Remove isolated nodes from the graph
    G.remove_nodes_from(list(nx.isolates(G)))

    return G




@slurm_script_manager.route("/generate_slurm_script_from_files", methods = ["POST", "GET"])
def generate_slurm_script_from_files():
    try:
        if request.files:
            files = request.files
            if 'bpmn_file' in files and 'script_folder_zip' in files:
                bpmn_file = files["bpmn_file"]
                script_folder_zip = files["script_folder_zip"]
                bpmn_file_path = storageprocessor.save_file(bpmn_file, config.bpmn.uploaded_files_directory)
                script_folder_zip_path = storageprocessor.save_file(script_folder_zip, config.bpmn.uploaded_files_directory)

                should_be_uploaded_list = SLURMprocessor.create_runable_files(bpmn_file_path)
                nodes = should_be_uploaded_list.__dict__['_BPMN__nodes']
                arcs = should_be_uploaded_list.__dict__['_BPMN__flows']
                dag = create_dag(nodes, arcs)
                storageprocessor.save_dag(dag)



                # remoteserver_info = {
                #     "serverhost": config.remoteserver.serverhost,
                #     "username": config.remoteserver.username, 
                #     "password": config.remoteserver.password
                # }
                # bpmn_info = {
                #     "filepath": bpmn_file_path,
                #     "directorypath": config.bpmn.uploaded_files_directory
                # }
                # should_be_uploaded_list = main.create_runable_files(bpmn_info, local_exe_filename, remoteserver_info, script_folder_name)
                # should_be_uploaded_list.append(scripts_dir_path)
                # should_be_uploaded_list.append(basedir + "/general/wrap_time.sh")
                # main.upload_and_run_exefile_on_SLURM(local_exe_filename, remoteserver_info, should_be_uploaded_list, script_folder_zip.filename)
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
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)