from flask import Flask, send_file
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
from APIs.homepage import homepage as homepage_blueprint
from APIs.log import log as log_blueprint
from APIs.slurm_log_analysis import sloga as sla_blueprint
from APIs.process_discovery import discovery as discovery_blueprint
import config
from flask_cors import CORS


def create_app():
    static_file_path = filedir + '/web/assets'
    template_path = filedir + '/web'

    app = Flask(__name__,
            static_folder= static_file_path,
            template_folder= template_path)

    CORS(app)
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.register_blueprint(homepage_blueprint)
    app.register_blueprint(log_blueprint)
    app.register_blueprint(sla_blueprint)
    app.register_blueprint(discovery_blueprint)

    @app.route("/", defaults={'path':""})
    @app.route('/<path:path>')
    def catch_all(path):
        return send_file(os.path.abspath('web/index.html'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host = config.general.localhost, port = config.general.port, debug=True)