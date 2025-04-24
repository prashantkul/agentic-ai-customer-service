"""
Agent interaction component for the Streamlit app.
"""

import logging
import json
import streamlit as st

from streamlit_components.utils import call_agent_api, parse_sse_response, update_cart_display
from streamlit_components.config import (
    AGENT_BASE_URL, 
    AGENT_RUN_PATH, 
    AGENT_SESSION_PATH_TEMPLATE, 
    AGENT_APP_NAME
)
from streamlit_components.chat import is_cart_related_query

logger = logging.getLogger(__name__)

def process_agent_interaction():
    """Process the user's message and get response from the agent."""
    # Only process if the last message is from the user and not currently processing
    if (
        st.session_state.messages[-1]["role"] != "user" 
        or st.session_state.processing_message
    ):
        return
        
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
        with st.spinner("Thinking..."):
            response = call_agent_api(run_url, run_payload, headers, timeout=45)
            # Store raw response for debugging
            st.session_state.last_raw_response = response.text[:10000]  # Limit size
            assistant_response_text, tool_outputs, order_confirmed = parse_sse_response(response.text)
            
            # Store tool outputs for debugging
            if tool_outputs:
                if 'tool_outputs' not in st.session_state:
                    st.session_state.tool_outputs = {}
                for tool_name, output in tool_outputs.items():
                    st.session_state.tool_outputs[tool_name] = output
                    
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
        assistant_response_text = "Sorry, an error occurred while processing your request."
    finally:
        st.session_state.processing_message = False  # Release flag

    # --- Finalize Interaction ---
    # Add assistant response to history if one exists and it wasn't a system message
    if assistant_response_text and not is_system_message:
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response_text}
        )
        st.rerun()  # Rerun to display the new assistant message and potentially updated cart


def ensure_agent_session(session_id, user_id, headers):
    """Ensure an agent session exists for the user."""
    if not st.session_state.get("session_initialized", False):
        logger.info(f"Initializing session {session_id} for user {user_id}")
        session_path = AGENT_SESSION_PATH_TEMPLATE.format(
            app_name=AGENT_APP_NAME, user_id=user_id, session_id=session_id
        )
        session_url = f"{AGENT_BASE_URL}{session_path}"
        session_payload = {"state": {}}
        session_response = call_agent_api(
            session_url, session_payload, headers, timeout=15
        )
        st.session_state.session_initialized = True
        logger.info(f"Session {session_id} initialized successfully.")


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