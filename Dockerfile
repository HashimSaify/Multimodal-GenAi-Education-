# Use a lightweight official Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /app

# Install system dependencies (optional, but good for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies strictly
# (Caching leverage: if requirements.txt hasn't changed, Docker reuses the cached layer for this step)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual application code
COPY backend/ ./backend/
COPY utils/ ./utils/

# Expose the port (Render uses $PORT, but defaults to 10000)
# The EXPOSE instruction is mostly documentation, the actual mapping is handled by Render
EXPOSE 8000

# Start the FastAPI application via Uvicorn
# We use $PORT so it dynamically binds to whatever port Render provides, defaulting to 8000
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
