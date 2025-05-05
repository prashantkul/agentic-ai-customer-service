#!/usr/bin/env python3
"""
Simple script to start the database-backed customer service agent locally.
No Docker or cloud deployment required.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
import time
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set environment variables
def setup_environment(agent_port=8080):
    """Set up environment variables for the application."""
    os.environ["AGENT_BASE_URL"] = f"http://localhost:{agent_port}"
    os.environ["AGENT_APP_NAME"] = "customer-service-agent-app"
    
    # Try to load .env file if dotenv is available
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"Loaded environment variables from {env_path}")
    except ImportError:
        logger.info("python-dotenv not installed, using default environment settings")
    
    logger.info(f"Environment setup with AGENT_BASE_URL={os.environ['AGENT_BASE_URL']}")

def initialize_database():
    """Initialize the SQLite database with sample data."""
    logger.info("Initializing database...")
    try:
        from database.init_db import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

def test_database():
    """Run simple tests to verify database functionality."""
    logger.info("Testing database operations...")
    try:
        # Get customer
        from database.operations import get_customer
        customer = get_customer("123")
        if not customer:
            raise ValueError("Customer not found")
        logger.info(f"✅ Customer found: {customer['customer_first_name']} {customer['customer_last_name']}")
        
        # Access cart
        from database.operations import access_cart_information
        cart = access_cart_information("123")
        if not cart or "cart" not in cart:
            raise ValueError("Cart information not found")
        logger.info(f"✅ Cart accessed successfully with {len(cart['cart'])} items")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

def start_agent(agent_port=8080):
    """Start the database-backed agent."""
    logger.info(f"Starting agent on port {agent_port}...")
    try:
        # Set environment variable for the agent port
        env = os.environ.copy()
        env["PORT"] = str(agent_port)
        
        agent_process = subprocess.Popen(
            [sys.executable, "run_db_agent.py"],
            env=env
        )
        logger.info(f"✅ Agent started successfully on port {agent_port}")
        return agent_process
    except Exception as e:
        logger.error(f"❌ Failed to start agent: {e}")
        return None

def start_streamlit(port=8501, agent_port=8080):
    """Start the Streamlit app."""
    logger.info(f"Starting Streamlit app on port {port}...")
    try:
        # Set environment variables for Streamlit
        env = os.environ.copy()
        env["AGENT_BASE_URL"] = f"http://localhost:{agent_port}"
        
        streamlit_process = subprocess.Popen([
            "streamlit", "run", "streamlit_app_db.py",
            f"--server.port={port}",
            "--server.address=0.0.0.0"
        ], env=env)
        
        logger.info(f"✅ Streamlit app started on http://localhost:{port}")
        return streamlit_process
    except Exception as e:
        logger.error(f"❌ Failed to start Streamlit: {e}")
        return None

def run_services(streamlit_port=8501, agent_port=8080, agent_only=False, streamlit_only=False):
    """Run both the agent and Streamlit services."""
    processes = []
    
    # Setup environment
    setup_environment(agent_port=agent_port)
    
    # Initialize database
    if not initialize_database():
        logger.error("Aborting due to database initialization failure")
        return
    
    # Test database
    if not test_database():
        logger.warning("Database tests failed, but continuing with startup...")
    
    # Start agent if needed
    if not streamlit_only:
        agent_process = start_agent(agent_port=agent_port)
        if agent_process:
            processes.append(("Agent", agent_process))
            # Give the agent time to start up
            time.sleep(3)
        else:
            if not agent_only:
                logger.error("Aborting due to agent startup failure")
                return
    
    # Start Streamlit if needed
    if not agent_only:
        streamlit_process = start_streamlit(port=streamlit_port, agent_port=agent_port)
        if streamlit_process:
            processes.append(("Streamlit", streamlit_process))
        else:
            # Kill agent if Streamlit fails
            for name, process in processes:
                logger.info(f"Shutting down {name} due to Streamlit startup failure")
                process.terminate()
            logger.error("Aborting due to Streamlit startup failure")
            return
    
    # Print access URLs
    if not agent_only and streamlit_process:
        logger.info(f"\n🌐 The Streamlit app is now available at: http://localhost:{streamlit_port}")
    if not streamlit_only and agent_process:
        logger.info(f"🤖 The agent is running at: http://localhost:{agent_port}")
    
    # Keep the script running until interrupted
    logger.info("\n✨ Services started. Press Ctrl+C to stop.")
    try:
        for name, process in processes:
            process.wait()
    except KeyboardInterrupt:
        logger.info("\nShutting down services...")
    finally:
        # Terminate all processes
        for name, process in processes:
            logger.info(f"Terminating {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"{name} didn't terminate gracefully, killing...")
                process.kill()

def main():
    """Parse command line arguments and start services."""
    parser = argparse.ArgumentParser(description="Start database-backed customer service")
    parser.add_argument("--port", type=int, default=8501, help="Port for Streamlit app")
    parser.add_argument("--agent-port", type=int, default=8080, help="Port for the agent")
    parser.add_argument("--agent-only", action="store_true", help="Start only the agent")
    parser.add_argument("--streamlit-only", action="store_true", help="Start only the Streamlit app")
    args = parser.parse_args()
    
    if args.agent_only and args.streamlit_only:
        logger.error("Cannot specify both --agent-only and --streamlit-only")
        return
    
    run_services(
        streamlit_port=args.port,
        agent_port=args.agent_port,
        agent_only=args.agent_only,
        streamlit_only=args.streamlit_only
    )

if __name__ == "__main__":
    main()