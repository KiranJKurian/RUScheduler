from pymongo import MongoClient

client = MongoClient(port=27106)
db=client.spring16
db.brothers.remove()
