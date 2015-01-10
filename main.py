import logging
import os
import pickle
import cgi
import webapp2
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
import json

import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2

from apiclient.discovery import build
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from Places import location
from CourseInfo import courseInfo

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<code>%s</code>
<p>You can find the Client ID and Client secret values
on the API Access tab in the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>

""" % CLIENT_SECRETS

decorator = OAuth2DecoratorFromClientSecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/calendar',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

service = build('calendar', 'v3')

baseURL=""

class MainHandler(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        test = ""
        page_token = None
        newClass=True
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render())
class addEvent(webapp2.RequestHandler):
    @decorator.oauth_aware
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('addClass.html')
        self.response.write(template.render())
        if decorator.has_credentials():
            errorCheck=None
            try:
              print "start"
              errorCheck=":)" 
              subjectNumber=[]
              if self.request.get('subjectNumber1'):
                subjectNumber.append(self.request.get('subjectNumber1'))
              if self.request.get('subjectNumber5'):
                subjectNumber.append(self.request.get('subjectNumber5'))
              if self.request.get('subjectNumber2'):
                subjectNumber.append(self.request.get('subjectNumber2'))
              if self.request.get('subjectNumber3'):
                subjectNumber.append(self.request.get('subjectNumber3'))
              if self.request.get('subjectNumber4'):
                subjectNumber.append(self.request.get('subjectNumber4'))
              courseNumber=[self.request.get('courseNumber1'),self.request.get('courseNumber2'),self.request.get('courseNumber3'),self.request.get('courseNumber4'),self.request.get('courseNumber5')]
              sectionNumber=[self.request.get('sectionNumber1'),self.request.get('sectionNumber2'),self.request.get('sectionNumber3'),self.request.get('sectionNumber4'),self.request.get('sectionNumber5')]
              print subjectNumber
              for classIndex in range(len(subjectNumber)):
                print "...what're you lookin' at?"
                cInfo=courseInfo(subjectNumber[classIndex],courseNumber[classIndex],sectionNumber[classIndex])
                
                locations=cInfo[0]
                startTimes=cInfo[1]
                endTimes=cInfo[2]
                days=cInfo[3]
                summary=cInfo[4]

                for index in range(len(locations)):
                    day="%s"%(days[index]).lower()
                    if day=="monday" or day=="m":
                        startDate="2015-01-26"
                    elif day=="tuesday" or day=="t":
                        startDate="2015-01-20"
                    elif day=="wednesday" or day=="w":
                        startDate="2015-01-21"
                    elif day=="thursday" or day=="th":
                        startDate="2015-01-22"
                    elif day=="friday" or day=="f":
                        startDate="2015-01-23"
                    else:
                        self.response.out.write("Couldn't recognize day: %s "%(day))
                    startTime="%s%s"%(startTimes[index],":00")
                    endTime="%s%s"%(endTimes[index],":00")
                    location="%s"%(locations[index])
                  
                    event = {
                    "location": "%s"%(location),
                     "end": {
                         "dateTime": "%sT%s"%(startDate,endTime),
                        "timeZone": "America/New_York"
                     },
                     "start": {
                         "dateTime": "%sT%s"%(startDate,startTime),
                        "timeZone": "America/New_York"
                     },
                     "summary": summary,
                     "recurrence": [
                      'RRULE:FREQ=WEEKLY;UNTIL=20150505T000000Z',
                     ],
                     "reminders": {
                        "useDefault":"false",
                        "overrides": [
                        {
                            "method":"popup",
                            "minutes": 20
                         }
                        ]
                    }
                    }
                    reminder=self.request.get('reminder')
                    if reminder=="reminder-none":
                      event["reminders"] = {
                          "useDefault":"false",
                          "overrides": [
                          ]
                      }
                    elif reminder=='reminder-40':
                      event["reminders"] = {
                          "useDefault":"false",
                          "overrides": [
                          {
                            "method":"popup",
                            "minutes": 40
                          }
                          ]
                      }
                    elif reminder=='reminder-60':
                      event["reminders"] = {
                          "useDefault":"false",
                          "overrides": [
                          {
                            "method":"popup",
                            "minutes": 60
                          }
                          ]
                      }
                    http = decorator.http()

                    recurring_event = service.events().insert(calendarId='primary', body=event).execute(http=http)
                    print "sucess"
            except:
              errorCheck="WTF"
              print "fail"
            if errorCheck==":)":
              self.response.out.write("<center><h2>Awesome, you class was added to your schedule!</h2></center>")
            else:
              self.response.out.write("<center>Oops, ran into an error when trying to add your class to your calendar. Try again, you may have mistyped your class info</center>")
            self.response.out.write("""<div class="row uniform 50%">
            <div class="6u 12u(3)"><center>
              <form action=/>
                <input type="submit" value="Add More Classes">
              </form></center>
            </div>
            <div class="6u 12u(3)"><center>
              <form action=https://www.google.com/calendar/>
                <input type="submit" value="Go to Calendar">
              </form></center>
            </div></div>""")
        else:
            self.response.out.write("Error, no credentials")


application = webapp.WSGIApplication(
  [
   ('/', MainHandler),
   ('/addEvent',addEvent),
   (decorator.callback_path, decorator.callback_handler()),
  ],
  debug=True)
run_wsgi_app(application)
