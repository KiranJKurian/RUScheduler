import json
import urllib2

semester=92015

def courseInfo(subNum,courseNum,sectionNum,school):
    from Places import location
    if not (subNum.isdigit() and courseNum.isdigit()):
        print "Subject or Course Number is NaN"
        return None
    try:
        courses = json.load(urllib2.urlopen("http://sis.rutgers.edu/soc/courses.json?semester=%s&subject=%s&campus=%s&level=U%%2CG"%(semester,subNum,school)))
    except:
        courses=None
    # print courses


    if not courses:
        print "Couldn't find json"
        return None

    info= {'title':"", 'meetingDays':[]}

    for course in courses:
        if int(course['courseNumber'])==int(courseNum):
            info['title']=course['title']

            # print "Found Course %s"%info['title']

            for section in course['sections']:
                if (section['number'])==(sectionNum) or (section['number'].isdigit() and sectionNum.isdigit() and int(section['number'])== int(sectionNum)):

                    # print "Found Section %s"%sectionNum

                    for meetingTimes in section['meetingTimes']:
                        meeting = {'startTime':"", 'endTime': "", 'day':"", 'location':[]}

                        if meetingTimes['startTime']:
                            if meetingTimes["pmCode"]=="P" and meetingTimes['startTime'][:2]!="12":
                                meeting['startTime']="%s:%s"%(str((int)(meetingTimes['startTime'][:2])+12),meetingTimes['startTime'][2:])
                            else:
                                meeting['startTime']="%s:%s"%(meetingTimes['startTime'][:2],meetingTimes['startTime'][2:])
                        else:
                            return None
                        if meetingTimes['endTime']:
                            if meetingTimes["pmCode"]=="P" and meetingTimes['endTime'][:2]!="12":
                                meeting['endTime']="%s:%s"%(str((int)(meetingTimes['endTime'][:2])+12),meetingTimes['endTime'][2:])
                            else:
                                meeting['endTime']="%s:%s"%(meetingTimes['endTime'][:2],meetingTimes['endTime'][2:])
                        else:
                            return None
                        if meetingTimes['meetingDay']:
                            meeting['day']=meetingTimes['meetingDay']
                        else:
                            return None
                        if not meetingTimes["meetingModeDesc"] or meetingTimes["meetingModeDesc"]=="ONLINE INSTRUCTION(INTERNET)":
                            meeting['location']="Online"
                        else:
                            loc=location(meetingTimes['buildingCode'])
                            meeting['location']={'building':loc,'room':meetingTimes['roomNumber'],'campus':meetingTimes['campusAbbrev']}
                        info['meetingDays'].append(meeting)
                    if info['meetingDays']:
                        return json.dumps(info)

            return None
    return None
'''
    Returns None in the event that: Semester/Subject/School/Course/Section not found; Invalid/Empty/Non-existant startTime/endTime/meetingDay
'''
if __name__ == "__main__":
    # print location("HLL")
    print courseInfo("190","206","1","NB")
