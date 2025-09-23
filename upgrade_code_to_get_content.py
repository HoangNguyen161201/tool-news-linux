from untils import func_to_string
from db_mongodb import get_collect

def get_info_new(url):
    import requests
    from bs4 import BeautifulSoup
    from collections import defaultdict
    import re
    from urllib.parse import urlparse
    
    def normalize_img_url(url):
        # Bỏ query string, chỉ lấy tên file cuối
        clean_url = urlparse(url).path.split("/")[-1]
        # Bỏ số kích thước kiểu -640w
        return re.sub(r"-\d+w", "", clean_url)

    def extract_images(container):
        images = {}

        # Regex tìm URL có đuôi ảnh
        pattern = re.compile(r"https?://[^\s\"']+\.(?:jpg|jpeg|png|gif|webp|avif|svg)(?:\?[^\s\"']*)?", re.IGNORECASE)

        # Quét toàn bộ text trong container
        for match in pattern.findall(str(container)):
            key = normalize_img_url(match)
            images[key] = match  # ghi đè => giữ link cuối (thường to nhất)

        return list(images.values())


    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")

    # Bỏ qua script/style
    for bad in soup(["script", "style", "noscript", "iframe"]):
        bad.decompose()

    # Tìm tất cả p
    p_tags = soup.find_all("p")

    # Gom theo cha (dùng p để xác định cha chính)
    scores = defaultdict(int)
    for p in p_tags:
        parent = p.find_parent()
        if parent:
            scores[parent] += len(p.get_text(strip=True))

    # Thẻ cha chứa nhiều text nhất
    best_parent = max(scores, key=scores.get)

    # Lấy toàn bộ text từ các thẻ con quan trọng (không chỉ <p>)
    allowed_tags = {"p", "h1", "h2", "h3", "h4", "li", "blockquote"}

    content = ''

    for child in best_parent.find_all(allowed_tags):
        text = child.get_text(strip=True)
        if text:
            content += text
            
    article_images = extract_images(best_parent)
    title = soup.find("title").get_text()
    description = None
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        description = meta_tag.get('content', None)
    print(description)

    def extract_tags(soup):
        candidates = [
            {"attr": "property", "value": "article:tag"},
            {"attr": "name", "value": "keywords"},
            {"attr": "name", "value": "news_keywords"},
            {"attr": "property", "value": "article:section"},
            {"attr": "name", "value": "tags"},
        ]

        tags = []

        for c in candidates:
            metas = soup.find_all("meta", attrs={c["attr"]: c["value"]})
            for m in metas:
                content = m.get("content")
                if content:
                    # tách nếu có nhiều tag phân cách bằng dấu phẩy
                    parts = [x.strip() for x in content.split(",") if x.strip()]
                    tags.extend(parts)

        return list(set(tags))
    
    tags = extract_tags(soup)
    
    if(article_images is None or article_images.__len__() == 0 ):
        return None
    
    return {
        "content": content,
        "title": title,
        "description": description,
        "tags": tags,
        "picture_links": article_images
    }
    
func = func_to_string(get_info_new)

collect = get_collect('news', 'func_vn')
collect.insert_one({
    "func": func
})