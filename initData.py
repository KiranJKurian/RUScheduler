from datetime import datetime, timedelta

# Initial Variables
semester = 12018
startDateDay = 16
semesterInfo = { 'endDate': datetime(2018, 4, 30), 'breakInfo': { 'start': datetime(2018, 3, 10), 'end': datetime(2018, 3, 18)} }
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
