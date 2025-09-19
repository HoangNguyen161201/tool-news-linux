from newspaper import Article

url = "https://nld.com.vn/bao-chong-bao-tren-bien-dong-du-bao-1-con-bao-rat-manh-co-nguy-co-anh-huong-toi-nuoc-ta-196250919063451063.htm"
article = Article(url, language="vi")
article.download()
article.parse()

print("Tiêu đề:", article.title)
print("\nNội dung:\n", article.text)

# Hình ảnh chính (thường là ảnh đại diện/bìa bài báo)
print("\nẢnh chính:", article.top_image)

# Tất cả ảnh tìm thấy trong bài
print("\nDanh sách ảnh:")
for img in article.images:
    print(img)