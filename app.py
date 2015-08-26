import os
from flask import Flask
from flask import render_template
import flask
from main import main
import json


app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/donate')
def donate():
    try:
        return render_template('donate.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/magic', methods=["POST"])
def magic():
    if flask.request.method=='POST':
        print "DATA:\n"
        print flask.request.json
        return main(json.dumps(flask.request.json))
    else:
        print "Didn't get a POST request..."


if __name__ == '__main__':
    app.run()