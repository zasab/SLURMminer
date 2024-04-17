from flask import Blueprint, render_template
import random

navigation = Blueprint('navigation', __name__)

@navigation.route('/')
def index():
    return render_template("homepage.html")

@navigation.route('/homepage')
def e():
    return render_template("homepage.html")

@navigation.route('/logging')
def logging():
    return render_template("logging_table.html")