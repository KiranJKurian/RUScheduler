import json
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

app = CustomFlask(__name__)

development=False

if development:
  CLIENT_SECRETS='client_secrets.json'
else:
  CLIENT_SECRETS='/var/www/RUScheduler/client_secrets.json'


@app.route('/')
def index():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('index.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/demo')
def demo():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('demo.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route("/bower_components/<path:fileName>")
def load_bower(fileName):
    return send_from_directory("bower_components", fileName)

@app.route("/data/<path:fileName>")
def load_data(fileName):
    return send_from_directory("data", fileName)

@app.route('/pledge')
def pledge():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('pledge.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/brother')
def brother():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('brothers.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/party')
def party():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('party.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"
@app.route('/chegg')
def chegg():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('chegg.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

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
      # print postInfo[0]
      flask.session['name']=postInfo['id']
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      # webbrowser.open_new_tab(flask.url_for('oauth2callback'))
      postInfo=flask.request.json
      print postInfo
      # print postInfo[0]
      flask.session['name']=postInfo['id']
      return flask.redirect(flask.url_for('oauth2callback'))
    else:
      print "Credentials located"
      return json.dumps({"success":True, "url":None})
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})

# @app.route('/activate')
# def activate():
#   flow = client.flow_from_clientsecrets(
#       CLIENT_SECRETS,
#       scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
#       redirect_uri=flask.url_for('oauth2callback', _external=True))
#   if 'code' not in flask.request.args:
#     auth_uri = flow.step1_get_authorize_url()
#     return flask.redirect(flask.url_for(auth_uri))
#   else:
#     auth_code = flask.request.args.get('code')
#     credentials = flow.step2_exchange(auth_code)
#     flask.session['credentials'] = credentials.to_json()
#     return flask.redirect(flask.url_for('loggedIn'))

# @app.route('/oauth', methods=["GET"])
# def oauth():
#   flow = client.flow_from_clientsecrets(
#       CLIENT_SECRETS,
#       scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
#       redirect_uri=flask.url_for('oauth2callback', _external=True))
#   if 'code' not in flask.request.args:
#     auth_uri = flow.step1_get_authorize_url()
#     # webbrowser.open_new_tab(auth_uri)
#     return json.dumps({"success":True, "url":auth_uri})
#   else:
#     auth_code = flask.request.args.get('code')
#     credentials = flow.step2_exchange(auth_code)
#     flask.session['credentials'] = credentials.to_json()
#     return flask.redirect(flask.url_for('loggedIn'))

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

@app.route('/magicPledge', methods=["POST"])
def magicPledge():
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
    return main.addToCal(http_auth,flask.request.json)

@app.route('/magicBrother', methods=["POST"])
def magicBrother():
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
    return main.addToCal(http_auth,flask.request.json,"Phi Sig- Brothers Schedules")

@app.route('/party/number', methods=["GET"])
def partyGetPeople():
  people=main.partyGetPeople()
  return json.dumps({"people":people})

@app.route('/party/add', methods=["GET"])
def partyAddPerson():
  people=main.partyAddPerson()
  return json.dumps({"people":people})

@app.route('/party/subtract', methods=["GET"])
def partySubtractPerson():
  people=main.partySubtractPerson()
  return json.dumps({"people":people})

@app.route('/party/clear', methods=["GET"])
def partyClear():
  people=main.partyClear()
  return json.dumps({"people":people})

@app.route('/supervisor', methods=["GET"])
def supervisor():
  try:
    return render_template('supervisor.html')
  except:
    print "Cannot render template"
    return "Error with rendering template"

@app.route('/chegg/people', methods=["GET"])
def cheggGetPeople():
  people=main.cheggGetPeople()
  return json.dumps({"people":people})

@app.route('/chegg/add/<name>', methods=["GET"])
def cheggAddPerson(name):
  print "Post info:"
  print name
  people=main.cheggAddPerson(name)
  return json.dumps({"people":people})
  # people=main.cheggAddPerson()
  # return json.dumps({"people":people})

@app.route('/chegg/subtract/<name>', methods=["GET"])
def cheggSubtractPerson(name):
  people=main.cheggSubtractPerson(name)
  return json.dumps({"people":people})

@app.route('/chegg/clear', methods=["GET"])
def cheggClear():
  success=main.cheggClear()
  return json.dumps({"success":success})

@app.route('/getCalendars', methods=["GET"])
def getCalendars():
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
    return main.getCalendars(http_auth,["Rho Eta","Phi Sig- Brothers Schedules","ruphisigmakappa@gmail.com","Birthdays","Holidays in United States"])


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
