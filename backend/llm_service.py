import os
import json
import requests
from functools import lru_cache
from typing import Optional

from .schemas import GenerateContentResponse
from utils.prompts import build_prompt, build_validation_prompt


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
        data = json.loads(cleaned)
        if isinstance(data, dict) and "flashcards" in data and isinstance(data["flashcards"], list):
            new_fc = []
            for item in data["flashcards"]:
                if isinstance(item, dict):
                    q = item.get("question", "") or item.get("front", "") or item.get("term", "")
                    a = item.get("answer", "") or item.get("back", "") or item.get("definition", "")
                    if q and a:
                        new_fc.append(f"**{q}**<br>{a}")
                    else:
                        new_fc.append(str(item))
                else:
                    new_fc.append(str(item))
            data["flashcards"] = new_fc
        return data
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = f"{base_url.rstrip('/')}/chat/completions"

    # Step 1: Validate Topic
    val_payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": build_validation_prompt(topic)}],
        "max_tokens": 5,
        "temperature": 0.0
    }
    try:
        val_res = requests.post(url, headers=headers, json=val_payload, timeout=10)
        if val_res.status_code == 200:
            val_text = val_res.json()["choices"][0]["message"]["content"].strip().upper()
            print(f"DEBUG VAL_TEXT for '{topic}': {val_text}")
            if "NO" in val_text and "YES" not in val_text:
                return {
                    "error": "This topic does not appear to be related to education. Please ask about an academic subject, concept, or formal skill."
                }
            if "NO" in val_text and "YES" in val_text:
                # If the model gives both YES and NO, we lean towards NO since it's confused
                if val_text.startswith("NO"):
                    return {
                        "error": "This topic does not appear to be related to education. Please ask about an academic subject, concept, or formal skill."
                    }
    except Exception as e:
        print("DEBUG VAL ERROR:", e)
        pass # Fallback to generation if validation fails

    # Step 2: Generate Content
    prompt = build_prompt(topic, grade_level or None)
    messages = [{"role": "user", "content": prompt}]
    
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
