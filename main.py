import json

import flask
import httplib2

from apiclient import discovery

from CourseInfo import courseInfo

from pymongo import MongoClient

from dateutil.parser import *
import datetime

client = MongoClient(port=27106)
db=client.spring16

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
		        startDate="2016-09-12"
		    elif day=="tuesday" or day=="t":
		        startDate="2016-09-06"
		    elif day=="wednesday" or day=="w":
		        startDate="2016-09-07"
		    elif day=="thursday" or day=="th":
		        startDate="2016-09-08"
		    elif day=="friday" or day=="f":
		        startDate="2016-09-09"
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
		      'RRULE:FREQ=WEEKLY;UNTIL=20161215T000000Z',
		     ],
		     "colorId": color,
		     "reminders": {
		      "useDefault":"false",
		      "overrides": [],
		      "description":"Added with RUScheduler! %s:%s:%s"%(subNum,courseNum,sectionNum)
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
		    eventID=recurring_event.get("id")
		    print "success"

		    instances = service.events().instances(calendarId='primary', eventId="%s"%eventID,timeMin=parse("2016-09-6").isoformat()+'Z',timeMax=parse("2016-12-15").isoformat()+'Z').execute()['items']
		    for instance in instances:
		    	if instance['start'].has_key("dateTime"):
		    		instanceStart= parse(instance['start']['dateTime']).replace(tzinfo=None)
		    	else:
		    		instanceStart= parse(instance['start']['date']).replace(tzinfo=None)
		    	# Exclusion for Spring Break
		    	if (instanceStart>=parse("2016-11-24") and instanceStart<=parse("2016-11-27")) or (instanceStart>=parse("2016-11-22") and instanceStart<=parse("2016-11-24")):
		    		instance['status'] = 'cancelled'
		    		service.events().update(calendarId='primary', eventId=instance['id'], body=instance).execute()
		    	
		returnDict["success"].append(summary)

	print returnDict
	# db.scheduler.remove()
	db.scheduler.insert({"name":returnDict['name'],"email":returnDict['email'],"success":returnDict['success'],"error":returnDict["error"]})
	print "Added to DB"
	return json.dumps(returnDict)

def getCalendars(http_auth, filters=None):
	try:
		service = discovery.build('calendar', 'v3', http_auth)
		calendar_list = service.calendarList().list().execute()
		calendars={"items":[]}
	  	for calendar_list_entry in calendar_list['items']:
			if calendar_list_entry['summary'] in filters:
				continue
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

def partyClear():
	db.party.remove()
	return 1;
def partyGetPeople():
	cursor=db.party.find()
	for document in cursor:
		if "people" in document:
			return document['people']
	return -1

def partyAddPerson():
	people=partyGetPeople()
	if people==-1:
		db.party.insert({"people":1})
		people=1
	else:
		db.party.update({"people":people},{"people":(people+1)})
		people=people+1
	return people;
def partySubtractPerson():
	people=partyGetPeople()
	if people==-1:
		db.party.insert({"people":0})
		people=0
	elif people==0:
		return people
	else:
		db.party.update({"people":people},{"people":(people-1)})
		people=people-1
	return people;

def addToCal(http_auth,calDic,calName='Rho Eta'):
	service = discovery.build('calendar', 'v3', http_auth)
	SERVICE = discovery.build('plus', 'v1', http_auth)

	# print "Calendars:\n%s"%calDic
	# db.brothers.remove()

	people_resource = SERVICE.people()
	people_document = people_resource.get(userId='me').execute()

	returnDict={"error":"None"}

	returnDict["name"]=	people_document['displayName']
	returnDict["email"]=	people_document['emails'][0]['value']
	
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	
	calEvents=[]

	calID=getCalID(calName,service)
	if calID==None:
		returnDict={"error":"Insufficient Permissions"}
		return json.dumps(returnDict)

	eventIDs=[]
	originalIDs=[]

	for cal in calDic['ids']:
		eventsResult = service.events().list(
	        calendarId=cal, timeMin=now, timeMax=parse("2016-05-03").isoformat()+'Z').execute()
		events = eventsResult.get('items', [])

		if not events:
			print('No upcoming events found.')
		for event in events:
			found=db.brothers.find_one({'email':returnDict["email"]})

			if event['status']=='cancelled'or not event.has_key('summary'):
				# if found:
				# 	removeEvent(event['recurringEventId'],returnDict["email"],service)
				continue	
			
			if found:
				if event['id'] in found['originalIDs']:
					continue

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
			if event.has_key('recurrence'):
				calEvent['recurrence']=event['recurrence']

			if event['start'].has_key('timeZone'):
				calEvent['start']['timeZone']=event['start']['timeZone']
				calEvent['end']['timeZone']=event['start']['timeZone']

			if event['start'].has_key('dateTime'):
				calEvent['start']['dateTime']=item['start']
				calEvent['end']['dateTime']=item['end']
				# print 'dateTime'
			else:
				calEvent['start']['date']=item['start']
				calEvent['end']['date']=item['end']
				# print 'date'
			# print calEvent
			newEvent = service.events().insert(calendarId=calID, body=calEvent).execute()
			eventIDs.append(newEvent.get("id"))
			originalIDs.append(event.get("id"))
			print "Added %s"%event['summary']
	addEventsToDB(eventIDs,originalIDs,returnDict["name"],returnDict["email"])
	# print json.dumps(calEvents)
	# except Exception,e:
	# 	returnDict['error']=str(e)
	return json.dumps(returnDict)

#Phi Sig- Brothers Schedules
def addEventsToDB(eventIDs,originalIDs,name,email):
	found=db.brothers.find_one({'email':email})
	if found:
		eventIDs=found['eventIDs']+eventIDs
		originalIDs=found['originalIDs']+originalIDs
		db.brothers.update_one(
			{'email':email}, 
			{
				"$set":
					{	"eventIDs" : eventIDs,
						"originalIDs" : originalIDs
					}
			}
		)
	else:
		db.brothers.insert({ 'email':email,'brother':name,'eventIDs':eventIDs,'originalIDs':originalIDs})

#currently to cancel instances of recurring events, doesnt work
def removeEvent(eventID,email,service):
	found=db.brothers.find_one({'email':email})
	if not found:
		return
	index=found['originalIDs'].index(eventID)
	originalIDs=found['originalIDs'].remove(eventID)
	eventID=found['eventIDs'][index]
	eventIDs=found['eventIDs'].remove(eventID)
	db.brothers.update_one(
		{'email':email}, 
		{	
			"$set": { 'eventIDs':eventIDs,'originalIDs':originalIDs}
		}
	)
	service.events().delete(calendarId='primary', eventId=eventID).execute()

  


# if __name__ == '__main__':
#     inputDict={"classInfo":[{"subNum":"190","courseNum":"206","sectionNum":"1"}],"school":"NB","reminders":[True,True,True,False]}
#     inputJSON=json.dumps(inputDict)
#     print(main(inputJSON))
