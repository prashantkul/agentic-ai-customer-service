"""
Configuration settings for the Streamlit app.
"""

import os
import logging

# --- Configuration ---
AGENT_BASE_URL = os.getenv(
    "AGENT_BASE_URL", "https://customer-service-agent-190206934161.us-central1.run.app"
)
AGENT_RUN_PATH = "/run_sse"
AGENT_SESSION_PATH_TEMPLATE = "/apps/{app_name}/users/{user_id}/sessions/{session_id}"
AGENT_APP_NAME = os.getenv("AGENT_APP_NAME", "customer-service-agent-app")
# AUTH_TOKEN = os.getenv("AGENT_AUTH_TOKEN") # Uncomment if needed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)