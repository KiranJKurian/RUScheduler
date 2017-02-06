import json

import flask
import httplib2

from apiclient import discovery

from CourseInfo import courseInfo
from finals import getFinalDate

from pymongo import MongoClient

from dateutil.parser import *
import datetime

from initData import dbSemester, semesterInfo

from multiprocessing import Pool

def insertRecord(record):
	try:
		client = MongoClient(port=27017)
		db = getattr(client, dbSemester)
		db.scheduler.insert(record)
		print "Added to DB"
	except:
		print "DB down"

def insertRecordAsync(record):
	try:
		pool = Pool(1)
		pool.apply_async(insertRecord, (record,))
		pool.close()
	except:
		print "Multiprocessing error"

def getUserInfo(http_auth):
	service = discovery.build('plus', 'v1', http_auth)
	people_resource = service.people()
	people_document = people_resource.get(userId='me').execute()
	return {'name': people_document['displayName'], 'email': people_document['emails'][0]['value']}

def getMeetingStartDate(day):
	day = day.lower()
	if day=="monday" or day=="m":
		return semesterInfo['startDates'][0]
	elif day=="tuesday" or day=="t":
		return semesterInfo['startDates'][1]
	elif day=="wednesday" or day=="w":
		return semesterInfo['startDates'][2]
	elif day=="thursday" or day=="th":
		return semesterInfo['startDates'][3]
	elif day=="friday" or day=="f":
		return semesterInfo['startDates'][4]
	elif day=="saturday" or day=="s":
		return semesterInfo['startDates'][5]

def getMeetingColor(location):
	if location == "Online":
		return "11"
	elif (location['campus']).upper()=="BUS":
		return "7"
	elif (location['campus']).upper()=="LIV":
		return "5"
	elif (location['campus']).upper()=="D/C":
		return "10"
	else:
		return "11"
# Version 3.0
def classes(http_auth, inputDict, calendarId = "primary", preText = "", postText = ""):
	service = discovery.build('calendar', 'v3', http_auth)
	userInfo = getUserInfo(http_auth)
	if "campus" in inputDict:
		school = inputDict["campus"]
	else:
		school = "NB"

	subject = inputDict["subject"]
	course = inputDict["course"]
	section = inputDict["section"]

	try:
		reminders = [int(s) for s in inputDict["reminders"].split(',')]
	except:
		reminders = inputDict["reminders"]

	cInfo = courseInfo(subject, course, section, school)
	print cInfo

	if cInfo is None:
		print "Error: Semester/Subject/School/Course/Section not found or Invalid/Empty/Non-existant startTime/endTime/meetingDay"
		return {"error":"Bad Input"}

	summary = "%s%s%s" % (preText, cInfo["title"], postText)

	for meetingDay in cInfo['meetingDays']:
		startDate = getMeetingStartDate(meetingDay['day'])
		if startDate is None:
			return {"error":"Bad Input"}

		startTime = "%s%s"%(meetingDay['startTime'], ":00")
		endTime = "%s%s"%(meetingDay['endTime'], ":00")
		location = "%s Room %s"%(meetingDay['location']['building'],meetingDay['location']['room'])

		color = getMeetingColor(meetingDay["location"])

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
			  'RRULE:FREQ=WEEKLY;UNTIL=%sT000000Z'%(semesterInfo['endDate'].strftime('%Y%m%d')),
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

		recurring_event = service.events().insert(calendarId=calendarId, body=event).execute()
		eventID=recurring_event.get("id")
		print "success"

		instances = service.events().instances(calendarId=calendarId, eventId="%s"%eventID,timeMin=semesterInfo['startDate'].isoformat()+'Z',timeMax=semesterInfo['endDate'].isoformat()+'Z').execute()['items']
		for instance in instances:
			if instance['start'].has_key("dateTime"):
				instanceStart = parse(instance['start']['dateTime']).replace(tzinfo=None)
			else:
				instanceStart = parse(instance['start']['date']).replace(tzinfo=None)
			# Exclusion for Thanksgiving
			if (instanceStart >= semesterInfo['breakInfo']['start'] and instanceStart <= semesterInfo['breakInfo']['end']):
				instance['status'] = 'cancelled'
				service.events().update(calendarId=calendarId, eventId=instance['id'], body=instance).execute()

	# db.scheduler.remove()
	insertRecordAsync({"name": userInfo['name'],"email": userInfo['email'], "success": summary, "error": None})
	return {"success":True,"course": summary}

