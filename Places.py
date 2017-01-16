import json
import os
# import urllib2

BUILDING='Buildings.json'

def location(code):
	# url="https://raw.githubusercontent.com/jennpeare/cs_capstone/master/data/buildings.json"

	# places = json.load(urllib2.urlopen(url))

    places = json.load(open(BUILDING))

    for item in places:
    	if item["code"] == code:
        	return item['name']
    return code

if __name__ == "__main__":
    print location("HLL")
