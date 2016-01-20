from pymongo import MongoClient

client = MongoClient(port=27106)
db=client.spring16

cursor=db.brothers.find()
for document in cursor:
	print document
