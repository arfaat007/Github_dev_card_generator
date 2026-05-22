FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies and install
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
