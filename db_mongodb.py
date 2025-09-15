from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import socket

# -----connect db and return collect
def get_collect(name_db, name_collection):
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[name_db]
    collection = db[name_collection]
    return collection

# -------------- links news
def get_all_links():
    collection = get_collect('news', 'links')
    # Truy vấn tất cả các tài liệu và chỉ lấy trường "link"
    links = [doc["link"] for doc in collection.find({}, {"link": 1, "_id": 0})]
    return links

def check_authorization():
    collection = get_collect('news', 'authorization')
    return collection.find_one({"password": "Cuem161201@"}) is not None
   
def check_link_exists(link):
    collection = get_collect('news', 'links')
    return collection.find_one({"link": link}) is not None
    

def insert_link(link):
    collection = get_collect('news', 'links')
    collection.insert_one({"link": link})

def delete_link(link):
    collection = get_collect('news', 'links')
    collection.delete_one({"link": link})

def get_webiste(name):
    collection = get_collect('news', 'websites')
    return collection.find_one({"name": name})

def insert_or_update_website(name):
    collection = get_collect('news', 'websites')
    current_time = datetime.now()
    existing_website = collection.find_one({"name": name})

    if existing_website:
        # Nếu website đã tồn tại, cập nhật trường 'timestamp'
        collection.update_one(
            {"name": name},  # Điều kiện tìm kiếm
            {"$set": {"timestamp": current_time}}  # Cập nhật timestamp
        )
    else:
        # Nếu website không tồn tại, tạo mới
        new_website = {
            "name": name,
            "timestamp": current_time
        }
        collection.insert_one(new_website)
        
# --------------------------------- ips
def check_not_exist_to_create_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    data = collection.find_one({"ip": local_ip})

    if data is False or data is None:
        collection.insert_one({
            "ip": local_ip,
            "youtubes": [],
            "geminiKeys": [],
            "driverPath": "C:/Program Files/Google/Chrome/Application/chrome.exe"
        })

    
def find_one_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    return collection.find_one({"ip": local_ip})

def check_exist_youtube_in_ip(name_chrome_yt):
    data = find_one_ip()
    if name_chrome_yt in data.get("youtubes", []):
        return True
    return False

   
def update_driver_path_to_ip(driver_path):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    collection.update_one(
        {"ip": local_ip},
        {"$set": {"driverPath": driver_path}}
    )
    
def add_youtube_to_ip(name_chrome_yt):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    collection.update_one(
        {"ip": local_ip},
        {"$push": {"youtubes": name_chrome_yt}}
    )
    
def remove_youtube_to_ip(name_chrome_yt):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    collection.update_one(
        {"ip": local_ip},
        {"$pull": {"youtubes": name_chrome_yt}}
    )
   
def add_gemini_key_to_ip(key):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    collection.update_one(
        {"ip": local_ip},
        {"$push": {"geminiKeys": key}}
    )
    
def remove_gemini_key_youtube_to_ip(key):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    collection = get_collect('news', 'ips')
    collection.update_one(
        {"ip": local_ip},
        {"$pull": {"geminiKeys": key}}
    )
    

   

    