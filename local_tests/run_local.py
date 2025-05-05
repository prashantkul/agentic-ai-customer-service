
"""
Script to run the Streamlit app locally in a simplified way.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run the Streamlit app locally."""
  
    
    # Start the Streamlit app
    logger.info("Starting Streamlit app...")
    try:
        subprocess.run([
            "streamlit", "run", "streamlit_app_db.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    finally:
        # Clean up the agent process
        logger.info("Stopping agent...")
        agent_process.terminate()
        agent_process.wait(timeout=5)

if __name__ == "__main__":
    main()