# Final Exam
def final(http_auth, inputDict, calendarId = "primary", preText = "", postText = ""):
	service = discovery.build('calendar', 'v3', http_auth)

	userInfo = getUserInfo(http_auth)

	if "campus" in inputDict:
		school = inputDict["campus"]
	else:
		school = "NB"

	subject = inputDict["subject"]
	course = inputDict["course"]
	section = inputDict["section"]
	index = inputDict["index"]
	courseName = inputDict["courseName"]

	finalInfo = getFinalDate(index, school)
	# print finalInfo

	if finalInfo is None:
		print "Error: Semester/Subject/School/Course/Section/Index not found or Invalid/Empty/Non-existant startTime/endTime"
		return { "error": "Bad Input" }

	summary = "%s%s%s" % (preText, courseName, postText)

	startTime = finalInfo['startTime'].isoformat()
	endTime = finalInfo['endTime'].isoformat()

	event = {
		"location": "Check class announcements",
		 "end": {
			 "dateTime": endTime,
			"timeZone": "America/New_York"
		 },
		 "start": {
			 "dateTime": startTime,
			"timeZone": "America/New_York"
		 },
		 "summary": summary,
		 "colorId": "11",
		 "reminders": {
		  "useDefault":"false",
		  "overrides": [],
		},
		"description":"Added final with RUScheduler! %s:%s:%s"%(subject,course,section)
	}

	# print "Created the event"

	service.events().insert(calendarId=calendarId, body=event).execute()
	# print "success"

	insertRecordAsync({"name": userInfo['name'],"email": userInfo['email'],"success": summary, "error": None})
	return {"success":True,"course": summary}

def finalBrother(http_auth, inputDict):
	service = discovery.build('calendar', 'v3', http_auth)
	calendar_list = service.calendarList().list().execute()
	correctCal = any(item['id'] == '5bcor9o45kfok59ja0bn8r2g00@group.calendar.google.com' for item in calendar_list['items'])
	if correctCal:
		return final(http_auth, inputDict, calendarId = '5bcor9o45kfok59ja0bn8r2g00@group.calendar.google.com', preText = "%s - "%inputDict['name'], postText = " FINAL")
	else:
		print "No Calendar Found"
		return {"error":"No Calendar"}

#Version 2.0 - Depreciated
def classesOld(http_auth, inputJSON):
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

	print "Reminders:"
	print reminders

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

		summary=cInfo["title"]

		for meetingDay in cInfo['meetingDays']:
			day="%s"%(meetingDay['day']).lower()
			if day=="monday" or day=="m":
				startDate=semesterInfo['startDates'][0]
			elif day=="tuesday" or day=="t":
				startDate=semesterInfo['startDates'][1]
			elif day=="wednesday" or day=="w":
				startDate=semesterInfo['startDates'][2]
			elif day=="thursday" or day=="th":
				startDate=semesterInfo['startDates'][3]
			elif day=="friday" or day=="f":
				startDate=semesterInfo['startDates'][4]
			elif day=="saturday" or day=="s":
				startDate=semesterInfo['startDates'][5]
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
			  'RRULE:FREQ=WEEKLY;UNTIL=%sT000000Z'%(semesterInfo['endDate'].strftime('%Y%m%d')),
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

			instances = service.events().instances(calendarId=calendarId, eventId="%s"%eventID,timeMin=semesterInfo['startDate'].isoformat()+'Z',timeMax=semesterInfo['endDate'].isoformat()+'Z').execute()['items']
			for instance in instances:
				if instance['start'].has_key("dateTime"):
					instanceStart = parse(instance['start']['dateTime']).replace(tzinfo=None)
				else:
					instanceStart = parse(instance['start']['date']).replace(tzinfo=None)
				# Exclusion for Thanksgiving
				if (instanceStart >= semesterInfo['breakInfo']['start'] and instanceStart <= semesterInfo['breakInfo']['end']):
					instance['status'] = 'cancelled'
					service.events().update(calendarId=calendarId, eventId=instance['id'], body=instance).execute()

		returnDict["success"].append(summary)

	print returnDict

	insertRecordAsync({"name":returnDict['name'],"email":returnDict['email'],"success":returnDict['success'],"error":returnDict["error"]})

	return json.dumps(returnDict)

def brotherClasses(http_auth, inputDict):
	calID = '5bcor9o45kfok59ja0bn8r2g00@group.calendar.google.com'
	service = discovery.build('calendar', 'v3', http_auth)
	calendar_list = service.calendarList().list().execute()
	correctCal = any(item['id'] == calID for item in calendar_list['items'])
	if correctCal:
		return classes(http_auth, inputDict, calendarId = calID, preText = "%s - "%inputDict['name'])
	else:
		print "No Calendar Found"
		return {"error":"No Calendar"}

def newMemberClasses(http_auth, inputDict):
	service = discovery.build('calendar', 'v3', http_auth)
	calendar_list = service.calendarList().list().execute()
	calID = 'dusm1q4hp6mo91m5d1216bkue4@group.calendar.google.com'
	correctCal = any(item['id'] == calID for item in calendar_list['items'])
	if correctCal:
		return classes(http_auth, inputDict, calendarId = calID, preText = "%s - "%inputDict['name'])
	else:
		print "No Calendar Found"
		return {"error":"No Calendar"}

# if __name__ == '__main__':
#     inputDict={"classInfo":[{"subNum":"190","courseNum":"206","sectionNum":"1"}],"school":"NB","reminders":[True,True,True,False]}
#     inputJSON=json.dumps(inputDict)
#     print(main(inputJSON))
