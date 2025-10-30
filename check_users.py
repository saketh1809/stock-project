from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client['stock_app']
users = db['users'].find()
for user in users:
    print(user)