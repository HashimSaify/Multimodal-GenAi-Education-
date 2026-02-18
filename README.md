# Multimodal GenAI Education

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Add your API keys in `.env`:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
HUGGINGFACE_API_KEY=your_hf_key_here
HUGGINGFACE_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
VECTOR_DB_PATH=./vector_store
LOG_LEVEL=INFO
```

3. Start backend:

```bash
uvicorn backend.main:app --reload
```

4. Start frontend:

```bash
streamlit run frontend/app.py
```

## Sample Prompts
- Explain Transformer architecture in NLP
- Photosynthesis
- Newton's Laws of Motion

## Notes
- Content and images are cached in-memory to avoid repeated API calls.
- Vector search uses ChromaDB with SentenceTransformers embeddings.
