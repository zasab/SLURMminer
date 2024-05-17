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

import configparser
import platform

configFilePath = filedir + '/config.ini'
Config = configparser.ConfigParser()
Config.read(configFilePath)

class Property(object):
    pass

general = Property()
general.port = Config.get('GENERAL', 'port').strip()
general.localhost = Config.get('GENERAL', 'localhost').strip()
general.wrap_time_file = filedir + '/wrap_time.sh'
if 'Linux' in platform.system():
    general.python_path = '/usr/bin/python3.8'
elif 'Windows' in platform.system():
    general.python_path = 'C:\Python310\python.exe'


logger = Property()
if not os.path.exists(os.path.join(filedir , 'slurm-log')):
    os.mkdir(os.path.join(filedir , 'slurm-log'))
logger.local_log = os.path.join(filedir , 'slurm-log', Config.get('LOGGER', 'local_log').strip())
logger.normal_log = os.path.join(filedir , 'slurm-log', Config.get('LOGGER', 'normal_log').strip())

remoteserver = Property()
remoteserver.serverhost = Config.get('SERVER', 'serverhost').strip()
remoteserver.username = Config.get('SERVER', 'username').strip()
remoteserver.password = Config.get('SERVER', 'password').strip()
remoteserver.REMOTE_FOLDER_NAME = Config.get('SERVER', 'REMOTE_FOLDER_NAME').strip()
remoteserver.REMOTE_PATH_HOME_FILE = os.path.join(filedir, Config.get('SERVER', 'REMOTE_PATH_HOME_FILE').strip())

bpmn = Property()
bpmn.ALLOWED_BPMN_EXTENTIONS = Config.get('BPMN', 'ALLOWED_BPMN_EXTENTIONS').strip()

hpc = Property()
hpc.hpc_files_directory = filedir + "/" + Config.get('HPC', 'hpc_files_directory').strip()