import logging
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    GenerateContentRequest,
    GenerateContentResponse,
    GenerateImageRequest,
    StoreVectorRequest,
    SearchRequest,
    SearchResponse,
)
from .llm_service import generate_content
from .image_service import generate_images
from .vector_db import VectorDB

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal GenAI Education")

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")
vector_db = VectorDB(persist_path=VECTOR_DB_PATH)


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/generate-content", response_model=GenerateContentResponse)
def generate_content_endpoint(req: GenerateContentRequest):
    try:
        logger.info("Generating content for topic=%s grade=%s", req.topic, req.grade_level)
        content = generate_content(req.topic, req.grade_level)
        return content
    except Exception as e:
        logger.exception("Content generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-image")
def generate_image_endpoint(req: GenerateImageRequest):
    try:
        logger.info("Generating images for topic=%s grade=%s", req.topic, req.grade_level)
        images = generate_images(req.topic, req.grade_level)
        return images
    except Exception as e:
        logger.exception("Image generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/store-vector")
def store_vector_endpoint(req: StoreVectorRequest):
    try:
        logger.info("Storing vector for prompt=%s", req.prompt)
        vector_db.add_document(req.prompt, req.explanation)
        return {"status": "stored"}
    except Exception as e:
        logger.exception("Vector store failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
def search_endpoint(req: SearchRequest):
    try:
        logger.info("Searching vectors query=%s top_k=%s", req.query, req.top_k)
        results = vector_db.search(req.query, top_k=req.top_k)
        return SearchResponse(results=results)
    except Exception as e:
        logger.exception("Vector search failed")
        raise HTTPException(status_code=500, detail=str(e))
