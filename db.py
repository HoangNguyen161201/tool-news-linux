from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# -------------- links news
def get_all_links():
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["news"]
    collection = db["links"]
    # Truy vấn tất cả các tài liệu và chỉ lấy trường "link"
    links = [doc["link"] for doc in collection.find({}, {"link": 1, "_id": 0})]
    return links

   
def check_link_exists(link):
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["news"]
    collection = db["links"]
    return collection.find_one({"link": link}) is not None
    

def insert_link(link):
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["news"]
    collection = db["links"]
    collection.insert_one({"link": link})

def delete_link(link):
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["news"]
    collection = db["links"]
    collection.delete_one({"link": link})