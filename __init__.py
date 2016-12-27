from flask import Flask, render_template, jsonify, send_from_directory
from oauth2client import client
from initData import semester
import json
import urllib2
import os
import flask
import httplib2
import datetime
import main

class CustomFlask(Flask):
  jinja_options = Flask.jinja_options.copy()
  jinja_options.update(dict(
    variable_start_string='{{{',
    variable_end_string='}}}',
  ))

app = CustomFlask(__name__, static_url_path='')

development = os.uname()[1] != "ruscheduler"

if development:
  CLIENT_SECRETS='client_secrets.json'
else:
  CLIENT_SECRETS='/var/www/RUScheduler/client_secrets.json'


# Version 3.0
@app.route('/', defaults={'hash': ""})
@app.route('/<hash>')
@app.route('/NB', defaults={'hash': ""})
@app.route('/NB/<hash>')
def indexNB(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('index.html',campus="NB")
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/NK', defaults={'hash': ""})
@app.route('/NK/<hash>')
def indexNK(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('index.html',campus="NK")
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/CM', defaults={'hash': ""})
@app.route('/CM/<hash>')
def indexCM(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('index.html',campus="CM")
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route("/subject/<subject>", defaults={'campus': "NB"})
@app.route("/subject/<subject>/<campus>")
def subjectJSON(subject,campus):
  try:
    return urllib2.urlopen("http://sis.rutgers.edu/soc/courses.json?semester=%s&subject=%s&campus=%s&level=UG"%(semester, subject,campus)).read()
  except:
    return app.send_static_file('static/data/Courses/%s.json'%subject)

@app.route('/subjects', defaults={'campus': "NB"})
@app.route('/subjects/<campus>')
def subjectsJSON(campus):
  try:
    print "Getting subjects..."
    return urllib2.urlopen("https://sis.rutgers.edu/soc/subjects.json?semester=%s&campus=%s&level=U"%(semester, campus)).read()
  except:
    return app.send_static_file('static/data/subjects.json')

@app.route('/authorize', methods=["POST"])
def authorize():
  # print flask.request.form
  # return "Fucker"
  postInfo = {"subject":flask.request.form["subject"],"course":flask.request.form["course"],"section":flask.request.form["section"],"reminders":flask.request.form["reminders"],"campus":flask.request.form["campus"]}
  try:
    flask.session["initData"] = postInfo
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      return flask.redirect(flask.url_for('oauth2callback'))
    else:
      print "Credentials located"
      return flask.redirect(flask.url_for('index'+postInfo['campus']))
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})

@app.route('/oauth2callback', methods=["GET"])
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()

    http_auth = credentials.authorize(httplib2.Http())
    result = main.classes(http_auth, flask.session["initData"])

    campus = flask.session["initData"]["campus"][::]

    flask.session.pop("initData",None)

    if "success" in result:
      return flask.redirect(flask.url_for("index"+campus)+'#'+result["course"].replace(" ","+"))
    else:
      return flask.redirect(flask.url_for('index'+campus)+"#BadInput")

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
    return flask.redirect(flask.url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    print "Credentials expired"
    flask.session.pop("credentials",None)
    return "Credentials expired"
  else:
    http_auth = credentials.authorize(httplib2.Http())
    print "Adding Classes now"
    return json.dumps( main.classes(http_auth, data) )

@app.route('/loggedIn', methods=["GET"])
def loggedIn():
  if 'credentials' not in flask.session:
    return json.dumps({"loggedIn":False})
  elif client.OAuth2Credentials.from_json(flask.session['credentials']).access_token_expired:
    return json.dumps({"loggedIn":False})
  else:
    return json.dumps({"loggedIn":True})


#Version 2.0 - Depreciated
@app.route('/old')
def old():
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('old.html')
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

@app.route('/loggedIn/old')
def loggedInOld():
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

@app.route('/authorize/old', methods=["POST"])
def authorizeOld():
  try:
    if 'credentials' not in flask.session:
      postInfo=flask.request.json
      print postInfo
      flask.session['name']=postInfo['id']
      return flask.redirect(flask.url_for('oauth2callbackOld'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      postInfo=flask.request.json
      print postInfo
      flask.session['name']=postInfo['id']
      return flask.redirect(flask.url_for('oauth2callbackOld'))
    else:
      print "Credentials located"
      return json.dumps({"success":True, "url":None})
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})

@app.route('/magic', methods=["POST"])
def magic():
  if 'credentials' not in flask.session:
    return flask.redirect(flask.url_for('oauth2callbackOld'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return flask.redirect(flask.url_for('oauth2callbackOld'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    # service = discovery.build('calendar', 'v3', http_auth)
    return main.classesOld(http_auth,json.dumps(flask.request.json))

@app.route('/oauth2callback/old', methods=["GET"])
def oauth2callbackOld():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callbackOld', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return json.dumps({"success":True, "url":auth_uri})
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('loggedInOld'))


# Brothers
@app.route('/brother', defaults={'hash': ""})
@app.route('/brother/<hash>')
def brother(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('brother.html',campus="NB")
    except:
        print "Cannot render template"
        return "Error with rendering template"
@app.route('/authorize/brother', methods=["POST"])
def authorizeBrother():
  # print flask.request.form
  # return "Fucker"
  postInfo = {"name":flask.request.form["name"],"subject":flask.request.form["subject"],"course":flask.request.form["course"],"section":flask.request.form["section"],"reminders":flask.request.form["reminders"],"campus":flask.request.form["campus"]}
  try:
    flask.session["initData"] = postInfo
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callbackBrother'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      return flask.redirect(flask.url_for('oauth2callbackBrother'))
    else:
      print "Credentials located"
      return flask.redirect(flask.url_for('brother'))
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})
@app.route('/oauth2callback/brother', methods=["GET"])
def oauth2callbackBrother():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callbackBrother', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()

    http_auth = credentials.authorize(httplib2.Http())
    result = main.brotherClasses(http_auth, flask.session["initData"])

    flask.session.pop("initData",None)

    if "success" in result:
      return flask.redirect(flask.url_for("brother")+'#'+result["course"].replace(" ","+"))
    elif result["error"] == "No Calendar":
      return flask.redirect(flask.url_for('brother')+"#NoCalendar")
    else:
      return flask.redirect(flask.url_for('brother')+"#BadInput")

@app.route('/addClass/brother', methods=["POST"])
def addClassBrother():
  print "Adding Classes..."
  data = flask.request.json
  print "Subject: %s\nCourse: %s\nSection: %s\Name: %s"%(int(data["subject"]),int(data["course"]),data["section"],data["name"])
  print "Reminders: ",
  for reminder in data["reminders"]:
    print int(reminder),
  print "\n"
  # return "Fucker"

  if 'credentials' not in flask.session:
    print "Authorizing..."
    return flask.redirect(flask.url_for('oauth2callbackBrother'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    print "Credentials expired"
    flask.session.pop("credentials",None)
    return "Credentials expired"
  else:
    http_auth = credentials.authorize(httplib2.Http())
    print "Adding Classes now"
    return json.dumps( main.brotherClasses(http_auth, data) )

# Brothers Finals
@app.route('/final/brother', defaults={'hash': ""})
@app.route('/final/brother/<hash>')
def finalBrother(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('finalBrother.html',campus="NB")
    except:
        print "Cannot render template"
        return "Error with rendering template"
@app.route('/authorize/final/brother', methods=["POST"])
def authorizeFinalBrother():
  # print flask.request.form
  # return "Fucker"
  postInfo = {"name":flask.request.form["name"],"subject":flask.request.form["subject"],"course":flask.request.form["course"],"section":flask.request.form["section"],"index":flask.request.form["index"],"campus":flask.request.form["campus"], "courseName":flask.request.form["courseName"]}
  try:
    flask.session["initData"] = postInfo
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callbackFinalBrother'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      return flask.redirect(flask.url_for('oauth2callbackFinalBrother'))
    else:
      print "Credentials located"
      return flask.redirect(flask.url_for('finalBrother'))
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})
@app.route('/oauth2callback/final/brother', methods=["GET"])
def oauth2callbackFinalBrother():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callbackFinalBrother', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()

    http_auth = credentials.authorize(httplib2.Http())
    result = main.finalBrother(http_auth, flask.session["initData"])

    flask.session.pop("initData",None)

    if "success" in result:
      return flask.redirect(flask.url_for("finalBrother")+'#'+result["course"].replace(" ","+"))
    elif result["error"] == "No Calendar":
      return flask.redirect(flask.url_for('finalBrother')+"#NoCalendar")
    else:
      return flask.redirect(flask.url_for('finalBrother')+"#BadInput")

@app.route('/addFinal/brother', methods=["POST"])
def addFinalBrother():
  print "Adding Finales..."
  data = flask.request.json

  if 'credentials' not in flask.session:
    print "Authorizing..."
    return flask.redirect(flask.url_for('oauth2callbackFinalBrother'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    print "Credentials expired"
    flask.session.pop("credentials",None)
    return "Credentials expired"
  else:
    http_auth = credentials.authorize(httplib2.Http())
    print "Adding Final now"
    return json.dumps( main.finalBrother(http_auth, data) )

# New Member
@app.route('/newMember', defaults={'hash': ""})
@app.route('/newMember/<hash>')
def newMember(hash):
    # flask.session.clear()
    # raise Exception('Testing')
    try:
        return render_template('newMember.html',campus="NB")
    except:
        print "Cannot render template"
        return "Error with rendering template"
@app.route('/authorize/newMember', methods=["POST"])
def authorizeNewMember():
  # print flask.request.form
  # return "Fucker"
  postInfo = {"name":flask.request.form["name"],"subject":flask.request.form["subject"],"course":flask.request.form["course"],"section":flask.request.form["section"],"reminders":flask.request.form["reminders"],"campus":flask.request.form["campus"]}
  try:
    flask.session["initData"] = postInfo
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callbackNewMember'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
      return flask.redirect(flask.url_for('oauth2callbackNewMember'))
    else:
      print "Credentials located"
      return flask.redirect(flask.url_for('newMember'))
  except Exception,e:
    print str(e)
    return json.dumps({"success":False})
@app.route('/oauth2callback/newMember', methods=["GET"])
def oauth2callbackNewMember():
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callbackNewMember', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    # webbrowser.open_new_tab(auth_uri)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()

    http_auth = credentials.authorize(httplib2.Http())
    result = main.newMemberClasses(http_auth, flask.session["initData"])

    flask.session.pop("initData",None)

    if "success" in result:
      return flask.redirect(flask.url_for("newMember")+'#'+result["course"].replace(" ","+"))
    elif result["error"] == "No Calendar":
      return flask.redirect(flask.url_for('newMember')+"#NoCalendar")
    else:
      return flask.redirect(flask.url_for('newMember')+"#BadInput")

@app.route('/addClass/newMember', methods=["POST"])
def addClassNewMember():
  print "Adding Classes..."
  data = flask.request.json
  print "Subject: %s\nCourse: %s\nSection: %s\Name: %s"%(int(data["subject"]),int(data["course"]),data["section"],data["name"])
  print "Reminders: ",
  for reminder in data["reminders"]:
    print int(reminder),
  print "\n"
  # return "Fucker"

  if 'credentials' not in flask.session:
    print "Authorizing..."
    return flask.redirect(flask.url_for('oauth2callbackNewMember'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    print "Credentials expired"
    flask.session.pop("credentials",None)
    return "Credentials expired"
  else:
    http_auth = credentials.authorize(httplib2.Http())
    print "Adding Classes now"
    return json.dumps( main.newMemberClasses(http_auth, data) )




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
