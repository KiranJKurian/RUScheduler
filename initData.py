from datetime import datetime, timedelta

# Initial Variables
semester = 12017
startDateDay = 17
semesterInfo = { 'endDate': datetime(2017, 5, 2), 'breakInfo': { 'start': datetime(2017, 3, 11), 'end': datetime(2017, 3, 19)} }

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
