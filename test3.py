from untils import func_to_string, get_info_new_kenh14_star
from db_mongodb import get_collect
import requests
from bs4 import BeautifulSoup

# def get_all_link_new():
#     url = 'https://kenh14.vn/star.chn'
#     headers = {
#         'User-Agent': 'Mozilla/5.0'
#     }

#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     link = []
    

#     # Lọc các thẻ <a> thỏa điều kiện
#     for a in soup.find_all('a', href=True, class_='ktncli-ava'):
#         link.append(f'https://kenh14.vn{a['href']}')
    
#     return link

# def get_info_new(url):
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0'
#         }

#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # title, description and content
#         title = None
#         meta_tag = soup.find('meta', attrs={'property': 'og:title'})
#         if meta_tag:
#             title = meta_tag.get('content', None)

#         description = None
#         meta_tag = soup.find('meta', attrs={'name': 'description'})
#         if meta_tag:
#             description = meta_tag.get('content', None)
            

#         tags = None
#         meta_tag = soup.find('meta', attrs={'name': 'keywords'})
#         if meta_tag:
#             tags = meta_tag.get('content', None)
            

#         content = soup.find('div', {'class': 'detail-content'}).get_text(strip=True)

        
#         # pictures
#         pictures = soup.find_all('img', attrs={'type': 'photo'})
#         picture_links = [img['src'] for img in pictures if img.has_attr('src')]

#         if len(picture_links) == 0 or content is None:
#             return None
        
#         return {
#             "content": content,
#             "title": title,
#             "description": description,
#             "tags": tags,
#             "picture_links": picture_links
#         }
#     except:
#       return None

# func = func_to_string(get_all_link_new) 
# func2 = func_to_string(get_info_new)

collect = get_collect('news', 'func_vn')
# collect.insert_one({
#     "func": func,
#     "func2": func2
# })

# data =  collect.find({}, {})
# docs = list(data)
# for doc in docs:
#     exec(doc['func'])
#     exec(doc['func2'])
#     result = get_all_link_new()
#     data = get_info_new(result[0])
#     print(data)