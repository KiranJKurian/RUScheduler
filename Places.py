import json
# import urllib2

def location(code):
	# url="https://raw.githubusercontent.com/jennpeare/cs_capstone/master/data/buildings.json"

	# places = json.load(urllib2.urlopen(url))

    places = json.load(open('buildings.json'))

    for item in places:
    	if item["code"] == code:
        	return item['name']
    return code

if __name__ == "__main__":
    print location("HLL")