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


def handle_404(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('addClass.html')
    response.write(template.render())
    response.write("<center><h3>Congratulations, you hacked into the fourth dimension! Jk, but seriously, you're not supposed to be here</h3></center>")
    response.write('<center><img src="/images/404.jpg" alt="Really?"></center>')

def handle_405(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('addClass.html')
    response.write(template.render())
    response.write("<center><h3>Congratulations, you hacked into the fourth dimension! Jk, but seriously, you're not supposed to be able to <b>get</b> here</h3></center>")
    response.write('<center><img src="/images/404.jpg" alt="Really?"></center>')

def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)


class MainHandler(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        page_token = None
        newClass=True
        user=users.get_current_user()
        if user:
            hello="Hello %s"%user.nickname()
        else:
            hello=""

        template_values = {
            'hello':hello
        }
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))
        # print "Just so you know, Kiran Kurian is awesome. Carry on."
class addEvent(webapp2.RequestHandler):
    
    @decorator.oauth_aware
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('addClass.html')
        self.response.write(template.render())
        # print "By using this service you acknowledge the creator's swag level is beyond 90001"
        if decorator.has_credentials():
            errorCheck=None
            try:
              # print "start"
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
              # print "got before school"
              school=self.request.get('campus')
              # print "school: %s"%school
              # print subjectNumber
              for classIndex in range(len(subjectNumber)):
                # print "...what're you lookin' at?"
                cInfo=courseInfo(subjectNumber[classIndex],courseNumber[classIndex],sectionNumber[classIndex],school)
                if cInfo=="empty":
                  self.response.write("<center><h3>Either you entered an invalid subject number or it seems like Rutgers is having some problems with their schedule of classes program, in which case you may need to try again later.</h3></center>")
                elif cInfo=="course":
                  self.response.write("<center><h3>You entered one of your course numbers incorrectly</h3></center>")
                elif cInfo=="section":
                  self.response.write("<center><h3>You entered one of your section numbers incorrectly</h3></center>")
                elif cInfo[0]=="online":
                  self.response.write("<center><h3>%s is an online lecture/recitation. Please enter when you'd %s"%(cInfo[1],'like to <a href="/addManual">schedule it here manually.</a></h3></center>'))
                else:
                  # print "got course info"
                  # print cInfo
                  locations=cInfo[0]
                  startTimes=cInfo[1]
                  endTimes=cInfo[2]
                  days=cInfo[3]
                  summary=cInfo[4]
                  campus=cInfo[5]

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
                      if campus[index]=="BUS":
                        color="7"
                      elif campus[index]=="LIV":
                        color="5"
                      elif campus[index]=="D/C":
                        color="10"
                      else: 
                        color="11"
                    
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
                       "colorId": color,
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
                      # print "sucess"
                  self.response.out.write("<center><h3>Awesome, added %s to your calendar!</h3></center>"%(summary))
            except:
              errorCheck="WTF"
              # print "fail"
            if not errorCheck==":)":
              self.response.out.write('<center><h3>Oops, ran into an error when trying to add your class to your calendar. Try again, you may have mistyped your class info. If you have an online lecture/recitation please <a href="/addManual">add that class manually here</a></h3></center>')
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
class addManual(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        test = ""
        page_token = None
        newClass=True
        user=users.get_current_user()
        if user:
            hello="Hello %s"%user.nickname()
        else:
            hello=""
        template_values = {
            'hello':hello
        }
        template = JINJA_ENVIRONMENT.get_template('addManual.html')
        self.response.write(template.render(template_values))

class addManualEvent(webapp2.RequestHandler):
    @decorator.oauth_aware
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('addClass.html')
        self.response.write(template.render())
        summary=self.request.get('summary')
        location=self.request.get('location')
        if self.request.get('startHour'):
          startHour=self.request.get('startHour')
        else:
          self.response.write("You didn't select a start hour, %s"%('please <a href="/addManual">try again and select one.</a>'))
          return
        if self.request.get('startMinute').isnumeric():
          startMinute=self.request.get('startMinute')
        else:
          self.response.write("You didn't input a valid start minute, %s"%('please <a href="/addManual">try again and input one.</a>'))
          return
        startTime="%s:%s:00"%(startHour,startMinute)
        if self.request.get('endHour'):
          endHour=self.request.get('endHour')
        else:
          self.response.write("You didn't select an end hour, %s"%('please <a href="/addManual">try again and select one.</a>'))
          return
          
        if self.request.get('endMinute').isnumeric():
          endMinute=self.request.get('endMinute')
        else:
          self.response.write("You didn't input a valid end minute, %s"%('please <a href="/addManual">try again and input one.</a>'))
          return
        endTime="%s:%s:00"%(endHour,endMinute)
        days=[]
        errorCheck=True
        if self.request.get('mon'):
          days.append("m")
          errorCheck=False
        if self.request.get('tue'):
          days.append("t")
          errorCheck=False
        if self.request.get('wed'):
          days.append("w")
          errorCheck=False
        if self.request.get('thur'):
          days.append("th")
          errorCheck=False
        if self.request.get('fri'):
          days.append("f")
          errorCheck=False
        if errorCheck:
          self.response.write("You didn't select a day, %s"%('please <a href="/addManual">try again and select one.</a>'))
          return
        try:
          for day in days:
            if day=="m":
                startDate="2015-01-26"
            elif day=="t":
                startDate="2015-01-20"
            elif day=="w":
                startDate="2015-01-21"
            elif day=="th":
                startDate="2015-01-22"
            elif day=="f":
                startDate="2015-01-23"

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
               "colorId": 9,
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
          self.response.out.write("<center><h2>Awesome, added %s to your calendar!</h2></center>"%(summary))
        except:
          self.response.out.write('<center>Oops, ran into an error when trying to add your class to your calendar. Try again, you may have mistyped something. If you have an online lecture/recitation please <a href="/addManual">add that class manually here</a></center>')
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
class donate(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('donate.html')
    self.response.write(template.render())
class clubawesome(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('clubawesome.html')
    self.response.write(template.render())

application = webapp.WSGIApplication(
  [
   ('/', MainHandler),
   ('/addEvent',addEvent),
   ('/addManual',addManual),
   ('/addManualEvent',addManualEvent),
   ('/donate',donate),
   ('/clubawesome',clubawesome),
   (decorator.callback_path, decorator.callback_handler()),
  ],
  debug=True)
run_wsgi_app(application)

application.error_handlers[404] = handle_404
application.error_handlers[500] = handle_500
application.error_handlers[405] = handle_405