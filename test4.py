import google.generativeai as genai

genai.configure(api_key='AIzaSyAWzlnFgRmr_6nddTqQeJgSr1DIPb32W6M')

models = genai.list_models()
for m in models:
    # bạn có thể lọc những model có hỗ trợ generateContent
    if 'generateContent' in m.supported_generation_methods:
        print(m.name, m.description, m.supported_generation_methods)