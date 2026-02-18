import os
import base64
from functools import lru_cache
from typing import Optional
from huggingface_hub import InferenceClient


def _call_hf(prompt: str) -> str:
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    model_name = os.getenv(
        "HUGGINGFACE_IMAGE_MODEL",
        "stabilityai/stable-diffusion-xl-base-1.0",
    )

    if not api_key:
        raise RuntimeError("HUGGINGFACE_API_KEY is not set")

    client = InferenceClient(api_key=api_key)
    
    try:
        # text_to_image returns a PIL Image or bytes depending on usage
        image = client.text_to_image(prompt, model=model_name)
        # Convert PIL Image or bytes to base64
        import io
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Hugging Face image error: {e}")


@lru_cache(maxsize=64)
def _cached_generate_images(topic: str, grade_level: str):
    grade_text = f" for {grade_level} students" if grade_level else ""

    diagram_prompt = (
        f"Create a clean educational diagram about {topic}{grade_text}. "
        "Use labels, minimal colors, white background."
    )

    flashcard_prompt = (
        f"Create a flashcard-style educational visual about {topic}{grade_text}. "
        "Add a title and 2-3 labeled elements. White background."
    )

    diagram_b64 = _call_hf(diagram_prompt)
    flashcard_b64 = _call_hf(flashcard_prompt)

    return {
        "diagram_b64": diagram_b64,
        "flashcard_b64": flashcard_b64,
    }


def generate_images(topic: str, grade_level: Optional[str]):
    return _cached_generate_images(topic, grade_level or "")

