import urllib
import urllib2
from bs4 import BeautifulSoup
from dateutil.parser import parse
import sys

def get_redirected_url(url):
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

url = "https://finalexams.rutgers.edu/"

def getFinalDate(index, campus = "nb"):
	values = {"degree_level":"U","campus": campus.lower(),"subject": "","course": "","index": index}
	data = urllib.urlencode(values)
	newUrl = get_redirected_url("%s?%s"%(url, data))
	response = urllib2.urlopen(newUrl)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	indexedDate = None
	try:
		for tr in soup.find_all('tr')[1:]:
			tds = tr('td')
			if len(tds) >= 4 and str(tds[0].string) == index:
				indexedDate = {'index': str(tds[0].string), 'date': str(tds[-1].string)}
		if indexedDate:
			dateIndexSplit = indexedDate['date'].index(':')
			date = indexedDate['date'][:dateIndexSplit].strip()
			times = indexedDate['date'][dateIndexSplit + 1:].split('-')
			return { 'startTime': parse("%s %s"%(date, times[0].strip())), 'endTime': parse("%s %s"%(date, times[1].strip())) }
	except Exception as e:
		return { 'error': e }

if __name__ == "__main__":
	if len(sys.argv) > 1:
	    print getFinalDate(sys.argv[1])
	else:
		prinProgFinal = getFinalDate("00198")
		print prinProgFinal

