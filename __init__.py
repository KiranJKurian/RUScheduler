import json
import urllib2
import os

import flask

from flask import Flask, render_template, jsonify, send_from_directory

import httplib2

# from apiclient import discovery
from oauth2client import client

import datetime

import main

class CustomFlask(Flask):
  jinja_options = Flask.jinja_options.copy()
  jinja_options.update(dict(
    variable_start_string='{{{',
    variable_end_string='}}}',
  ))

app = CustomFlask(__name__, static_url_path='')

development = False

if development:
  CLIENT_SECRETS='client_secrets.json'
else:
  CLIENT_SECRETS='/var/www/RUScheduler/client_secrets.json'


@app.route('/old')
def index():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('index.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/', defaults={'hash': ""})
@app.route('/<hash>')
def demo(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('demo.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

# @app.route("/bower_components/<path:fileName>")
# def load_bower(fileName):
#     return send_from_directory(os.path.join(os.path.dirname(os.getcwd()),"bower_components"), fileName)

# @app.route("/data/<path:fileName>")
# def load_data(fileName):
#     return send_from_directory(os.path.join(os.path.dirname(os.getcwd()),"data"), fileName)

@app.route("/subject/<subject>")
def subjectJSON(subject):
  try:
    return urllib2.urlopen("http://sis.rutgers.edu/soc/courses.json?semester=92016&subject=%s&campus=NB&level=UG"%subject).read()
  except:
    return app.send_static_file('static/data/Courses/%s.json'%subject)

@app.route("/subjects")
def subjectsJSON():
  try:
    print "Getting subjects..."
    return urllib2.urlopen("https://sis.rutgers.edu/soc/subjects.json?semester=92016&campus=NB&level=U").read()
  except:
    return app.send_static_file('static/data/subjects.json')

@app.route('/faq')
def faq():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('faq.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/loggedIn')
def loggedIn():
    return """You are now authorized, go back to your other tab and add your classes!
      <script>localStorage.setItem('%s',true);
      function storage_handler(evt)
        {
          window.close();
        }

        window.addEventListener('storage', storage_handler, false);</script>"""%flask.session['name']

@app.route('/donate')
def donate():
    try:
        return render_template('donate.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/authorize', methods=["POST"])
def authorize():
  try:
    if 'credentials' not in flask.session:
      # webbrowser.open_new_tab(flask.url_for('oauth2callback'))
      postInfo=flask.request.json
      print postInfo
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      print "credentials expired"
      postInfo=flask.request.json
      print postInfo
      return flask.redirect(flask.url_for('oauth2callback'))
    else:
      print "Credentials located"
      return json.dumps({"success":True, "url":None})
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})

@app.route('/authorize/demo', methods=["POST"])
def authorizeDemo():
  # print flask.request.form
  # return "Fucker"
  postInfo = {"subject":flask.request.form["subject"],"course":flask.request.form["course"],"section":flask.request.form["section"],"reminders":flask.request.form["reminders"]}
  try:
    flask.session["initData"] = postInfo
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callbackDemo'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      return flask.redirect(flask.url_for('oauth2callbackDemo'))
    else:
      print "Credentials located"
      return flask.redirect(flask.url_for('demo'))
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})

@app.route('/oauth2callback/demo', methods=["GET"])
def oauth2callbackDemo():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callbackDemo', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    
    http_auth = credentials.authorize(httplib2.Http())
    result = main.classesDemo(http_auth, flask.session["initData"])

    flask.session.pop("initData",None)

    if result["success"]:
      return flask.redirect(flask.url_for("demo")+'#'+result["course"].replace(" ","+"))
    else:
      return flask.redirect(flask.url_for('demo#BadInput'))

@app.route('/addClass', methods=["POST"])
def addClass():
  print "Adding Classes..."
  data = flask.request.json
  print "Subject: %s\nCourse: %s\nSection: %s"%(int(data["subject"]),int(data["course"]),data["section"])
  print "Reminders: ",
  for reminder in data["reminders"]:
    print int(reminder),
  print "\n"
  # return "Fucker"

  if 'credentials' not in flask.session:
    print "Authorizing..."
    return flask.redirect(flask.url_for('oauth2callbackDemo'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    print "Credentials expired"
    flask.session.pop("credentials",None)
    return "Credentials expired"
  else:
    http_auth = credentials.authorize(httplib2.Http())
    print "Adding Classes now"
    return json.dumps( main.classesDemo(http_auth, data) )

@app.route('/loggedIn/demo', methods=["GET"])
def loggedInDemo():
  if 'credentials' not in flask.session:
    return json.dumps({"loggedIn":False})
  else if client.OAuth2Credentials.from_json(flask.session['credentials']).access_token_expired:
    return json.dumps({"loggedIn":False})
  else:
    return json.dumps({"loggedIn":True})

@app.route('/magic', methods=["POST"])
def magic():
  if 'credentials' not in flask.session:
    # webbrowser.open_new_tab(flask.url_for('oauth2callback'))
    return flask.redirect(flask.url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    # webbrowser.open_new_tab(flask.url_for('oauth2callback'))
    return flask.redirect(flask.url_for('oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    # service = discovery.build('calendar', 'v3', http_auth)
    return main.classes(http_auth,json.dumps(flask.request.json))

@app.route('/oauth2callback', methods=["GET"])
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return json.dumps({"success":True, "url":auth_uri})
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('loggedIn'))


@app.errorhandler(500)
def internal_error(error):

    return render_template('error.html',errorMessage="Oops, looks like something went wrong. Email kiran.kurian@rutgers.edu if this persists.")

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html',errorMessage="Congratulations, you hacked into the fourth dimension! Jk, but seriously, you're not supposed to be here"),404

if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = development 
  app.run()
