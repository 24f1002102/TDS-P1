import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key[:10]}...")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say 'Hello, TDS Project!'"}],
    "max_tokens": 50
}

try:
    response = requests.post(
        "https://aipipe.org/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    print("✅ OpenAI API connection successful!")
    print("Response:", response.json()["choices"][0]["message"]["content"])
except Exception as e:
    print(f"❌ Error: {e}")
