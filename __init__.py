import json

import flask

from flask import Flask
from flask import render_template

import httplib2

# from apiclient import discovery
from oauth2client import client

import datetime

import main

app = flask.Flask(__name__)

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

@app.route('/pledge')
def pledge():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('pledge.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/basement')
def basement():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('basement.html')
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
    return main.pledge(http_auth,flask.request.json)

@app.route('/basement/number', methods=["GET"])
def basementGetPeople():
  people=main.basementGetPeople()
  return json.dumps({"people":people})

@app.route('/basement/add', methods=["GET"])
def basementAddPerson():
  people=main.basementAddPerson()
  return json.dumps({"people":people})

@app.route('/basement/subtract', methods=["GET"])
def basementSubtractPerson():
  people=main.basementSubtractPerson()
  return json.dumps({"people":people})

@app.route('/basement/clear', methods=["GET"])
def basementClear():
  people=main.basementClear()
  return json.dumps({"people":people})

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
    return main.getCalendars(http_auth)


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
