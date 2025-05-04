#!/usr/bin/env python3
"""
Deployment script for the database-backed customer service agent and Streamlit app.
"""

import os
import argparse
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Deploy the database-backed customer service agent')
parser.add_argument('--project', type=str, help='Google Cloud project ID')
parser.add_argument('--location', type=str, default='us-central1', help='Google Cloud location')
parser.add_argument('--agent-name', type=str, default='customer-service-db-agent', help='Agent name')
parser.add_argument('--streamlit-name', type=str, default='customer-service-db-streamlit', help='Streamlit app name')
parser.add_argument('--local-only', action='store_true', help='Only run locally, don\'t deploy to Cloud Run')
args = parser.parse_args()

# Directories
ROOT_DIR = Path(__file__).parent.parent
DEPLOYMENT_DIR = ROOT_DIR / 'deployment'
DATABASE_DIR = ROOT_DIR / 'database'

def create_dockerfile(app_type, output_file):
    """Create a Dockerfile for the specified application type."""
    if app_type == 'agent':
        content = """
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install poetry && \\
    poetry config virtualenvs.create false && \\
    poetry install --no-dev

# Copy application code
COPY . .

# Ensure database directory exists
RUN mkdir -p /app/database/data

# Initialize the database
RUN python -m database.init_db

# Expose port for the agent
EXPOSE 8080

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Command to run the agent
CMD ["python", "run_db_agent.py"]
"""
    elif app_type == 'streamlit':
        content = """
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install poetry && \\
    poetry config virtualenvs.create false && \\
    poetry install --no-dev

# Copy application code
COPY . .

# Ensure database directory exists
RUN mkdir -p /app/database/data

# Expose port for Streamlit
EXPOSE 8501

# Environment variables
ENV PORT=8501
ENV PYTHONUNBUFFERED=1
ENV AGENT_BASE_URL="https://AGENT_URL"

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_app_db.py", "--server.port=$PORT", "--server.address=0.0.0.0"]
"""
    else:
        raise ValueError(f"Unknown app type: {app_type}")
    
    with open(output_file, 'w') as f:
        f.write(content.strip())
    
    logger.info(f"Created Dockerfile for {app_type} at {output_file}")

def run_locally():
    """Run the database-backed agent and Streamlit app locally."""
    # Initialize the database
    logger.info("Initializing database...")
    subprocess.run(["python", "-m", "database.init_db"], check=True)
    
    # Start the agent in the background
    logger.info("Starting agent...")
    agent_process = subprocess.Popen(["python", "run_db_agent.py"])
    
    # Start the Streamlit app
    logger.info("Starting Streamlit app...")
    try:
        subprocess.run(["streamlit", "run", "streamlit_app_db.py"], check=True)
    finally:
        # Clean up the agent process
        logger.info("Stopping agent...")
        agent_process.terminate()

def deploy_to_cloud_run():
    """Deploy the agent and Streamlit app to Cloud Run."""
    # Check if project and location are provided
    if not args.project:
        logger.error("Project ID is required for Cloud Run deployment")
        return
    
    # Create agent Dockerfile
    agent_dockerfile = DEPLOYMENT_DIR / "Dockerfile.agent"
    create_dockerfile('agent', agent_dockerfile)
    
    # Create streamlit Dockerfile
    streamlit_dockerfile = DEPLOYMENT_DIR / "Dockerfile.streamlit"
    create_dockerfile('streamlit', streamlit_dockerfile)
    
    # Build and deploy agent
    logger.info(f"Building and deploying agent to Cloud Run in {args.project}...")
    agent_image = f"gcr.io/{args.project}/{args.agent_name}"
    
    # Build the agent image
    subprocess.run([
        "gcloud", "builds", "submit", 
        "--project", args.project,
        "--tag", agent_image,
        "--dockerfile", str(agent_dockerfile),
        str(ROOT_DIR)
    ], check=True)
    
    # Deploy the agent to Cloud Run
    subprocess.run([
        "gcloud", "run", "deploy", args.agent_name,
        "--project", args.project,
        "--image", agent_image,
        "--platform", "managed",
        "--region", args.location,
        "--allow-unauthenticated",
        "--memory", "1Gi"
    ], check=True)
    
    # Get the agent URL
    agent_url_result = subprocess.run([
        "gcloud", "run", "services", "describe", args.agent_name,
        "--project", args.project,
        "--region", args.location,
        "--format", "value(status.url)"
    ], capture_output=True, text=True, check=True)
    
    agent_url = agent_url_result.stdout.strip()
    logger.info(f"Agent deployed to {agent_url}")
    
    # Update the Streamlit Dockerfile with the agent URL
    with open(streamlit_dockerfile, 'r') as f:
        content = f.read()
    
    content = content.replace("AGENT_URL", agent_url)
    
    with open(streamlit_dockerfile, 'w') as f:
        f.write(content)
    
    # Build and deploy Streamlit app
    logger.info(f"Building and deploying Streamlit app to Cloud Run in {args.project}...")
    streamlit_image = f"gcr.io/{args.project}/{args.streamlit_name}"
    
    # Build the Streamlit image
    subprocess.run([
        "gcloud", "builds", "submit", 
        "--project", args.project,
        "--tag", streamlit_image,
        "--dockerfile", str(streamlit_dockerfile),
        str(ROOT_DIR)
    ], check=True)
    
    # Deploy the Streamlit app to Cloud Run
    subprocess.run([
        "gcloud", "run", "deploy", args.streamlit_name,
        "--project", args.project,
        "--image", streamlit_image,
        "--platform", "managed",
        "--region", args.location,
        "--allow-unauthenticated",
        "--memory", "1Gi",
        "--set-env-vars", f"AGENT_BASE_URL={agent_url}"
    ], check=True)
    
    # Get the Streamlit URL
    streamlit_url_result = subprocess.run([
        "gcloud", "run", "services", "describe", args.streamlit_name,
        "--project", args.project,
        "--region", args.location,
        "--format", "value(status.url)"
    ], capture_output=True, text=True, check=True)
    
    streamlit_url = streamlit_url_result.stdout.strip()
    logger.info(f"Streamlit app deployed to {streamlit_url}")
    
    logger.info("Deployment complete!")
    logger.info(f"Agent URL: {agent_url}")
    logger.info(f"Streamlit URL: {streamlit_url}")

if __name__ == "__main__":
    if args.local_only:
        run_locally()
    else:
        deploy_to_cloud_run()