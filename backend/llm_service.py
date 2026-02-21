import os
import json
import requests
from functools import lru_cache
from typing import Optional

from .schemas import GenerateContentResponse
from utils.prompts import build_prompt


def _safe_json(text: str) -> dict:
    if not text:
        return {
            "overview": "",
            "key_points": [],
            "real_world_example": "",
            "flashcards": [],
            "summary": "",
        }
    cleaned = text.strip()
    if "{" in cleaned:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start:end+1]
        
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned.replace("json", "", 1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "overview": cleaned,
            "key_points": [],
            "real_world_example": "",
            "flashcards": [],
            "summary": "",
        }


@lru_cache(maxsize=128)
def _cached_generate_content(topic: str, grade_level: str):
    api_key = os.getenv("LLM_API_KEY")
    model_name = os.getenv("LLM_MODEL", "llama3.1-8b")
    base_url = os.getenv("LLM_BASE_URL", "https://api.cerebras.ai/v1")

    if not api_key:
        raise RuntimeError("LLM_API_KEY is not set in .env")

    prompt = build_prompt(topic, grade_level or None)
    messages = [{"role": "user", "content": prompt}]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.3
    }

    try:
        url = f"{base_url.rstrip('/')}/chat/completions"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        text_out = response.json()["choices"][0]["message"]["content"]
        return _safe_json(text_out)
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            err_msg += f" - Response: {e.response.text}"
        raise RuntimeError(f"Cerebras LLM request failed: {err_msg}")


def generate_content(topic: str, grade_level: Optional[str]) -> GenerateContentResponse:
    data = _cached_generate_content(topic, grade_level or "")
    return GenerateContentResponse(**data)
