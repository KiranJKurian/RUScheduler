# from urllib import urlopen
import json
from google.appengine.api import urlfetch

def location(building_code):
	url="https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt"
	result = urlfetch.fetch(url)
	places = json.loads(result.content)
	# jsonurl = urlopen("https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt")
	# places=json.loads(jsonurl.read())

	found=False
	for location in places['all']:
		if 'building_code' in places['all'][location] and places['all'][location]['building_code']==building_code:
			if places['all'][location]['title']=="Hill Center Bldg for the Mathematical Sciences":
				return "Hill Center"
			else:
				return places['all'][location]['title']
	return building_code