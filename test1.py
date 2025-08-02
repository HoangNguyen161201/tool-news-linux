from untils import generate_content
from data import gemini_keys
data = generate_content('tôi tên là hoàng, chuyển sang tiếng anh', model='gemini-1.5-flash', api_key= gemini_keys[0] )
print(data)