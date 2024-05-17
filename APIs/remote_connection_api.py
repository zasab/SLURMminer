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
from flask import jsonify, request, Blueprint
from server.response import *
from server.request import *
import config
from server.error_messages import messages
from functions import ssh_connection
from flask_api import status
from functions.file_management import save_value
SEP = "\t"
import warnings
warnings.filterwarnings("ignore")

connection = Blueprint('connection', __name__)

@connection.route('/check_connection', methods=['POST'])
def check_connection():
    try:
        data = create_data(request)
        print()
        print("data: ", data)
        servername = data['servername']
        username = data['username']
        password = data['password']
        two_factor_code = data['twofactor']
        two_factor_code_filepath = "{}/two_factor_code.key".format(config.hpc.hpc_files_directory)
        with open(two_factor_code_filepath, 'w') as file:
            file.write(two_factor_code)
        ssh = ssh_connection.get_ssh_client(servername, username, password, two_factor_code_filepath)
        stdin, stdout, stderr = ssh.exec_command('pwd')
        home_path = stdout.read().decode().strip()

        
        # save_value(home_path, config.remoteserver.REMOTE_PATH_HOME_FILE)
        return response_json({
                    "msg": 'Connection checked successfully!',
                    },
                status.HTTP_200_OK)
    except Exception as e:
        return response_json({"error":  messages["server_side_error"]}, status.HTTP_500_INTERNAL_SERVER_ERROR)