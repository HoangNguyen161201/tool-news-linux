import requests
from bs4 import BeautifulSoup
from untils import get_func_Website_to_create

data = get_func_Website_to_create()
print(data)
links = data['get_links']()
print(data['get_info'](links[0]))
