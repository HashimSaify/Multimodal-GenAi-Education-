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
    model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    # Native endpoint uses models/{model}:generateContent
    base_url = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

    if not api_key:
        raise RuntimeError("LLM_API_KEY is not set in environment")

    headers = {
        "Content-Type": "application/json"
    }
    
    # Ensure model_name doesn't already have 'models/' prefix
    if not model_name.startswith("models/"):
        model_path = f"models/{model_name}"
    else:
        model_path = model_name

    url = f"{base_url.rstrip('/')}/{model_path}:generateContent?key={api_key}"

    # Step 1: Validate Topic
    val_payload = {
        "contents": [{
            "parts": [{"text": build_validation_prompt(topic)}]
        }],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    try:
        val_res = requests.post(url, headers=headers, json=val_payload, timeout=30)
        if val_res.status_code == 200:
            val_text = val_res.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
            if "NO" in val_text and "YES" not in val_text:
                return {
                    "error": "This topic does not appear to be related to education. Please ask about an academic subject, concept, or formal skill."
                }
            if "NO" in val_text and "YES" in val_text:
                if val_text.startswith("NO"):
                    return {
                        "error": "This topic does not appear to be related to education. Please ask about an academic subject, concept, or formal skill."
                    }
    except Exception:
        pass

    # Step 2: Generate Content
    prompt = build_prompt(topic, grade_level or None)
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        text_out = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _safe_json(text_out)
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            err_msg += f" - Response: {e.response.text}"
        raise RuntimeError(f"Gemini API request failed: {err_msg}")


def generate_content(topic: str, grade_level: Optional[str]) -> GenerateContentResponse:
    data = _cached_generate_content(topic, grade_level or "")
    return GenerateContentResponse(**data)
