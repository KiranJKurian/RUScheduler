import httplib2
import os

from httplib2 import Http

from apiclient import discovery
from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
import json

from CourseInfo import courseInfo

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'RUScheduler'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credential')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'RUScheduler.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    prompted=False
    if credentials is None or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        prompted=True
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return [credentials,prompted]

def main(inputJSON):
	prompted=None
	inputDict=json.loads(inputJSON)
	returnDict={"success":[],"error":"None"}
	try:
		credentials = get_credentials()
		prompted=credentials[1]
		credentials=credentials[0]
		service = build('calendar', 'v3', http=credentials.authorize(Http()))
	except:
		if prompted:
			print "Auth error"
			returnDict["error"]="Authorization Error"
			return json.dumps(returnDict)
		else:
			print "Token error"
			returnDict["error"]="Access Token Error"
			return json.dumps(returnDict)

	school=inputDict['school']
	reminders=inputDict['reminders']
	for classInfo in inputDict['classInfo']:
		subNum=classInfo['subNum']
		courseNum=classInfo['courseNum']
		sectionNum=classInfo['sectionNum']	

		try:

			cInfo=courseInfo(subNum,courseNum,sectionNum,school)
			print cInfo

			if cInfo is None:
				print "Error: Semester/Subject/School/Course/Section not found or Invalid/Empty/Non-existant startTime/endTime/meetingDay"
				returnDict["error"]="Bad Input"
				continue
			else:
				cInfo=json.loads(cInfo)

			summary=cInfo["title"]

			for meetingDay in cInfo['meetingDays']:
			    day="%s"%(meetingDay['day']).lower()
			    if day=="monday" or day=="m":
			        startDate="2015-09-07"
			    elif day=="tuesday" or day=="t":
			        startDate="2015-09-01"
			    elif day=="wednesday" or day=="w":
			        startDate="2015-09-02"
			    elif day=="thursday" or day=="th":
			        startDate="2015-09-03"
			    elif day=="friday" or day=="f":
			        startDate="2015-09-04"
			    else:
			        print "Invalid meetingDay"
			        return json.dumps({"error":"Bad Input"})
			    startTime="%s%s"%(meetingDay['startTime'],":00")
			    endTime="%s%s"%(meetingDay['endTime'],":00")
			    location="%s Room %s"%(meetingDay['location']['building'],meetingDay['location']['room'])

			    if meetingDay["location"]=="Online":
			    	color="11"
			    elif (meetingDay["location"]['campus']).upper()=="BUS":
			      color="7"
			    elif (meetingDay["location"]['campus']).upper()=="LIV":
			      color="5"
			    elif (meetingDay["location"]['campus']).upper()=="D/C":
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
			      'RRULE:FREQ=WEEKLY;UNTIL=20151211T000000Z',
			      # "EXDATE:TZID=America/New_York:20151126T134001Z,20151127T134001Z,20151128T134001Z,20151129T134001Z"
			      # "EXDATE;TZID=America/New_York:20151126T%s%s00Z,20151127T%s%s00Z,20151128T%s%s00Z,20151129T%s%s00Z"%(startTime[:2],startTime[3:],startTime[:2],startTime[3:],startTime[:2],startTime[3:],startTime[:2],startTime[3:])
			     ],
			     "colorId": color,
			     "reminders": {
			      "useDefault":"false",
			      "overrides": []
			    }
			    }

			    print "Created the event"
			    if reminders[0]:
			      event["reminders"]["overrides"].append({
			            "method":"popup",
			            "minutes": 15
			          })
			    if reminders[1]:
			      event["reminders"]["overrides"].append({
			            "method":"popup",
			            "minutes": 30
			          })
			    if reminders[2]:
			      event["reminders"]["overrides"].append({
			            "method":"popup",
			            "minutes": 45
			          })
			    if reminders[3]:
			      event["reminders"]["overrides"].append({
			            "method":"popup",
			            "minutes": 60
			          })

			    recurring_event = service.events().insert(calendarId='primary', body=event).execute()
			    recurring_event
			    print "success"
			returnDict["success"].append(summary)
		except:
			if prompted:
				print "Auth error"
				returnDict["error"]="Authorization Error"
				return json.dumps(returnDict)
			else:
				print "Token error"
				returnDict["error"]="Access Token Error"
				return json.dumps(returnDict)
	return json.dumps(returnDict)
  


if __name__ == '__main__':
    inputDict={"classInfo":[{"subNum":"190","courseNum":"206","sectionNum":"1"}],"school":"NB","reminders":[True,True,True,False]}
    inputDict["classInfo"].append({"subNum":"198","courseNum":"206","sectionNum":"2"})
    inputDict["classInfo"].append({"subNum":"198","courseNum":"211","sectionNum":"1"})
    inputJSON=json.dumps(inputDict)
    print(main(inputJSON))