import os
import base64
import requests
from functools import lru_cache
from typing import Optional

def _call_custom_api(prompt: str) -> str:
    api_key = os.getenv("IMAGE_API_KEY")
    model_name = os.getenv("IMAGE_MODEL", "flux2-dev")
    base_url = os.getenv("IMAGE_BASE_URL", "https://api.infip.pro/v1")

    if not api_key:
        raise RuntimeError("IMAGE_API_KEY is not set in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    clean_base_url = base_url.split("/images/generations")[0].rstrip("/")
    url = f"{clean_base_url}/images/generations"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "response_format": "url"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        
        image_url = data["data"][0]["url"]
        
        # Download the image from the URL and convert to Base64
        image_res = requests.get(image_url, timeout=60)
        image_res.raise_for_status()
        return base64.b64encode(image_res.content).decode("utf-8")
        
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            err_msg += f" - Response: {e.response.text}"
        raise RuntimeError(f"Image API error: {err_msg}")


@lru_cache(maxsize=64)
def _cached_generate_images(topic: str, grade_level: str):
    grade_text = f" for {grade_level} students" if grade_level else ""

    diagram_prompt = (
        f"Create a clean educational diagram about {topic}{grade_text}. "
        "Use labels, minimal colors, white background."
    )

    diagram_b64 = _call_custom_api(diagram_prompt)

    return {
        "diagram_b64": diagram_b64,
        "flashcard_b64": None,
    }


def generate_images(topic: str, grade_level: Optional[str]):
    return _cached_generate_images(topic, grade_level or "")

