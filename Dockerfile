FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files for the Streamlit app
COPY requirements.txt .
COPY README.md .
COPY better-sale-logo.png .
COPY streamlit_app_refactored.py .
COPY streamlit_components/ ./streamlit_components/
COPY customer_service/ ./customer_service/
COPY iamges/ ./iamges/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the database directory writable
RUN chmod -R 777 customer_service/database

# Set environment variables (will be overridden by Cloud Run)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default values that can be overridden at runtime
ENV AGENT_BASE_URL=https://customer-service-agent-190206934161.us-central1.run.app
ENV AGENT_APP_NAME=customer-service-agent-app

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "streamlit_app_refactored.py", "--server.port=8501", "--server.address=0.0.0.0"]