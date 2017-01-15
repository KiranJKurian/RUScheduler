import json
import urllib2
from initData import semester

url = urllib2.urlopen("https://sis.rutgers.edu/soc/subjects.json?semester=%s&campus=NB&level=UG"%(semester))
subjects = json.loads(url.read())

for subject in subjects:
	url = urllib2.urlopen("http://sis.rutgers.edu/soc/courses.json?semester=%s&subject=%s&campus=NB&level=UG"%(semester, str(subject["code"])))
	content = url.read()

	with open('static/data/Courses/%s.json'%str(subject["code"]), 'w') as outfile:
	    json.dump(json.loads(content), outfile)
	print "Scraped %s.json"%str(subject["code"])

with open('static/data/subjects.json', 'w') as outfile:
    json.dump(subjects, outfile)
print "Scraped subjects.json"
