import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("Checking available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Found model: {m.name}")
