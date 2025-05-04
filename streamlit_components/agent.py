"""
Agent interaction component for the Streamlit app.
"""

import logging
import json
import streamlit as st
import sys

# Configure root logger to ensure messages appear in console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Ensure logs go to stdout for Streamlit
    ]
)

from streamlit_components.utils import call_agent_api, parse_sse_response, update_cart_display
from streamlit_components.config import (
    AGENT_BASE_URL, 
    AGENT_RUN_PATH, 
    AGENT_SESSION_PATH_TEMPLATE, 
    AGENT_APP_NAME
)
from streamlit_components.chat import is_cart_related_query

# Get logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add a console handler if one doesn't exist
has_stdout_handler = False
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
        has_stdout_handler = True
        break

if not has_stdout_handler:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Log startup message to verify logging is working
logger.info("==== STREAMLIT AGENT COMPONENT INITIALIZED ====")
logger.info(f"Agent Base URL: {AGENT_BASE_URL}")
logger.info(f"Agent App Name: {AGENT_APP_NAME}")
logger.info(f"Agent Run Path: {AGENT_RUN_PATH}")
logger.info(f"Using customer ID: CUST-80CA281C")
logger.info("=================================================")

def process_agent_interaction():
    """Process the user's message and get response from the agent."""
    # Only process if the last message is from the user and not currently processing
    if (
        st.session_state.messages[-1]["role"] != "user" 
        or st.session_state.processing_message
    ):
        return
    
    logger.info("----- PROCESSING NEW USER MESSAGE -----")
    logger.info(f"Session ID: {st.session_state.get('session_id', 'not set')}")
    logger.info(f"Message: {st.session_state.messages[-1]['content']}")
        
    st.session_state.processing_message = True  # Set flag
    user_prompt = st.session_state.messages[-1]["content"]
    assistant_response_text = None
    cart_needs_refresh = False
    is_system_message = user_prompt.startswith("SYSTEM_")

    # Determine if this interaction likely modified the cart or is a request to view it
    cart_needs_refresh = is_cart_related_query(user_prompt) or is_system_message

    try:
        session_id = st.session_state.session_id
        user_id = "streamlit_user"
        headers = {"Content-Type": "application/json"}
        # Add Auth header if needed: headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

        # --- Step 1: Ensure Session Exists (ONLY ONCE per Streamlit session) ---
        ensure_agent_session(session_id, user_id, headers)

        # --- Step 2: Run the Agent with the Prompt ---
        run_url = f"{AGENT_BASE_URL}{AGENT_RUN_PATH}"
        effective_prompt = format_effective_prompt(user_prompt)

        run_payload = {
            "app_name": AGENT_APP_NAME,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {"role": "user", "parts": [{"text": effective_prompt}]},
            "streaming": False,
        }

        logger.info(f"Attempting run POST to: {run_url}")
        
        # Add debug info for the request
        with st.sidebar:
            with st.expander("Agent Request", expanded=False):
                st.write("**Request Details**")
                st.code(f"URL: {run_url}\nPayload: {json.dumps(run_payload, indent=2)}")
        
        with st.spinner("Thinking..."):
            response = call_agent_api(run_url, run_payload, headers, timeout=45)
            # Store raw response for debugging
            st.session_state.last_raw_response = response.text[:10000]  # Limit size
            
            # Add debug info for the response
            with st.sidebar:
                with st.expander("Agent Response", expanded=False):
                    st.write("**Response Details**")
                    st.code(f"Status: {response.status_code}\nContent Type: {response.headers.get('Content-Type', 'Not specified')}\nBody Sample: {response.text[:500]}")
            
            logger.info(f"Received response with status: {response.status_code}, content-type: {response.headers.get('Content-Type', 'Not specified')}")
            assistant_response_text, tool_outputs, order_confirmed = parse_sse_response(response.text)
            
            # Store and display tool outputs for debugging
            if tool_outputs:
                if 'tool_outputs' not in st.session_state:
                    st.session_state.tool_outputs = {}
                for tool_name, output in tool_outputs.items():
                    st.session_state.tool_outputs[tool_name] = output
                
                # Add tool outputs to debug UI
                with st.sidebar:
                    with st.expander("Tool Outputs", expanded=False):
                        st.write("**Tools Used:**")
                        for tool_name, output in tool_outputs.items():
                            st.write(f"**{tool_name}:**")
                            st.code(json.dumps(output, indent=2)[:500])
                    
            # Handle order confirmation
            if order_confirmed:
                st.session_state.order_confirmed = True
                
                # Clear the cart after successful order submission
                if 'order_submission_state' in st.session_state and st.session_state.order_submission_state == 'confirmed':
                    # We'll keep the cart data for the order summary, but mark it as submitted
                    st.session_state.order_submitted = True
                    
                    # Reset the order submission state
                    st.session_state.order_submission_state = None

            # --- Step 3: Explicitly Refresh Cart if Needed ---
            # Check if the access_cart_information tool was called AND returned data
            if "access_cart_information" in tool_outputs:
                handle_cart_information(tool_outputs)
                cart_needs_refresh = False
            # Or, if the response suggests a change but the tool didn't run/return cart
            elif cart_needs_refresh and not is_system_message:
                explicitly_fetch_cart(run_url, user_id, session_id, headers)

            # Handle case where no text response was found
            if assistant_response_text is None:
                if is_system_message:  # Don't show system messages to user
                    assistant_response_text = None  # Suppress output
                else:
                    logger.warning("No text content message found in the response.")
                    assistant_response_text = (
                        "I processed your request, but didn't generate a text response."
                    )

    # --- Error Handling (Consolidated) ---
    except Exception as e:
        logger.error("An error occurred during agent interaction", exc_info=True)
        error_message = str(e)
        assistant_response_text = "Sorry, an error occurred while processing your request."
        
        # Show error details in the UI
        with st.sidebar:
            with st.expander("Error Details", expanded=True):
                st.error(f"**Agent Interaction Error:**\n{error_message}")
                if hasattr(e, 'response') and e.response is not None:
                    st.code(f"Status: {e.response.status_code}\nResponse: {e.response.text[:500]}")
    finally:
        st.session_state.processing_message = False  # Release flag

    # --- Finalize Interaction ---
    # Add assistant response to history if one exists and it wasn't a system message
    if assistant_response_text and not is_system_message:
        # Log the response text before adding to messages to check formatting
        logger.info("==== RESPONSE TO BE ADDED TO MESSAGES ====")
        logger.info(f"RAW Response content: {assistant_response_text}")
        logger.info("============================================")
        
        # Add debug UI in sidebar
        with st.sidebar:
            with st.expander("Raw Agent Response", expanded=True):
                st.write("**Raw response from agent (will be added to messages):**")
                st.code(assistant_response_text)
                st.write("**Preview how it should render:**")
                st.markdown(assistant_response_text, unsafe_allow_html=True)
        
        # Add to message history
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response_text}
        )
        
        # Debug the current state of messages
        logger.info(f"Updated messages. Count: {len(st.session_state.messages)}")
        for i, msg in enumerate(st.session_state.messages):
            logger.info(f"Message {i}: role={msg['role']}, content_start={msg['content'][:50]}...")
        
        st.rerun()  # Rerun to display the new assistant message and potentially updated cart


