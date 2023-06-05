from flask import Blueprint, send_file
import os

homepage = Blueprint('homepage', __name__)

@homepage.route('/')
def index():
    return send_file(os.path.abspath('web/index.html'))