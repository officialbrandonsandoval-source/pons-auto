FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY pyproject.toml .

# Install the application
RUN pip install -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "shiftly.main:app", "--host", "0.0.0.0", "--port", "8000"]