def ensure_agent_session(session_id, user_id, headers):
    """Ensure an agent session exists for the user."""
    if not st.session_state.get("session_initialized", False):
        logger.info(f"Initializing session {session_id} for user {user_id}")
        try:
            session_path = AGENT_SESSION_PATH_TEMPLATE.format(
                app_name=AGENT_APP_NAME, user_id=user_id, session_id=session_id
            )
            session_url = f"{AGENT_BASE_URL}{session_path}"
            logger.info(f"Session URL: {session_url}")
            session_payload = {"state": {}}
            
            # Add debugging info directly to UI
            with st.sidebar:
                with st.expander("Debug Info", expanded=False):
                    st.write("**Session Initialization**")
                    st.code(f"URL: {session_url}\nPayload: {json.dumps(session_payload, indent=2)}")
            
            session_response = call_agent_api(
                session_url, session_payload, headers, timeout=15
            )
            st.session_state.session_initialized = True
            logger.info(f"Session {session_id} initialized successfully.")
            
            # Update debug info with success
            with st.sidebar:
                with st.expander("Debug Info", expanded=False):
                    st.write("**Session Response**")
                    st.code(f"Status: {session_response.status_code}\nBody: {session_response.text[:500]}")
        
        except Exception as e:
            logger.error(f"Failed to initialize session: {str(e)}")
            
            # Update debug info with error
            with st.sidebar:
                with st.expander("Debug Info", expanded=False):
                    st.write("**Session Error**")
                    st.error(f"Failed to initialize session: {str(e)}")
            
            # Continue without failing - we'll try again later
            st.session_state.session_initialized = False


def format_effective_prompt(user_prompt):
    """Format the prompt for specific system actions."""
    # Use a specific prompt for system messages like refresh
    effective_prompt = user_prompt
    if user_prompt == "SYSTEM_FETCH_CART":
        effective_prompt = "Use the access_cart_information tool to show what's in my cart."
    elif user_prompt == "SYSTEM_FETCH_CART_INTERNAL":
        effective_prompt = "Run access_cart_information and return the current contents of my shopping cart."
    return effective_prompt


def handle_cart_information(tool_outputs):
    """Handle cart information from the agent response."""
    logger.info(f"Found access_cart_information in tool_outputs: {tool_outputs['access_cart_information']}")
    update_success = update_cart_display(tool_outputs["access_cart_information"])
    if update_success:
        logger.info("Cart display updated successfully")
    else:
        logger.warning("Failed to update cart display from tool output")


def explicitly_fetch_cart(run_url, user_id, session_id, headers):
    """Explicitly fetch cart information from the agent."""
    logger.info("Response suggests cart change, explicitly fetching cart.")
    fetch_cart_payload = {
        "app_name": AGENT_APP_NAME,
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": "SYSTEM_FETCH_CART_INTERNAL"}],
        },  # Internal trigger
        "streaming": False,
    }
    try:
        # Use a shorter timeout for this potentially quick call
        fetch_response = call_agent_api(
            run_url, fetch_cart_payload, headers, timeout=20
        )
        _, fetch_tool_outputs, _ = parse_sse_response(fetch_response.text)
        if "access_cart_information" in fetch_tool_outputs:
            logger.info(f"Explicit cart fetch received: {fetch_tool_outputs['access_cart_information']}")
            update_success = update_cart_display(
                fetch_tool_outputs["access_cart_information"]
            )
            if update_success:
                logger.info("Cart display updated successfully from explicit fetch")
            else:
                logger.warning("Failed to update cart display from explicit fetch")
        else:
            logger.warning(
                "Explicit cart fetch did not return expected tool output. Available keys: " + 
                str(list(fetch_tool_outputs.keys()))
            )
    except Exception as fetch_err:
        logger.error(f"Failed to explicitly fetch cart: {fetch_err}")
        # Don't overwrite the main assistant response if fetch fails