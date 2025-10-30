from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['stock_app']
users = db['users'].find()
for user in users:
    print(user)