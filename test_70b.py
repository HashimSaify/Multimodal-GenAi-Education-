import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL", "https://api.cerebras.ai/v1")

headers = {
    "Authorization": f"Bearer {api_key}"
}

r = requests.get(f"{base_url}/models", headers=headers)
try:
    print(", ".join([m["id"] for m in r.json().get("data", [])]))
except Exception as e:
    print(r.text)
