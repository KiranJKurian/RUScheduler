import json

import flask
import httplib2

from apiclient import discovery

from CourseInfo import courseInfo

from pymongo import MongoClient

from dateutil.parser import *
import datetime

client = MongoClient(connect=False)
db=client.fall15

def classes(http_auth, inputJSON):
	service = discovery.build('calendar', 'v3', http_auth)
	SERVICE = discovery.build('plus', 'v1', http_auth)

	people_resource = SERVICE.people()
	people_document = people_resource.get(userId='me').execute()

	returnDict={"success":[],"error":"None"}

	returnDict["name"]=	people_document['displayName']
	returnDict["email"]=	people_document['emails'][0]['value']

	inputDict=json.loads(inputJSON)
	
	school=inputDict['school']
	reminders=inputDict['reminders']
	for classInfo in inputDict['classInfo']:
		subNum=classInfo['subNum']
		courseNum=classInfo['courseNum']
		sectionNum=classInfo['sectionNum']	

		# try:

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
		        startDate="2016-01-25"
		    elif day=="tuesday" or day=="t":
		        startDate="2016-01-19"
		    elif day=="wednesday" or day=="w":
		        startDate="2016-01-20"
		    elif day=="thursday" or day=="th":
		        startDate="2016-01-21"
		    elif day=="friday" or day=="f":
		        startDate="2016-01-22"
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
		      'RRULE:FREQ=WEEKLY;UNTIL=20160503T000000Z',
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
		# except:
		# 	if prompted:
		# 		print "Auth error"
		# 		returnDict["error"]="Authorization Error"
		# 		return json.dumps(returnDict)
		# 	else:
		# 		print "Token error"
		# 		returnDict["error"]="Access Token Error"
		# 		return json.dumps(returnDict)
	return json.dumps(returnDict)

def getCalendars(http_auth):
	try:
		service = discovery.build('calendar', 'v3', http_auth)
		calendar_list = service.calendarList().list().execute()
		calendars={"items":[]}
	  	for calendar_list_entry in calendar_list['items']:
			info={"summary":calendar_list_entry['summary'],"id":calendar_list_entry['id']}
			calendars['items'].append(info)
		# print calendars
	except Exception,e:
		return json.dumps({'error':str(e)})
	return json.dumps(calendars)

def getCalID(summary, service):
	calendar_list = service.calendarList().list().execute()
	for calendar_list_entry in calendar_list['items']:
		if calendar_list_entry['summary']==summary:
			return calendar_list_entry['id']
	return None

def basementClear():
	db.basement.remove()
	return 1;
def basementGetPeople():
	cursor=db.basement.find()
	for document in cursor:
		if "people" in document:
			return document['people']
	return -1

def basementAddPerson():
	people=basementGetPeople()
	if people==-1:
		db.basement.insert({"people":1})
		people=1
	else:
		db.basement.update({"people":people},{"people":(people+1)})
		people=people+1
	return people;
def basementSubtractPerson():
	people=basementGetPeople()
	if people==-1:
		db.basement.insert({"people":0})
		people=0
	elif people==0:
		return people
	else:
		db.basement.update({"people":people},{"people":(people-1)})
		people=people-1
	return people;

def pledge(http_auth,calDic):
	service = discovery.build('calendar', 'v3', http_auth)
	SERVICE = discovery.build('plus', 'v1', http_auth)

	# print "Calendars:\n%s"%calDic

	people_resource = SERVICE.people()
	people_document = people_resource.get(userId='me').execute()

	returnDict={"error":"None"}

	returnDict["name"]=	people_document['displayName']
	returnDict["email"]=	people_document['emails'][0]['value']
	
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	
	calEvents=[]

	calID=getCalID('Rho Eta',service)
	if calID==None:
		returnDict={"error":"Insufficient Permissions"}
		return json.dumps(returnDict)

	for cal in calDic['ids']:
		eventsResult = service.events().list(
	        calendarId=cal, timeMin=now, timeMax=parse("2016-05-03").isoformat()+'Z', singleEvents=True,
	        orderBy='startTime').execute()
		events = eventsResult.get('items', [])

		if not events:
			print('No upcoming events found.')
		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))

			end = event['end'].get('dateTime', event['end'].get('date'))
			item={"start":start, "summary": event['summary'], "end": end}
			calEvents.append(item)
			calEvent = {
			  'summary': '%s- %s'%(people_document['displayName'],item["summary"]),
			  'start': {
			    # 'dateTime': item['start'],
			  },
			  'end': {
			    # 'dateTime': item['end'],
			  },
			}
			if event['start'].has_key('dateTime'):
				calEvent['start']['dateTime']=item['start']
				calEvent['end']['dateTime']=item['end']
				# print 'dateTime'
			else:
				calEvent['start']['date']=item['start']
				calEvent['end']['date']=item['end']
				# print 'date'
			# print calEvent
			service.events().insert(calendarId=calID, body=calEvent).execute()
	# print json.dumps(calEvents)
	# except Exception,e:
	# 	returnDict['error']=str(e)
	return json.dumps(returnDict)
  


# if __name__ == '__main__':
#     inputDict={"classInfo":[{"subNum":"190","courseNum":"206","sectionNum":"1"}],"school":"NB","reminders":[True,True,True,False]}
#     inputJSON=json.dumps(inputDict)
#     print(main(inputJSON))
