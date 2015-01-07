import json
import requests

from soc import Soc
from Places import location

def courseInfo(subNum,courseNum,sectionNum):
    # subNum=198
    # courseNum="111"
    # sectionNum=1

    locations=[]
    startTimes=[]
    endTimes=[]
    days=[]

    soc=Soc()

    courses = soc.get_courses(subNum)
    if not courses():
        print "courses() is empty"
    else:
        courseFalse=True
        sectionFalse=True
        for course in courses():
            if course["courseNumber"]==courseNum:
                courseTitle=course['title']
                courseFalse=False
                for sections in course['sections']:
                    if int(sections['number'])== int(sectionNum):
                        sectionFalse=False
                        for meetingTimes in sections['meetingTimes']:
                            locations.append("%s room %s, %s"%(location(meetingTimes['buildingCode']),meetingTimes["roomNumber"],meetingTimes['campusName']))
                            days.append("%s"%(meetingTimes['meetingDay']))
                            if meetingTimes["pmCode"]=="P":
                                startTimes.append("%s:%s"%(str((int)(meetingTimes['startTime'][:2])+12),meetingTimes['startTime'][2:]))
                                endTimes.append("%s:%s"%(str((int)(meetingTimes['endTime'][:2])+12),meetingTimes['endTime'][2:]))
                            else:
                                startTimes.append("%s:%s"%(meetingTimes['startTime'][:2],meetingTimes['startTime'][2:]))
                                endTimes.append("%s:%s"%(meetingTimes['endTime'][:2],meetingTimes['endTime'][2:]))



        if courseFalse:
            print "Cannot find course %s in subject number %s"%(courseNum,subNum)
        elif courseFalse:
            print "Cannot find section number %s in %s"%(sectionNum,courseTitle)
        else:
            return [locations,startTimes,endTimes,days]
            # print "Locations: %s"%(locations)
            # print "Days: %s"%(days)
            # print "Start Times: %s"%(startTimes)
            # print "End Times: %s"%(endTimes)
# print courseInfo(198,"111",1)