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
from functions import SRunFactory_new
from functions import SBatchFactory
from functions import graphObject
from functions.graphObject import JOB
from functions import CommandsFactory
import warnings
warnings.filterwarnings("ignore")
import pm4py
import networkx as nx
import random
import string
import shutil



slurm_script_manager = Blueprint('slurm_script_manager', __name__)

@slurm_script_manager.route("/generate_slurm_script_from_files", methods = ["POST", "GET"])
def generate_slurm_script_from_files():
    try:
        if request.files:
            print()
            print()
            print("-----"*20)
            storageprocessor.remove_dir(config.bpmn.uploaded_files_directory)
            JOB.remove_all_jobs()
            should_be_uploaded_list = {}
            files = request.files
            if 'bpmn_file' in files and 'script_folder_zip' in files:
                bpmn_file = files["bpmn_file"]
                script_folder_zip = files["script_folder_zip"]
                bpmn_file_path = storageprocessor.save_file(bpmn_file, config.bpmn.uploaded_files_directory)
                storageprocessor.save_file(script_folder_zip, config.bpmn.uploaded_files_directory)
                preprocessed_processed_bpmn = SLURMprocessor.preprocessing_bpmn(bpmn_file_path)
                processed_bpmn = SLURMprocessor.postprocessing_bpmn(preprocessed_processed_bpmn)

                net, im, fm = pm4py.convert_to_petri_net(processed_bpmn)
                pm4py.view_petri_net(net, im, fm)
                # tree= pm4py.convert_to_process_tree(net, im, fm)
                # pm4py.view_process_tree(tree)
                depend_script, should_be_uploaded_list = graphObject.create(net, im, fm, processed_bpmn)
                SRunFactory_new.create(should_be_uploaded_list)
                sbatch_file_name = bpmn_file.filename.split('.')[0] + ".sh"
                sbatch_file_path = "{}/{}".format(config.bpmn.uploaded_files_directory, sbatch_file_name)
                should_be_uploaded_list.add(sbatch_file_path)
                sbatch_file = open(sbatch_file_path, 'w')
                main_CI = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

                SBatchFactory.create(sbatch_file, main_CI)
                CommandsFactory.create('run_commands.sh', sbatch_file_name, script_folder_zip.filename, should_be_uploaded_list)

                shutil.copy(config.hpc.squeue_logger_path, config.bpmn.uploaded_files_directory)

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