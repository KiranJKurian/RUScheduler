import json

import flask
import httplib2

from apiclient import discovery

from CourseInfo import courseInfo

from pymongo import MongoClient

from dateutil.parser import *
import datetime

client = MongoClient(port=27106)
db=client.fall16

def classes(http_auth, inputJSON):
	service = discovery.build('calendar', 'v3', http_auth)
	SERVICE = discovery.build('plus', 'v1', http_auth)

	people_resource = SERVICE.people()
	people_document = people_resource.get(userId='me').execute()

	returnDict={"success":[],"error":"None"}

	returnDict["name"]=	people_document['displayName']
	returnDict["email"]= people_document['emails'][0]['value']

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

def classesDemo(http_auth, inputDict):
	service = discovery.build('calendar', 'v3', http_auth)
	SERVICE = discovery.build('plus', 'v1', http_auth)

	people_resource = SERVICE.people()
	people_document = people_resource.get(userId='me').execute()

	name =	people_document['displayName']
	email = people_document['emails'][0]['value']

	school="NB"
	subject = inputDict["subject"]
	course = inputDict["course"]
	section = inputDict["section"]
	reminders = inputDict["reminders"]
	
	cInfo=courseInfo(subject, course, section, school)
	print cInfo

	if cInfo is None:
		print "Error: Semester/Subject/School/Course/Section not found or Invalid/Empty/Non-existant startTime/endTime/meetingDay"
		return {"error":"Bad Input"}

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
	        return {"error":"Bad Input"}

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
		      "description":"Added with RUScheduler! %s:%s:%s"%(subject,course,section)
		    }
	    }

	    for reminder in reminders:
	    	event["reminders"]["overrides"].append({
				"method":"popup",
				"minutes": int(reminder)
			})
		print "Created the event"

	    recurring_event = service.events().insert(calendarId='primary', body=event).execute()
	    eventID=recurring_event.get("id")
	    print "success"

	    instances = service.events().instances(calendarId='primary', eventId="%s"%eventID,timeMin=parse("2016-09-6").isoformat()+'Z',timeMax=parse("2016-12-15").isoformat()+'Z').execute()['items']
	    for instance in instances:
	    	if instance['start'].has_key("dateTime"):
	    		instanceStart= parse(instance['start']['dateTime']).replace(tzinfo=None)
	    	else:
	    		instanceStart= parse(instance['start']['date']).replace(tzinfo=None)
	    	# Exclusion for Thanksgiving
	    	if (instanceStart>=parse("2016-11-24") and instanceStart<=parse("2016-11-27")) or (instanceStart>=parse("2016-11-22") and instanceStart<=parse("2016-11-24")):
	    		instance['status'] = 'cancelled'
	    		service.events().update(calendarId='primary', eventId=instance['id'], body=instance).execute()

	# db.scheduler.remove()
	db.scheduler.insert({"name": name,"email": email,"success": summary, "error": None})
	print "Added to DB"
	return {"success":True,"course": summary}

# if __name__ == '__main__':
#     inputDict={"classInfo":[{"subNum":"190","courseNum":"206","sectionNum":"1"}],"school":"NB","reminders":[True,True,True,False]}
#     inputJSON=json.dumps(inputDict)
#     print(main(inputJSON))
