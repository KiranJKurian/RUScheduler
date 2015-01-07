import json
from Places import location

# from urllib import urlopen
from google.appengine.api import urlfetch

def isNum(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def courseInfo(subNum,courseNum,sectionNum):
    # subNum=198
    # courseNum="111"
    # sectionNum=1

    locations=[]
    startTimes=[]
    endTimes=[]
    days=[]

    # courses = soc.get_courses(subNum)
    url="http://sis.rutgers.edu/soc/courses.json?semester=12015&subject=%s&campus=NB&level=U%%2CG"%(subNum)
    result = urlfetch.fetch(url)
    courses = json.loads(result.content)

    # jsonurl = urlopen(url)
    # courses = json.loads(jsonurl.read())
    
    if not courses:
        print "courses is empty"
    else:
        courseFalse=True
        sectionFalse=True
        for course in courses:
            if course["courseNumber"]==courseNum:
                courseTitle=course['title']
                courseFalse=False
                for sections in course['sections']:
                    if (sections['number'])==(sectionNum) or (isNum(sections['number']) and isNum(sectionNum) and int(sections['number'])== int(sectionNum)):
                        sectionFalse=False
                        for meetingTimes in sections['meetingTimes']:
                            locations.append("%s Room %s, %s"%(location(meetingTimes['buildingCode']),meetingTimes["roomNumber"],meetingTimes['campusName']))
                            days.append("%s"%(meetingTimes['meetingDay']))
                            if meetingTimes["pmCode"]=="P" and meetingTimes['startTime'][:2]!="12":
                                startTimes.append("%s:%s"%(str((int)(meetingTimes['startTime'][:2])+12),meetingTimes['startTime'][2:]))
                            else:
                                startTimes.append("%s:%s"%(meetingTimes['startTime'][:2],meetingTimes['startTime'][2:]))
                            if meetingTimes["pmCode"]=="P" and meetingTimes['endTime'][:2]!="12":
                                endTimes.append("%s:%s"%(str((int)(meetingTimes['endTime'][:2])+12),meetingTimes['endTime'][2:]))
                            else:
                                endTimes.append("%s:%s"%(meetingTimes['endTime'][:2],meetingTimes['endTime'][2:]))
                    # else:
                    #     print "%s!=%s"%(sections['number'],sectionNum)



        if courseFalse:
            print "Cannot find course %s in subject number %s"%(courseNum,subNum)
        elif sectionFalse:
            print "Cannot find section number %s in %s"%(sectionNum,courseTitle)
        else:
            # print [locations,startTimes,endTimes,days,courseTitle]
            return [locations,startTimes,endTimes,days,courseTitle]
            # print "Locations: %s"%(locations)
            # print "Days: %s"%(days)
            # print "Start Times: %s"%(startTimes)
            # print "End Times: %s"%(endTimes)
# print courseInfo(198,"111",1)