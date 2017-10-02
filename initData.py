from datetime import datetime, timedelta

# Initial Variables
semester = 92017
startDateDay = 5
semesterInfo = { 'endDate': datetime(2017, 12, 14), 'breakInfo': { 'start': datetime(2017, 11, 23), 'end': datetime(2017, 11, 26)} }
brotherCalendar = 'trmd06d138ujsdrdvn41dgmk8o@group.calendar.google.com'
newMemberCalendar = 'lpth4igpesa9urlaoajp3kkuto@group.calendar.google.com'

# Computations
spring = False
if str(semester)[0] == '1':
	spring = True
if spring:
	dbSemester = 'spring%s'%(str(semester)[-2:])
else:
	dbSemester = 'fall%s'%(str(semester)[-2:])

semesterInfo['startDate'] = datetime(int(str(semester)[1:]), int(str(semester)[0]), startDateDay)

startDay = semesterInfo['startDate'].weekday()
startDates = []
for weekday in range(0,6):
	if startDay > weekday:
		startDates.append((7 - startDay) + weekday)
	else:
		startDates.append(weekday - startDay)
semesterInfo['startDates'] = [(semesterInfo['startDate'] + timedelta(days = dateDiff)).strftime('%Y-%m-%d') for dateDiff in startDates]
