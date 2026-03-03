# EduGen AI (Multimodal GenAI Education)

EduGen AI is a production-ready, multimodal Generative AI application designed to transform any topic into a structured, highly visual "Concept Pack". By targeting specific grade levels, it tailors complex concepts into easy-to-understand narratives, visual flashcards, and structured data suitable for presentations.

## ✨ Features

- **Tailored Learning:** Generate content dynamically adapted to specific grade levels (Elementary, High School, College, Professional).
- **Multimodal Generation:**
  - **Text:** Comprehensive learning narratives and structured concept breakdowns using Google Gemini.
  - **Images:** High-fidelity visual flashcards and diagrams generated via an Image Generation API to complement the text.
- **Structured Concept Packs:** Outputs structured JSON containing narrative text, key concepts with images, detailed explanations, and summary points.
- **Modern User Interface:** A sleek, responsive, and dynamic frontend built with Streamlit, featuring a dark-themed UI, session history management, and polished aesthetics.
- **Optimized Performance:** In-memory caching for content and images to avoid repeated API calls and ensure fast response times.
- **Vector Search Ready:** Uses ChromaDB with SentenceTransformers embeddings for semantic search capabilities.

## 🏗️ Architecture

- **Frontend:** [Streamlit](https://streamlit.io/) for a highly interactive and aesthetically pleasing user interface.
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) providing robust REST APIs (`/generate-content`, `/generate-image`).
- **LLM Engine:** [Google Gemini](https://ai.google.dev/) for generating educational text and structuring data.
- **Image Engine:** Custom Image Generation API for generating educational visuals.

## 🚀 Setup & Installation

### 1. Environment Setup

Create a virtual environment and install the required dependencies:

```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory and add your API keys:

```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
IMAGE_API_KEY=your_image_api_key_here
IMAGE_MODEL=provider-4/imagen-4
IMAGE_BASE_URL=https://api.a4f.co/v1
VECTOR_DB_PATH=./vector_store
LOG_LEVEL=INFO
```

### 3. Start the Backend Server

Run the FastAPI backend using `uvicorn`:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend API will be available at `http://127.0.0.1:8000`. You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

### 4. Start the Frontend Application

In a new terminal, activate your virtual environment and run the Streamlit app:

```bash
streamlit run frontend/app.py
```

The application will open in your default web browser (typically at `http://localhost:8501`).

## 💡 Sample Prompts

Try these topics with different grade levels to see how the content adapts:

- _Explain Transformer architecture in NLP_ (College / Professional)
- _Photosynthesis_ (Elementary / High School)
- _Newton's Laws of Motion_ (High School)
- _The Water Cycle_ (Elementary)
- _Quantum Computing_ (College)

## 📝 Notes & Development

- The application uses custom CSS injection in Streamlit to achieve a premium, dark-mode visual experience reminiscent of high-end AI tools.
- Generated images and content are cached to optimize API usage and latency.
- Make sure you have valid API keys from Google and your Image API provider for full functionality.
