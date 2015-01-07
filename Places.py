# from urllib import urlopen
import json
from google.appengine.api import urlfetch

def loc():
	print "What building are you near?"
	building=(raw_input()).lower()
	if building=='rsc' or building=="casc" or building=='rcs' or building=='cacc' or building=='college ave student center' or building=='college ave campus center':
		building='rutgers student center'
	elif building=='bsc'or building=='bcc' or building=='busch student center':
		building='busch campus center'
	elif building=='lsc' or building=='lcs' or building=='livingston campus center':
		building='livingston student center'
	elif building=='hill' or building=='hill center':
		building='Hill Center Bldg for the Mathematical Sciences'.lower()
	
	url="https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt"
	result = urlfetch.fetch(url)
	places = json.loads(result.content)

	# jsonurl = urlopen("https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt")
	# places=json.loads(jsonurl.read())

	for location in places['all']:
		if (places['all'][location]['title']).lower()==building:
			print "The %s is located on %s Campus"%(places['all'][location]['title'],places['all'][location]['campus_name'])
			print "It is located on: \t%s\n\t\t\t%s\n\t\t\t%s, %s\n\t\t\t%s"%(places['all'][location]['location']['name'],places['all'][location]['location']['street'],places['all'][location]['location']['city'],places['all'][location]['location']['state_abbr'],places['all'][location]['location']['postal_code'])
			if not places['all'][location]['description']== "":
				print 'Description: %s'%(places['all'][location]['description'])

def location(building_code):
	url="https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt"
	result = urlfetch.fetch(url)
	places = json.loads(result.content)
	# jsonurl = urlopen("https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt")
	# places=json.loads(jsonurl.read())

	found=False
	for location in places['all']:
		if 'building_code' in places['all'][location] and places['all'][location]['building_code']==building_code:
			return places['all'][location]['title']

# print location("HLL")
