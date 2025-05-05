#!/usr/bin/env python3
"""
Script to set up Docker files for the database-backed agent and Streamlit app.
"""

import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Directories
ROOT_DIR = Path(__file__).parent
DEPLOYMENT_DIR = ROOT_DIR / 'deployment'

def create_dockerfile(app_type, output_file):
    """Create a Dockerfile for the specified application type."""
    if app_type == 'agent':
        content = """FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure database directory exists
RUN mkdir -p /app/database/data

# Initialize the database
RUN python -m database.init_db

# Add health check endpoint
RUN echo 'import http.server, socketserver\\n\\nclass HealthHandler(http.server.BaseHTTPRequestHandler):\\n    def do_GET(self):\\n        if self.path == "/health":\\n            self.send_response(200)\\n            self.send_header("Content-type", "text/plain")\\n            self.end_headers()\\n            self.wfile.write(b"OK")\\n\\nwith socketserver.TCPServer(("", 8080), HealthHandler) as httpd:\\n    httpd.serve_forever()' > health_check.py

# Expose port for the agent
EXPOSE 8080

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Command to run the agent
CMD ["python", "run_db_agent.py"]
"""
    elif app_type == 'streamlit':
        content = """FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure database directory exists
RUN mkdir -p /app/database/data

# Expose port for Streamlit
EXPOSE 8501

# Environment variables
ENV PORT=8501
ENV PYTHONUNBUFFERED=1
ENV AGENT_BASE_URL="http://agent:8080"

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_app_db.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
    else:
        raise ValueError(f"Unknown app type: {app_type}")
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(content.strip())
    
    logger.info(f"Created Dockerfile for {app_type} at {output_file}")

def main():
    """Create Docker files."""
    logger.info("Setting up Docker environment...")
    
    # Create agent Dockerfile
    agent_dockerfile = DEPLOYMENT_DIR / "Dockerfile.agent"
    create_dockerfile('agent', agent_dockerfile)
    
    # Create streamlit Dockerfile
    streamlit_dockerfile = DEPLOYMENT_DIR / "Dockerfile.streamlit"
    create_dockerfile('streamlit', streamlit_dockerfile)
    
    logger.info(f"""
Docker environment set up successfully!

To run the application with Docker Compose:
1. Ensure Docker is installed and running
2. Run: docker-compose up

The Streamlit app will be available at http://localhost:8501
""")

if __name__ == "__main__":
    main()