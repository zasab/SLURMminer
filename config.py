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
import shutil
import platform

configFilePath = filedir + '/config.ini'
Config = configparser.ConfigParser()
Config.read(configFilePath)

class Property(object):
    pass

general = Property()
general.port = Config.get('GENERAL', 'port').strip()
general.localhost = Config.get('GENERAL', 'localhost').strip()
if 'Linux' in platform.system():
    general.python_path = '/usr/bin/python3.8'
elif 'Windows' in platform.system():
    general.python_path = 'C:\Python310\python.exe'
if not os.path.exists(os.path.join(filedir , 'models')):
    os.mkdir(os.path.join(filedir , 'models'))
general.models_dir = os.path.join(filedir , 'models')

remoteserver = Property()
# remoteserver.serverhost = Config.get('SERVER', 'serverhost').strip()


logger = Property()
if not os.path.exists(os.path.join(filedir , 'slurm-log')):
    os.mkdir(os.path.join(filedir , 'slurm-log'))
logger.local_log = os.path.join(filedir , 'slurm-log', Config.get('LOGGER', 'local_log').strip())
logger.normal_log = os.path.join(filedir , 'slurm-log', Config.get('LOGGER', 'normal_log').strip())
logger.ocel_log = os.path.join(filedir , 'slurm-log', Config.get('LOGGER', 'ocel_log').strip())
logger.project_ID_topic = os.path.join(filedir , Config.get('LOGGER', 'project_ID_topic').strip())
logger.project_ID_topic_json = os.path.join(filedir , Config.get('LOGGER', 'project_ID_topic_json').strip())
