FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install uv (fast pip wrapper)
RUN pip install --no-cache-dir uv

# Copy backend requirements and install them
COPY backend/requirements.txt ./
RUN uv pip install --system -r requirements.txt

# Copy backend source code
COPY backend/ .

# Copy the frontend assets (needed for the UI mount)
COPY frontend/ ./frontend

# Expose the port Cloud Run will set via $PORT (default 8080 for local testing)
EXPOSE 8080

# Run the FastAPI app
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
