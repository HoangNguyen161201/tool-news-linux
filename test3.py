import requests
from bs4 import BeautifulSoup
from untils import get_func_Website_to_create
from db import insert_or_update_website 

insert_or_update_website('theguardian')
data = get_func_Website_to_create()
links = data['get_links']()
print(data['get_info'](links[0]))
