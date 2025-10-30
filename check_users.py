from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/stock_app")
db = client['stock_app']
users = db['users'].find()
for user in users:
    print(user)