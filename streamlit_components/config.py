"""
Configuration settings for the Streamlit app.
"""

import os
import logging
from pathlib import Path

# Try to import dotenv and load environment variables
try:
    from dotenv import load_dotenv
    # Look for .env file in the repository root
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.info(f"Loaded environment variables from {env_path}")
except ImportError:
    logging.warning("python-dotenv not installed. Environment variables must be set manually.")

# --- Configuration ---
# For local development: "http://localhost:8080"
# For Cloud Run: "https://customer-service-agent-190206934161.us-central1.run.app" 
AGENT_BASE_URL = os.getenv(
    "AGENT_BASE_URL", "http://localhost:8080"
)
AGENT_RUN_PATH = "/run_sse"
AGENT_SESSION_PATH_TEMPLATE = "/apps/{app_name}/users/{user_id}/sessions/{session_id}"
AGENT_APP_NAME = os.getenv("AGENT_APP_NAME", "customer-service-agent-app")
# AUTH_TOKEN = os.getenv("AGENT_AUTH_TOKEN") # Uncomment if needed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Log the configuration
logger.info("====== STREAMLIT APP CONFIGURATION ======")
logger.info(f"Agent Base URL: {AGENT_BASE_URL}")
logger.info(f"Agent App Name: {AGENT_APP_NAME}")
logger.info(f"Agent Run Path: {AGENT_RUN_PATH}")
logger.info(f"Agent Session Path Template: {AGENT_SESSION_PATH_TEMPLATE}")
logger.info("=========================================")