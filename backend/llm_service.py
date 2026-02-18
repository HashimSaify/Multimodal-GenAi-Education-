import os
import json
from functools import lru_cache
from typing import Optional
from huggingface_hub import InferenceClient

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
    # Handle cases where model adds extra conversational text
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
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    # Llama-3.3-70B-Instruct is confirmed available via the router
    model_name = os.getenv("HUGGINGFACE_TEXT_MODEL", "meta-llama/Llama-3.3-70B-Instruct")

    if not api_key:
        raise RuntimeError("HUGGINGFACE_API_KEY is not set")

    client = InferenceClient(api_key=api_key)
    prompt = build_prompt(topic, grade_level or None)
    
    # Using chat_completion for instruct models is usually more reliable
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat_completion(
            messages=messages,
            model=model_name,
            max_tokens=1000,
            temperature=0.7
        )
        text_out = response.choices[0].message.content
        return _safe_json(text_out)
    except Exception as e:
        # Fallback to text_generation if chat_completion fails or is not supported
        try:
            hf_prompt = f"<s>[INST] {prompt} [/INST]"
            text_out = client.text_generation(
                hf_prompt,
                model=model_name,
                max_new_tokens=1000,
                temperature=0.7
            )
            return _safe_json(text_out)
        except Exception as inner_e:
            raise RuntimeError(f"Hugging Face request failed: {e} | {inner_e}")


def generate_content(topic: str, grade_level: Optional[str]) -> GenerateContentResponse:
    data = _cached_generate_content(topic, grade_level or "")
    return GenerateContentResponse(**data)
