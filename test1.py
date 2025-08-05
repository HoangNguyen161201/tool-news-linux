import google.generativeai as genai
from data import gemini_keys
genai.configure(api_key=gemini_keys[0])

models = genai.list_models()
for m in models:
    print(m.name)