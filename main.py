#!/usr/bin/env python
#
# Copyright 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Starting template for Google App Engine applications.

Use this project as a starting point if you are just beginning to build a Google
App Engine project. Remember to download the OAuth 2.0 client secrets which can
be obtained from the Developer Console <https://code.google.com/apis/console/>
and save them as 'client_secrets.json' in the project directory.
"""

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


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret.
# You can see the Client ID and Client secret on the API Access tab on the
# Google APIs Console <https://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
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




# Set up an OAuth2Decorator object to be used for authentication.  Add one or
# more of the following scopes in the scopes parameter below. PLEASE ONLY ADD
# THE SCOPES YOU NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
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
#example from calendarsList
        newClass=True
        baseURL=self.request.url
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render())
class addEvent(webapp2.RequestHandler):
    @decorator.oauth_aware
    def post(self):
        if decorator.has_credentials(): 
            # summary=cgi.escape(self.request.get('coursetitle'))
            subjectNumer=cgi.escape(self.request.get('subjectNumer'))
            courseNumber=cgi.escape(self.request.get('courseNumber'))
            sectionNumber=cgi.escape(self.request.get('sectionNumber'))

            cInfo=courseInfo(subjectNumer,courseNumber,sectionNumber)
            
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
                try:
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
                            "minutes":20
                         }
                         ]
                    }
                    }
                    http = decorator.http()

                    recurring_event = service.events().insert(calendarId='primary', body=event).execute(http=http)

                    self.response.out.write("Event Added!")
                except:
                    self.response.out.write("Error")
        else:
            self.response.out.write("Error, no credentials")
        self.response.out.write("""<form action=baseURL>
          <input type="submit" value="Add Another Class">
        </form>""")


application = webapp.WSGIApplication(
  [
   ('/', MainHandler),
   ('/addEvent',addEvent),
   (decorator.callback_path, decorator.callback_handler()),
  ],
  debug=True)
run_wsgi_app(application)
