import json
import urllib2 

url = urllib2.urlopen("https://sis.rutgers.edu/soc/subjects.json?semester=92016&campus=NB&level=U")
subjects = json.loads(url.read())

for subject in subjects:
	url = urllib2.urlopen("http://sis.rutgers.edu/soc/courses.json?semester=92016&subject=%s&campus=NB&level=UG"%str(subject["code"]))
	content = url.read()

	with open('data/Courses/%s.json'%str(subject["code"]), 'w') as outfile:
	    json.dump(json.loads(content), outfile)
	print "Scraped %s.json"%str(subject["code"])
