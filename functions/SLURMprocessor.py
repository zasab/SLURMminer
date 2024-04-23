import sys, os
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
# from werkzeug.utils import secure_filename
from functions import bpmn_parser
# import random
from functions import SRunFactory
from functions import SBatchFactory
# from functions import ssh_connection
# import pysftp
# import config
# from functions.file_management import get_value

def preprocessing_bpmn(bpmn_file_path):
    file_name = os.path.basename(bpmn_file_path)
    bpmn_graph = bpmn_parser.extract_bpmn_information(bpmn_file_path)
    pre_processed_bpmn = bpmn_parser.pre_processing(bpmn_graph)
    bpmn_graph_processed_explicit_loops = bpmn_parser.process_explicit_loops(pre_processed_bpmn)
    bpmn_graph_processed_hidden_loops = bpmn_parser.process_hidden_loops(bpmn_graph_processed_explicit_loops)
    # SRunFactory.create(bpmn_graph_processed_explicit_loops)
    # SBatchFactory.create(processed_bpmn, should_be_uploaded_list, bpmn_info, local_exe_filename, remoteserver_info)
    # SBatchFactory.create(bpmn_graph_processed_explicit_loops)
    return bpmn_graph_processed_hidden_loops

# def upload_and_run_exefile_on_SLURM(local_exe_filename, remoteserver_info, should_be_uploaded_list, script_folder_zip):
#     try:
#         REMOTE_FOLDER_NAME = config.remoteserver.REMOTE_FOLDER_NAME
#         HOST_SERVER = remoteserver_info['serverhost']
#         USERNAME_RWTH = remoteserver_info['username']
#         PASSWORD_PATH = remoteserver_info['password']
#         LOCAL_RUNNABLE_FILE_PATH = should_be_uploaded_list[-1]
#         cnopts = pysftp.CnOpts()
#         cnopts.hostkeys = None
#         srv = ssh_connection.My_Connection(host=HOST_SERVER, username= USERNAME_RWTH, 
#         password= PASSWORD_PATH , cnopts=cnopts)

#         ssh1 = ssh_connection.get_ssh_client(HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH)
#         ssh_stdin0, ssh_stdout0, ssh_stderr0 = ssh1.exec_command("mkdir {}".format(REMOTE_FOLDER_NAME))

#         with srv.cd('{}/'.format(REMOTE_FOLDER_NAME)):
#             srv.put(LOCAL_RUNNABLE_FILE_PATH)
#             for i in range(len(should_be_uploaded_list)-1):
#                 srv.put(should_be_uploaded_list[i])

            
#         srv.close()

#         REMOTE_RUNABLE_FILENAME = local_exe_filename
#         print("****"*20)
#         print("REMOTE_FOLDER_NAME: ", REMOTE_FOLDER_NAME)
#         for uploaded_file in should_be_uploaded_list:
#             uploaded_file_name = uploaded_file.split('/')[-1]
#             ssh_stdin, ssh_stdout, ssh_stderr = ssh1.exec_command("cd {}/ && chmod +x {}".format(REMOTE_FOLDER_NAME, uploaded_file_name))
#             print(ssh_stdout.read().decode())
#         ssh_stdin0, ssh_stdout0, ssh_stderr0 = ssh1.exec_command("dos2unix {}/*".format(REMOTE_FOLDER_NAME))
#         # do not remove this print line
#         print(ssh_stdout0.read().decode())
#         ssh_stdin1, ssh_stdout1, ssh_stderr1 = ssh1.exec_command("cd {}/ && unzip -o {}".format(REMOTE_FOLDER_NAME, script_folder_zip))
#         print(ssh_stdout1.read().decode())
#         ssh_stdin2, ssh_stdout2, ssh_stderr2 = ssh1.exec_command("cd {}/ && chmod +x {}/{}".format(REMOTE_FOLDER_NAME, str(script_folder_zip).split('.')[0], '*'))
#         print(ssh_stdout2.read().decode())
#         ssh_stdin3, ssh_stdout3, ssh_stderr3 = ssh1.exec_command("cd {}/ && dos2unix {}".format(REMOTE_FOLDER_NAME, REMOTE_RUNABLE_FILENAME))
#         print(ssh_stdout3.read().decode())
#         ssh_stdin4, ssh_stdout4, ssh_stderr4 = ssh1.exec_command("cd {}/ && chmod +x {}".format(REMOTE_FOLDER_NAME, REMOTE_RUNABLE_FILENAME))
#         print(ssh_stdout4.read().decode())
#         ssh_stdin5, ssh_stdout5, ssh_stderr5 = ssh1.exec_command("cd {}/ && ./{}".format(REMOTE_FOLDER_NAME, REMOTE_RUNABLE_FILENAME))

#     except Exception as e:
#         print(e)