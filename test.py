from pymongo import MongoClient
from pymongo.server_api import ServerApi

def get_collect(name_db, name_collection):
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[name_db]
    collection = db[name_collection]
    return collection

# kiểm tra collection
collection = get_collect("news", "links")

# tìm document có trường 'link' chứa 'afamily'
result = collection.find({"link": {"$regex": "afamily", "$options": "i"}})

count = 0
for doc in result:
    print(doc)
    count += 1

if count == 0:
    print("Không tìm thấy")