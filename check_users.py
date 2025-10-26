from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:admin@cluster0.tgpyua2.mongodb.net/")
db = client['stock_app']
users = db['users'].find()
for user in users:
    print(user)