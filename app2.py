import os
import sys
import threading
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
from APIs.remote_connection_api import connection as remote_connection_blueprint
import warnings
warnings.simplefilter("ignore")
import os

def create_app():
    app = Flask(__name__)
    app.register_blueprint(navigation_blueprint)
    app.register_blueprint(slurm_script_blueprint)
    app.register_blueprint(remote_connection_blueprint)
    return app

def manage_threads():
    # Placeholder for your thread creation logic
    threads = []

    def example_thread():
        print("Thread starting")
        # Simulate a long-running process
        import time
        time.sleep(5)
        print("Thread finishing")

    # Create and start threads
    for _ in range(5):  # Adjust the range as needed
        thread = threading.Thread(target=example_thread)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    manage_threads()  # Ensure all threads complete before starting the server
    app = create_app()
    app.run(host=config.general.localhost, port=config.general.port, debug=True)
