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
import config
from flask import Flask
from APIs.navigations import navigation as navigation_blueprint
from APIs.slurm_script_api import slurm_script_manager as slurm_script_blueprint
import warnings
warnings.simplefilter("ignore")
import os

def create_app():
    app = Flask(__name__)
    app.register_blueprint(navigation_blueprint)
    app.register_blueprint(slurm_script_blueprint)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host = config.general.localhost, port = config.general.port, debug=True)